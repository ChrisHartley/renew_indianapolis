from django.db import models
from django.contrib.auth.models import User
from property_inventory.models import Property


class propertyInquiry(models.Model):


    user = models.ForeignKey(User)
    Property = models.ForeignKey(Property, blank=True, null=True)
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Time/Date")
    showing_scheduled = models.DateTimeField(blank=True, null=True)
    applicant_ip_address = models.GenericIPAddressField(blank=True, null=True)

    SOLD_STATUS = 1
    USER_CANCELLED_STATUS = 2
    USER_NON_RESPONSIVE_STATUS = 3
    USER_CONTACTED_STATUS = 4
    SCHEDULED_STATUS = 5
    COMPLETED_STATUS = 6
    DUPLICATE_REQUEST_STATUS = 7
    STATUS_CHOICES = (
        (SOLD_STATUS,'Property was sold after request submitted'),
        (USER_CANCELLED_STATUS,'User cancelled request'),
        (USER_NON_RESPONSIVE_STATUS,'User was unresponsive'),
        (USER_CONTACTED_STATUS,'Contacted user to schedule'),
        (SCHEDULED_STATUS,'Showing scheduled'),
        (COMPLETED_STATUS,'Showing completed'),
        (DUPLICATE_REQUEST_STATUS, 'Duplicate request')
    )

    status = models.IntegerField(blank=True, null=True, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "property inquiries"

    def __unicode__(self):
        return u'%s - %s' % (self.Property, self.user.email)

class PropertyInquirySummary(propertyInquiry):
    class Meta:
        proxy = True
        verbose_name = 'Property Inquiry Summary'
        verbose_name_plural = 'Property Inquiry Summaries'
