from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from property_inventory.models import Property
from datetime import datetime, timedelta
from time import sleep
from django.utils.timezone import localtime
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone # timezone aware now()
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client import file, client, tools
import logging
from operator import itemgetter, attrgetter
from itertools import groupby
from applicants.models import ApplicantProfile
from django.core.urlresolvers import reverse

class propertyInquiry(models.Model):
    user = models.ForeignKey(User)
    Property = models.ForeignKey(Property, blank=True, null=True)
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Time/Date")
    showing_scheduled = models.DateTimeField(blank=True, null=True)
    applicant_ip_address = models.GenericIPAddressField(blank=True, null=True)

    NULL_STATUS = None
    SOLD_STATUS = 1
    USER_CANCELLED_STATUS = 2
    USER_NON_RESPONSIVE_STATUS = 3
    USER_CONTACTED_STATUS = 4
    SCHEDULED_STATUS = 5
    COMPLETED_STATUS = 6
    DUPLICATE_REQUEST_STATUS = 7
    USER_DID_NOT_SHOW = 8
    REQUESTED_ANOTHER_INVITATION = 9

    STATUS_CHOICES = (
        (NULL_STATUS, 'Initial status'),
        (SOLD_STATUS,'Property was sold/pending after request submitted'),
        (USER_CANCELLED_STATUS,'User cancelled request'),
        (USER_NON_RESPONSIVE_STATUS,'User was unresponsive'),
        (USER_CONTACTED_STATUS,'Contacted user to schedule'),
        (SCHEDULED_STATUS,'Showing scheduled'),
        (COMPLETED_STATUS,'Showing completed'),
        (DUPLICATE_REQUEST_STATUS, 'Duplicate request'),
        (USER_DID_NOT_SHOW, 'User did not appear at appointment'),
        (REQUESTED_ANOTHER_INVITATION, 'User would like to be invited to subsequent showing'),
     )

    status = models.IntegerField(blank=True, null=True, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "property inquiries"

    def __unicode__(self):
        return u'{0} - {1} {2} ({3}) - {4} - {5}'.format(self.Property, self.user.first_name, self.user.last_name, self.user.email, self.timestamp.strftime('%x'), self.get_status_display())

def save_location(instance, filename):
    return "property_showing/{0}/{1}/{2}".format(instance.Property, instance.datetime.strftime('%Y-%m-%d'), filename)

def save_calendar_events(showing):
    url = 'https://build.renewindianapolis.org/{}?parcel={}&rsvpId={}'.format(reverse('submit_property_inquiry'), showing.Property.parcel, showing.id)
    for calendar in settings.PROPERTY_SHOWING_CALENDARS:
        e = {
            'summary': '{} - Property Showing'.format(showing.Property.streetAddress,).title(),
            'location': '{0}, Indianapolis, IN'.format(showing.Property.streetAddress,),
            'description': 'If no one RSVPs to this showing it may be cancelled - <a href="{}">RSVP here</a> if you plan on attending.'.format(url,),
            'start': {
                'dateTime': showing.datetime.isoformat(),
                'timeZone': '',
            },
            'end': {
                'dateTime': (showing.datetime+timedelta(minutes=30)).isoformat(),
                'timeZone': '',
            }

        }
        if calendar['sharing'] == 'private':
            data = sorted(showing.inquiries.all(), key=attrgetter('user'))
            users = []
            people = []
            for k,g in groupby(data, attrgetter('user')):
                users.append(k)
            for u in users:
                try:
                    people.append(u'{} {} - {} {}'.format(u.first_name, u.last_name, u.email, u.profile.phone_number))
                except ApplicantProfile.DoesNotExist:
                    people.append(u'{} {} - {}'.format(u.first_name, u.last_name, u.email))
            #for inq in self.inquiries.all():

            e['description'] = render_to_string('property_inquiry/property_showing_ics_description.txt', {'showing': showing, 'properties': Property.objects.filter(pk=showing.Property.pk), 'users': people})
        SCOPES = 'https://www.googleapis.com/auth/calendar'
        store = file.Storage(settings.GOOGLE_API_TOKEN_LOCATION)
        creds = store.get()
        logger = logging.getLogger(__name__)

        if not creds or creds.invalid:
            logger.error('Error with Google API token.json - creds not found or invalid')
            return
        for i in range(5):
            try:
                service = build('calendar', 'v3', http=creds.authorize(Http()), cache_discovery=False)
                if calendar['sharing'] == 'public':
                    if showing.google_public_calendar_event_id is not None:
                        e = service.events().update(calendarId=calendar['id'], eventId=showing.google_public_calendar_event_id, body=e).execute()
                    else:
                        e = service.events().insert(calendarId=calendar['id'], body=e).execute()
                if calendar['sharing'] == 'private':
                    if showing.google_private_calendar_event_id is not None:
                        e = service.events().update(calendarId=calendar['id'], eventId=showing.google_private_calendar_event_id, body=e).execute()
                    else:
                        e = service.events().insert(calendarId=calendar['id'], body=e).execute()

            except HttpError as e:
                sleep(2)
                logger.warning('HttpError calling Google Calendar API')
                continue
            except TypeError as e:
                sleep(2)
                logger.warning('TypeError calling Google Calendar API, most likely event not found resulting in JSON not serializable.')
                continue
            else:
                if calendar['sharing'] == 'public':
                    showing.google_public_calendar_event_id = e.get('id')
                if calendar['sharing'] == 'private':
                    showing.google_private_calendar_event_id = e.get('id')
                break
    showing.save()

class propertyShowing(models.Model):
    Property = models.ForeignKey(Property, blank=False, null=False)
    datetime = models.DateTimeField(verbose_name="Time/Date")
    notes = models.CharField(blank=True, max_length=1024)
    inquiries = models.ManyToManyField(
        propertyInquiry,
        blank=True,
        related_name='showings',
    )
    signin_sheet = models.FileField(
        upload_to=save_location,
        max_length=512,
        blank=True,
    )

    google_public_calendar_event_id = models.CharField(blank=True, null=True, max_length=1024, help_text='Google Public Calendar Event ID, if created')
    google_private_calendar_event_id = models.CharField(blank=True, null=True, max_length=1024, help_text='Google Private Calendar Event ID, if created')


    class Meta:
        verbose_name_plural = "property showings"
        ordering = ['-datetime']

    def save(self, *args, **kwargs):
        try:
            orig = propertyShowing.objects.get(pk=self.pk)
            super(propertyShowing, self).save(*args, **kwargs)

        except propertyShowing.DoesNotExist:
            super(propertyShowing, self).save(*args, **kwargs)
            orig = None
        finally:
            if orig == None or (
                self.google_public_calendar_event_id == None or
                self.google_private_calendar_event_id == None or
                orig.google_public_calendar_event_id != self.google_public_calendar_event_id or
                orig.google_private_calendar_event_id != self.google_private_calendar_event_id or
                orig.Property != self.Property or
                orig.datetime != self.datetime or
                orig.inquiries != self.inquiries
                ): # if things have changed, need to re-update
                save_calendar_events(self)

    def delete(self):
        if self.google_public_calendar_event_id is not None or self.google_private_calendar_event_id is not None:
            for calendar in settings.PROPERTY_SHOWING_CALENDARS:

                SCOPES = 'https://www.googleapis.com/auth/calendar'
                store = file.Storage(settings.GOOGLE_API_TOKEN_LOCATION)
                creds = store.get()
                logger = logging.getLogger(__name__)

                if not creds or creds.invalid:
                    logger.error('Error with Google API token.json - creds not found or invalid')
                    return
                for i in range(5):
                    try:
                        service = build('calendar', 'v3', http=creds.authorize(Http()), cache_discovery=False)
                        if calendar['sharing'] == 'public':
                            if self.google_public_calendar_event_id is not None:
                                e = service.events().delete(calendarId=calendar['id'], eventId=self.google_public_calendar_event_id).execute()
                        if calendar['sharing'] == 'private':
                            if self.google_private_calendar_event_id is not None:
                                e = service.events().delete(calendarId=calendar['id'], eventId=self.google_private_calendar_event_id).execute()
                    except HttpError as e:
                        sleep(2)
                        logger.warning('HttpError calling Google Calendar API')
                        continue
                    else:
                        break
        super(propertyShowing, self).delete()


    def __unicode__(self):
        return u'{0} - {1}'.format(self.Property, datetime.strftime(localtime(self.datetime), '%x, %-I:%M%p') )

class PropertyInquirySummary(propertyInquiry):
    class Meta:
        proxy = True
        verbose_name = 'Property Inquiry Summary'
        verbose_name_plural = 'Property Inquiry Summaries'

class PropertyInquiryMapProxy(propertyInquiry):
   class Meta:
       proxy = True
       verbose_name = 'Property Inquiry Map'
       verbose_name_plural = 'Property Inquiries Map'
