# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from utils.admin import ExportCsvMixin

from .models import Contact, Property, Program

class PropertyAdmin(admin.OSMGeoAdmin, ExportCsvMixin):
    #readonly_fields = ('geometry',)
    search_fields = ('parcel', 'street_address', 'zipcode')
    list_display = ('parcel', 'street_address', 'status', 'lockbox', 'recommendation', 'price_offer')
    list_filter = ('status',)
admin.site.register(Contact)
admin.site.register(Program)
admin.site.register(Property, PropertyAdmin)
