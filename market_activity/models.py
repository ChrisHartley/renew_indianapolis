# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from property_inventory.models import census_tract

# Model saves census tract level analysis of sales disclosures
# for the past 12 months. Should be updated monthly.
class tract_sdf_summary(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    census_tract = models.ForeignKey(census_tract, related_name='sdf_summary')
    bottom_10_percent = models.DecimalField(max_digits=15, decimal_places=2)
    top_90_percent = models.DecimalField(max_digits=15, decimal_places=2)
    median = models.DecimalField(max_digits=15, decimal_places=2)
    average = models.DecimalField(max_digits=15, decimal_places=2)
    minimum = models.DecimalField(max_digits=15, decimal_places=2)
    maximum = models.DecimalField(max_digits=15, decimal_places=2)
    number_qualifying_sales = models.IntegerField()

    LOT = False
    IMPROVEMENTS = True

    IMPROV_CHOICES = (
        (LOT, 'Vacant lot'),
        (IMPROVEMENTS, 'Structure'),
    )

    with_improvements = models.BooleanField(choices=IMPROV_CHOICES)

    class Meta:
        verbose_name = 'Census Tract Sales Summary'
        verbose_name_plural = 'Census Tract Sales Summaries'

    def __str__(self):              # __unicode__ on Python 2
        return '{} - {} - {}'.format(self.census_tract, self.created, self.get_with_improvements_display())
