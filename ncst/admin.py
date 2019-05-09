# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from django.contrib import admin as regular_admin
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from utils.admin import ExportCsvMixin

from .models import Contact, Property, Program
from photos.models import photo

class photoInlineAdmin(regular_admin.TabularInline):
    model = photo
    fields = ('prop_ncst', 'image', 'file_download')
    extra = 1
    readonly_fields = ('file_download',)
    def file_download(self, obj):
        if obj.id is None:
            return '-'
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("send_class_file", kwargs={'app_name': 'photos', 'class_name': 'photo', 'pk':obj.id, 'field_name':'image'}),
                "Download"
            ))


class PropertyAdmin(admin.OSMGeoAdmin, ExportCsvMixin):
    #readonly_fields = ('geometry',)
    search_fields = ('parcel', 'street_address', 'zipcode')
    list_display = ('parcel', 'street_address', 'status', 'lockbox', 'recommendation', 'price_offer')
    list_filter = ('status',)
    inlines = [ photoInlineAdmin, ]
admin.site.register(Contact)
admin.site.register(Program)
admin.site.register(Property, PropertyAdmin)
