# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models
from localflavor.us.models import PhoneNumberField
from django.utils.encoding import python_2_unicode_compatible
from utils.utils import pull_property_info_from_arcgis

@python_2_unicode_compatible
class Contact(models.Model):
    name = models.CharField(max_length=254, blank=False)
    phone = PhoneNumberField()
    email = models.EmailField(blank=True, default='')
    notes = models.CharField(blank=True, max_length=1024)

    def __str__(self):
        return self.name

class Program(models.Model):
    name = models.CharField(max_length=254, blank=False)
    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Property(models.Model):
    NEW_STATUS = 1
    INSPECTING_STATUS = 2
    INSPECTING_COMPLETE_STATUS = 3
    WAITING_OFFER_STATUS =  4
    OFFER_STATUS = 5
    PENDING_OFFER_ACCEPT_STATUS = 6
    OFFER_ACCEPT_STATUS = 7
    DECLINED_STATUS = 8
    REMOVED_STATUS = 9
    SENT_TO_DOC_PREP = 10
    NSI_AWAITING_PA = 11
    NSI_CLOSING = 12
    NSI_CLOSED = 13


    STATUS_CHOICES = (
        (NEW_STATUS, 'NSI New'),
        (INSPECTING_STATUS,'NSI Inspecting'),
        (INSPECTING_COMPLETE_STATUS,'NSI Inspecting - Completed'),
        (WAITING_OFFER_STATUS,'NSI Awaiting Offer'),
        (OFFER_STATUS,'NSI Offer'),
        (PENDING_OFFER_ACCEPT_STATUS,'NSI Pending Offer Accept'),
        (OFFER_ACCEPT_STATUS,'NSI Offer Accepted'),
        (SENT_TO_DOC_PREP,'Sent to Doc Prep'),
        (NSI_AWAITING_PA,'NSI Awaiting PA'),
        (NSI_CLOSING,'NSI Closing'),
        (NSI_CLOSED,'NSI Closed'),
        (DECLINED_STATUS,'NSI Declined by Buyer'),
        (REMOVED_STATUS,'NSI Removed by Seller'),
    )

    geometry = models.MultiPolygonField(srid=4326, blank=True, null=True)
    street_address = models.CharField(blank=True, max_length=254)
    zipcode = models.CharField(blank=True, max_length=5)
    parcel = models.CharField(blank=False, max_length=7)

    update_from_server = models.BooleanField(default=True, help_text="Attempt to update street address, etc from remote server on next save.")

    program = models.ForeignKey(Program, null=False)
    contact = models.ForeignKey(Contact, null=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    status = models.IntegerField(choices=STATUS_CHOICES, null=False, default=NEW_STATUS)

    lockbox =  models.CharField(blank=True, max_length=30)

    notes = models.CharField(blank=True, max_length=1024)

    price_efmv = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_adjustment = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_offer = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    request_deadline = models.DateTimeField(blank=False)
    inspection_deadline = models.DateTimeField(blank=True, null=True)
    acquisition_deadline = models.DateTimeField(blank=True, null=True)

    recommendation = models.NullBooleanField(blank=True, help_text="Recommened by staff for acquisition?")

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return '{} - {} - {}'.format(self.street_address, self.parcel, self.get_status_display())


    def save(self, *args, **kwargs):
        if self.parcel is not None and self.parcel != '' and self.update_from_server == True:
            results = pull_property_info_from_arcgis(self.parcel)
            if results:
                self.street_address = results['street_address']
                self.zipcode = results['zipcode']
                self.geometry = results['geometry']
                self.update_from_server = False
        super(Property, self).save(*args, **kwargs)
