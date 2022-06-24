from django.core.management.base import BaseCommand, CommandError
from property_inquiry.models import propertyInquiry
from django.contrib.auth.models import User
from datetime import timedelta, datetime, date
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Q
from property_inventory.models import Property
from project_agreement_management.models import Enforcement, BreechType, BreechStatus

class Command(BaseCommand):
    help = 'Given a list of properties and breach type, create enforcements and breeches'


    def add_arguments(self, parser):
        parser.add_argument('parcels', nargs='+')
        parser.add_argument(
            '--comprehensive',
            action='store_true',
            dest='comprehensive',
            default=False,
            help='Close existing tax sale breeches if not listed - the given parcel list is assumed comprehensive',
        )
        parser.add_argument(
            '--breach-type',
            choices=BreechType.objects.all().values_list('name', flat=True),
            dest='breach_type',
            help='Specify type of breach',
        )


    def handle(self, *args, **options):
        props = Property.objects.filter(project_agreement_released=False).filter(status__startswith='Sold').filter(parcel__in=options['parcels'])

        breach_type = BreechType.objects.get(name=options['breach_type'])

        if options['comprehensive'] == True:
            all_enf = Enforcement.objects.exclude(Property__in=props)
            for e in all_enf:
            #    print(e.breech_types)
            #    print(dir(e))
                for b in e.breechstatus_set.all():
                    if b.breech == breach_type and b.date_resolved is None:
                        self.stdout.write('{} - Breach is open, should be closed'.format(e,))
                        b.date_resolved = timezone.now()
                        b.status = BreechStatus.CLOSED
                        b.save()

        for p in props:
            app = p.buyer_application
            if app is not None:
                enforcements = Enforcement.objects.filter(Property=p).filter(Application=app).order_by('created')
            else:
                enforcements = Enforcement.objects.filter(Q(Application__isnull=True) & Q(owner__exact=p.applicant))
            has_this_breech = False
            for e in enforcements:
                    for b in e.breech_types.all():
                        if b == breach_type:
                            has_this_breech = True
            if has_this_breech == False:
                enf = enforcements.last()
                if enf is None:
                    if app is not None:
                        enf = Enforcement(Property=p, Application=app)
                    else:
                        enf = Enforcement(Property=p, owner=p.applicant)
                    enf.save()
                bs = BreechStatus(breech=breach_type, enforcement=enf, date_created=date.today())
                bs.save()
                self.stdout.write(enf)
