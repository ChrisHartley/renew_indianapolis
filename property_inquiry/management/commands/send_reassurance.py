from django.core.management.base import BaseCommand, CommandError
from property_inquiry.models import propertyInquiry
from django.contrib.auth.models import User
from datetime import timedelta, datetime, date
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Q

class Command(BaseCommand):
    help = 'Sends a re-assurance email to stale property inquiries'
    stale_period = timedelta(days=4)


    def handle(self, *args, **options):
        # need to fix this filter so it just pulls ones 4 days old
        users = User.objects.filter(Q(propertyinquiry__status__isnull=True) & Q(propertyinquiry__timestamp__date__gt=date(2018,4,1)) & Q(propertyinquiry__timestamp__date=date.today() - self.stale_period)).distinct()
        for u in users:
            context = {}
            context['user'] = u
            context['inquiry_list'] = propertyInquiry.objects.filter(user=u).filter(status__isnull=True).filter(timestamp__date__gt=date(2018,4,1))
            message_body = render_to_string('email/property_inquiry_reassurance.txt', context)
            message_subject = 'Property Inquiry Followup'
            self.stdout.write(message_body)
            send_mail(message_subject, message_body, 'info@renewindianapolis.org', [u.email,], fail_silently=False)
