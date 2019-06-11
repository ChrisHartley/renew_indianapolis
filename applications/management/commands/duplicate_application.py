from django.core.management.base import BaseCommand, CommandError
from applications.models import Application, MeetingLink, Meeting
from property_inventory.models import Property
from user_files.models import UploadedFile
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Duplicate an application and change the property'

    def add_arguments(self, parser):
        parser.add_argument('--application_id', nargs=1, type=int, required=True)
        parser.add_argument('--parcels', nargs='+', type=int, required=True)


    def handle(self, *args, **options):
        parcels = options['parcels']
        template_app = Application.objects.get(id=options['application_id'][0])
        org_app =  Application.objects.get(id=options['application_id'][0])
        self.stdout.write('Duplicating {}'.format(org_app,))
        for parcel in parcels:
            self.stdout.write('Parcel {}'.format(parcel,))
            app = org_app
            prop = Property.objects.get(parcel=parcel)
            app.id = None
            app.Property = prop
            app.price_at_time_of_submission = prop.price
            app.save()
            mls = MeetingLink.objects.filter(application=template_app).order_by('meeting__meeting_date')
            for ml in mls:
                ml.application = app
                ml.id = None
                ml.save()
                self.stdout.write('MeetingLink {}'.format(ml,))
            files = UploadedFile.objects.filter(application=template_app)
            for f in files:
                f2 = UploadedFile(
                    user=f.user,
                    organization=f.organization,
                    application=app,
                    file_purpose=f.file_purpose,
                    send_with_neighborhood_notification=f.send_with_neighborhood_notification,

                )
                fname = f.supporting_document.name.split('/')[-1]
                f2.supporting_document.save(fname, ContentFile(f.supporting_document), save=True)
                self.stdout.write('File {}'.format(fname,))
