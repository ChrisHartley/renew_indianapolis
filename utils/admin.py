# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
import csv
from django.contrib import admin

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
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"
