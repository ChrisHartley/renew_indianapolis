# -*- coding: utf-8 -*-


from django.contrib.gis.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class market_value_analysis(models.Model):
    classification = models.CharField(max_length=25)
    geoid = models.CharField(max_length=50)
    geometry = models.MultiPolygonField(srid=2965)

    def __str__(self):
        return '{}'.format(self.classification,)

@python_2_unicode_compatible
class parcel(models.Model):
    parcel_number = models.CharField(max_length=7)
    street_address = models.CharField(max_length=255)
    has_building = models.BooleanField()

    SURPLUS_TYPE = 1
    INVENTORY_TYPE = 2
    BEP_TYPE = 3
    TAX_SALE_UNSOLD = 4

    PROPERTY_TYPE_CHOICES = (
        (SURPLUS_TYPE, 'County Surplus'),
        (TAX_SALE_UNSOLD, 'Tax Sale Unsold'),
        (INVENTORY_TYPE, 'Renew Inventory'),
        (BEP_TYPE, 'BEP lot'),
    )
    property_type = models.IntegerField(choices=PROPERTY_TYPE_CHOICES)

    AVAILABLE = 1
    PENDING = 2
    SOLD = 3
    REQUESTED = 4

    STATUS_CHOICES = (
        (AVAILABLE, 'Available'),
        (PENDING, 'Pending'),
        (SOLD, 'Sold'),
        (REQUESTED, 'Requested'),

    )

    status = models.IntegerField(choices=STATUS_CHOICES)

    REUP_MORTGAGE = 'Re-up mortgage'
    EXPIRE_MORTGAGE = 'Let the mortgage expire'

    MORTGAGE_CHOICES = (
        (REUP_MORTGAGE,'Re-up mortgage, unlikely to sell'),
        (EXPIRE_MORTGAGE,'Let the mortgage expire, sale likely'),
    )

    mortgage_decision = models.CharField(choices=MORTGAGE_CHOICES, null=True, max_length=100)
    mva_category = models.CharField(max_length=2)

    bid_group = models.FloatField(null=False)
    notes = models.CharField(max_length=1024, blank=True)
    flagged = models.BooleanField(default=False)
    ilp_within_quarter_mile = models.IntegerField(null=True, blank=True)
    adjacent_homesteads_non_surplus = models.IntegerField(null=True, blank=True)



    geometry = models.MultiPolygonField(srid=2965)

    def __str__(self):
        return '{0} - {1}'.format(self.street_address, self.parcel_number,)
