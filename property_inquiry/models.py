from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from property_inventory.models import Property
from datetime import datetime
from django.utils.timezone import localtime

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
        return u'{0} - {1} - {2} - {3}'.format(self.Property, self.user.email, self.timestamp.strftime('%x'), self.get_status_display())

def save_location(instance, filename):
    return "property_showing/{0}/{1}/{2}".format(instance.Property, instance.datetime.strftime('%Y-%m-%d'), filename)

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
        super(propertyShowing, self).save(*args, **kwargs)

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
