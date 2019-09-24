from django.core.management.base import BaseCommand, CommandError
from property_inquiry.models import propertyInquiry
from django.contrib.auth.models import User
from datetime import timedelta, datetime, date
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Q
from property_inventory.models import Property
from project_agreement_management.models import Enforcement, BreechType, BreechStatus

class Command(BaseCommand):
    help = 'Check for properties past the two year deadline and create enforcements and breeches'
    deadline = timedelta(days=(2*365))


    def handle(self, *args, **options):
        # need to fix this filter so it just pulls ones 4 days old
    #    users = User.objects.filter(Q(propertyinquiry__status__isnull=True) & Q(propertyinquiry__timestamp__date__gt=date(2018,4,1)) & Q(propertyinquiry__timestamp__date=date.today() - self.stale_period)).distinct()
        props = Property.objects.filter(project_agreement_released=False).filter(status__startswith='Sold')

        overdue_breech = BreechType.objects.get(name='Past two year deadline')

        for p in props:
            sold_date = datetime.strptime(p.status[5:], "%m/%d/%Y").date()
            if sold_date + self.deadline <= date.today():
                app = p.buyer_application
                if app is not None:
                    enforcements = Enforcement.objects.filter(Property=p).filter(Application=app).order_by('created')
                else:
                    enforcements = Enforcement.objects.filter(Q(Application__isnull=True) & Q(owner__exact=p.applicant))
                print(p, app, enforcements)
                has_overdue = False
                for e in enforcements:
                        for b in e.breech_types.all():
                            if b == overdue_breech:
                                has_overdue = True
                if has_overdue == False:
                    print('Overdue breech created for {}'.format(p,))
                    enf = enforcements.last()
                    if enf is None:
                        if app is not None:
                            enf = Enforcement(Property=p, Application=app)
                        else:
                            enf = Enforcement(Property=p, owner=p.applicant)
                        enf.save()
                    bs = BreechStatus(breech=overdue_breech, enforcement=enf, date_created=date.today())
                    bs.save()
