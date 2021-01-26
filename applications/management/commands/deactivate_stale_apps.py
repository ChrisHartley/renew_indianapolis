from django.core.management.base import BaseCommand, CommandError
from applications.models import Application, MeetingLink, Meeting
from property_inventory.models import Property
from user_files.models import UploadedFile
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Mark old applications as Inactive'

    def add_arguments(self, parser):
        parser.add_argument('--days', nargs=1, type=int, required=True)

    def handle(self, *args, **options):
        days = timedelta(days=options['days'][0])
        now = timezone.now()
        cutoff_date = now - days
        old_applications = Application.objects.filter(status__in=[Application.ACTIVE_STATUS, Application.INITIAL_STATUS]).filter(created__lte=cutoff_date)
        #self.stdout.write('Duplicating {}'.format(org_app,))
        for app in old_applications:
            self.stdout.write('.', ending='')
            app.status = Application.INACTIVE_STATUS
            app.save(update_fields=['status'])
