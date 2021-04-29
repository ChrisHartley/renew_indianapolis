from django.core.management.base import BaseCommand, CommandError
from property_inquiry.models import propertyInquiry
from django.contrib.auth.models import User
from datetime import timedelta, datetime, date
from django.utils import timezone

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Q
from property_inventory.models import Property
from annual_report_form.models import annual_report
from applications.models import Application
from project_agreement_management.models import Enforcement, BreechType, BreechStatus

class Command(BaseCommand):
    help = 'Check for properties that did not submit annual reports and create enforcements and breeches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            default=timezone.now().year,
            dest='year',
            type=int,
            help='The year the annual report was due, defaults to the current year'
        )



    def handle(self, *args, **options):
        props = Property.objects.filter(project_agreement_released=False).filter(status__startswith='Sold')

        # get sales in the named year after april 1
        exclude_ids = []
        for p in props:
            status = p.status
            sold_date_string = status[5:]
            sold_date = datetime.strptime(sold_date_string, '%m/%d/%Y')
            if sold_date >=  datetime(options['year'], 4, 1): # Exclude properties sold after April 1st of the given year, the report deadline
                exclude_ids.append(p.id)
        props = Property.objects.filter(project_agreement_released=False).filter(status__startswith='Sold').exclude(id__in=exclude_ids)

        reports = annual_report.objects.filter(created__year=options['year'])
        reports_property_list = reports.values_list('Property', flat=True).order_by('Property')
        annual_report_breech = BreechType.objects.get(name='Missing Annual Report')
        for p in props:
            app = p.buyer_application
            breech_required = False
            if p.id not in reports_property_list:
#                print("Property {} doesn't have an annual report on file for {}".format(p,options['year']))
                if app is not None:
                    if app.application_type not in[Application.HOMESTEAD, Application.STANDARD]:
#                        print("{} application, no annual report required".format(app.get_application_type_display(),) )
                        pass
                    else:
                    #    print("**Annual report required, not filed** {} {}".format(p,app))
                        breech_required = True
                else:
                    #print('No app linked to property: {}, buyer: {}'.format(p,p.applicant))
                    pass
            else:
#                print('SOMEONE DID THE RIGHT THING: {} {}'.format(p,p.applicant))
##              We need to now close any open annual report breaches for this year.
                for enf in Enforcement.objects.filter(Property=p).filter(Application=app).order_by('created'):
                    for breachstatus in enf.breechstatus_set.all():
                        if breachstatus.breech == annual_report_breech and breachstatus.status == False:
                            breachstatus.status = True # closed
                            breachstatus.date_resolved = timezone.now()
                            breachstatus.save()
                            print("Breach open, should be closed, {} {} {} closed.".format(breachstatus, p, app))

            if breech_required:
                enforcements = Enforcement.objects.filter(Property=p).filter(Application=app).order_by('created')
                enf = enforcements.last()
                duplicate_breech = False
                if enf is None:
                    if app is not None:
                        enf = Enforcement(Property=p, Application=app)
                    else:
                        enf = Enforcement(Property=p, owner=p.applicant)
                    enf.save()
                else:
                    for breachstatus in enf.breechstatus_set.all():
                        if breachstatus.breech == annual_report_breech and breachstatus.status == False:
                            duplicate_breech = True
                if duplicate_breech == False:
                    bs = BreechStatus(breech=annual_report_breech, enforcement=enf, date_created=date.today())
                    bs.save()
                    print("Breech created: {} {} {}".format(bs,p,app))
                else:
                #    print("Breech already open")
                    pass

            # sold_date = datetime.strptime(p.status[5:], "%m/%d/%Y").date()
            # if sold_date + self.deadline <= date.today():
            #     app = p.buyer_application
            #     if app is not None:
            #         if app.application_type not in[Application.HOMESTEAD, Application.STANDARD]:
            #             print('No timeline in PA. Property: {}, Application: {}, Application Type: {}'.format(p, app, app.application_type))
            #             continue
            #         enforcements = Enforcement.objects.filter(Property=p).filter(Application=app).order_by('created')
            #     else:
            #         enforcements = Enforcement.objects.filter(Q(Application__isnull=True) & Q(owner__exact=p.applicant))
            #     has_overdue = False
            #     for e in enforcements:
            #             for b in e.breech_types.all():
            #                 if b == overdue_breech:
            #                     has_overdue = True
            #     if has_overdue == False:
            #         print('Overdue breech created for {}'.format(p,))
            #         enf = enforcements.last()
            #         if enf is None:
            #             if app is not None:
            #                 enf = Enforcement(Property=p, Application=app)
            #             else:
            #                 enf = Enforcement(Property=p, owner=p.applicant)
            #             enf.save()
            #         bs = BreechStatus(breech=overdue_breech, enforcement=enf, date_created=date.today())
            #         bs.save()
