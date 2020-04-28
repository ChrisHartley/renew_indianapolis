# -*- coding: utf-8 -*-

from django.http import HttpResponse
import csv
from django.contrib import admin

class PropertyTypeFilter(admin.SimpleListFilter):
    title = 'property type'
    parameter_name = 'property_type'

    def lookups(self, request, model_admin):
        return (
            ('in', 'Investment'),
            ('lb', 'Landbank'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in':
            return queryset.filter(propertyType__exact='in')
        if self.value() == 'lb':
            return queryset.filter(propertyType__exact='lb')
        return queryset

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        try:
            field_names.remove('geometry')
            field_names.remove('centroid_geometry')
        except ValueError:
            pass

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            print(obj)
        #    for field in field_names:
        #        print(getattr(obj, field))
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"
