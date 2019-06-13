# -*- coding: utf-8 -*-


from django.contrib.gis import admin
from django.contrib import admin as regular_admin
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from utils.admin import ExportCsvMixin

from .models import Contact, Property, Program, Seller
from photos.models import photo
from property_condition.models import ConditionReport

class photoInlineAdmin(regular_admin.TabularInline):
    model = photo
    fields = ('prop_ncst', 'image', 'image_tag')
    extra = 0
    readonly_fields = ('image_tag',)


class propertyConditionReportInlineAdmin(regular_admin.TabularInline):
    model = ConditionReport
    fields = ('quick_condition', 'secure', 'occupied', 'major_structural_issues', 'full_link')
    readonly_fields = ('full_link',)
    extra = 0

    def full_link(self, obj):
        if obj.id is None:
            return '-'
        return mark_safe('<a href="{}" target="_blank">{}</a>'.format(
            reverse("admin:property_condition_conditionreport_change", args=(obj.id,)),
                "Open Report"
            ))

class PropertyAdmin(admin.OSMGeoAdmin, ExportCsvMixin):
    search_fields = ('parcel', 'street_address', 'zipcode')
    list_display = ('parcel', 'street_address', 'status', 'lockbox', 'recommendation', 'price_offer', 'condition_report_completed')
    list_filter = ('status',)
    inlines = [ photoInlineAdmin,propertyConditionReportInlineAdmin]

    def condition_report_completed(self, obj):
        return ConditionReport.objects.filter(Property_ncst=obj).count()>0
    condition_report_completed.boolean = True

admin.site.register(Contact)
admin.site.register(Program)
admin.site.register(Seller)
admin.site.register(Property, PropertyAdmin)
