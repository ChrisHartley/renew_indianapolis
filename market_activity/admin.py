# -*- coding: utf-8 -*-


from django.contrib import admin

from .models import tract_sdf_summary
class tract_sdf_summaryAdmin(admin.ModelAdmin):
    search_fields = ('census_tract__name',)
    list_display = ('census_tract', 'created', 'with_improvements', 'average')
admin.site.register(tract_sdf_summary, tract_sdf_summaryAdmin)
