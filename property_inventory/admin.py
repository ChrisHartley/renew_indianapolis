from django.contrib.gis import admin
from django.contrib import admin as regular_admin
from django.contrib.admin import SimpleListFilter

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.forms import Textarea
from django.urls import NoReverseMatch
from .models import Property, CDC, Neighborhood, ContextArea, price_change, note, featured_property, blc_listing, yard_sign, take_back, lockbox
from applications.models import Application
from photos.models import photo
from applications.admin import PriceChangeMeetingLinkInline
from property_inquiry.models import propertyInquiry
from property_condition.models import ConditionReport
import datetime
from django.utils.timezone import now
#import pytz

class PropertyStatusYearListFilter(SimpleListFilter):
    title = 'Property Status Year'
    parameter_name = 'status-year'

    def lookups(self, request, model_admin):
        return (
            ('2014','2014'),
            ('2015','2015'),
            ('2016','2016'),
            ('2017','2017'),
            ('2018','2018'),
            ('2019','2019'),
        )
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status__contains=self.value())
        return queryset

class PropertyStatusListFilter(SimpleListFilter):
    title = 'Property Status'
    parameter_name = 'status'
    def lookups(self, request, model_admin):
        return (
            ('available','Available'),
            ('sold', 'Sold'),
            ('approved', 'Received Final Approval'),
            ('consideration', 'Application under consideration'),
            ('bep', 'BEP demolition slatted'),
            ('newinventory', 'New Inventory'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'sold':
            return queryset.filter(status__contains='Sold')
        if self.value() == 'available':
            return queryset.filter(status__contains='Available')
        if self.value() == 'approved':
            return queryset.filter( ( Q(status__contains='Sale approved by MDC') & Q(renew_owned__exact=False) ) | (Q(status__contains='Sale approved by Board of Directors') & Q(renew_owned__exact=True)) )
        if self.value() == 'consideration':
            return queryset.filter( Q(status__contains='Sale approved by Review Committee') | (Q(status__contains='Sale approved by Board of Directors') & Q(renew_owned__exact=False)))
        if self.value() == 'bep':
            return queryset.filter(status__contains='BEP demolition slated')
        if self.value() == 'newinventory':
            return queryset.filter(status__contains='New Inventory')
        return queryset

class NoteInlineAdmin(regular_admin.TabularInline):
    model = featured_property
    fields = ('Property', 'start_date', 'end_date', 'note')
    #readonly_fields=('created','modified',  'Property')
    extra = 0

class lockboxInlineAdmin(regular_admin.TabularInline):
    model = lockbox
    fields = ('Property', 'code', 'note')
    extra = 0

class FeaturedPropertyInlineAdmin(regular_admin.TabularInline):
    model = note
    fields = ('text', 'created', 'modified', 'Property')
    readonly_fields=('created','modified',  'Property')
    extra = 0


class PropertyAdmin(admin.OSMGeoAdmin):
    search_fields = ('parcel', 'streetAddress', 'zipcode__name')
    list_display = ('parcel', 'streetAddress', 'structureType', 'price', 'status')
    list_filter = (PropertyStatusListFilter,'structureType', PropertyStatusYearListFilter, 'renew_owned', 'is_active', 'hhf_demolition')
    inlines = [ NoteInlineAdmin, FeaturedPropertyInlineAdmin, lockboxInlineAdmin]
    raw_id_fields = ('buyer_application',) # we need to be able to set to null if the app withdraws but don't want to incur overhead of select field.
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    modifiable = False
    readonly_fields = ('applications_search','view_photos','context_area_strategy','context_area_name', 'number_of_inquiries', 'main_photo', 'application_summary', 'condition_report_link')

    def main_photo(self, obj):
        ph = photo.objects.filter(prop=obj).filter(main_photo__exact=True).first()
        return ph.image_tag(300, 300)

    def context_area_strategy(self, obj):
        return ContextArea.objects.filter(geometry__contains=obj.geometry).first().disposition_strategy

    def context_area_name(self, obj):
        return ContextArea.objects.filter(geometry__contains=obj.geometry).first()

    def applications_search(self, obj):
        summary_link = '<a href="{}">{}</a>'.format(
            reverse("admin:app_list", args=('applications',))+'application/?q={}'.format(obj.parcel,), "View Applications")
        return mark_safe(summary_link)

    def application_summary(self, obj):
        apps = []
        for app in obj.application_set.exclude(status=Application.INITIAL_STATUS):
            apps.append('<a href="{0}">{1} {2} ({3}) ({4}), {5}</a>'.format(
                reverse("admin:applications_application_change", args=(app.id,)),
                app.user.first_name, app.user.last_name,
                app.organization, app.get_status_display(),
                app.created.strftime('%Y-%m-%d') ))
        app_links = '<li>'.join(apps)
        app_links = '<li>' + app_links
        return mark_safe('<ul>{0}</ul>'.format(app_links,))

    def number_of_inquiries(self, obj):
        inquiries = {}
        for duration in (30,60,90,180):
            end_day = now().date()
            start_day = end_day - datetime.timedelta(duration)
            #print(pytz.utc.localize(start_day))
            #print(start_day)
            inquiries['previous {0} days'.format(duration,)] = propertyInquiry.objects.filter(Property=obj).filter(timestamp__range=(start_day, end_day)).count()
        inquiries['all time'] = propertyInquiry.objects.filter(Property=obj).count()
        return inquiries

    def view_photos(self, obj):
        photo_page_link = '<a href="{}">{}</a>'.format(
                    reverse("property_photos", kwargs={'parcel': obj.parcel}), "View Photos")
        return mark_safe(photo_page_link)

    def condition_report_link(self, obj):
        count = ConditionReport.objects.filter(Property__exact=obj).count()
        summary_link = '<a href="{}">reports - {}</a>'.format(
            reverse("admin:app_list", args=('property_condition',))+'conditionreport/?q={}'.format(obj.parcel,), count)
        return mark_safe(summary_link)



class ContextAreaAdmin(admin.OSMGeoAdmin):
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    modifiable = False


class price_changeAdmin(admin.OSMGeoAdmin):
    search_fields = ('Property__streetAddress','Property__parcel')
    list_display = ('datestamp','Property', 'get_current_price', 'proposed_price', 'get_latest_approval_status')
    readonly_fields = ('approved', 'get_current_price','applications_search', 'get_current_property_status', 'summary_view')
    inlines = [ PriceChangeMeetingLinkInline ]


    def summary_view(self, obj):
        try:
            link = reverse("price_change_summary_view", args=(obj.pk,))
        except NoReverseMatch:
            link = ''
        summary_link = '<a href="{}">{}</a>'.format(
            link,'View Summary Page')
        return mark_safe(summary_link)

    def applications_search(self, obj):
        summary_link = '<a href="{}">{}</a>'.format(
            reverse("admin:app_list", args=('applications',))+'application/?q={}'.format(obj.Property.parcel,), "View Applications")
        return mark_safe(summary_link)

    def get_current_price(self, obj):
        return obj.Property.price

    def get_current_property_status(self, obj):
        return obj.Property.status

    def get_latest_approval_status(self, obj):
        if obj.meeting.first():
            return "{0}".format(obj.meeting.first())
        else:
            return '-'

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(price_changeAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'notes':
            formfield.widget = Textarea(attrs=formfield.widget.attrs)
        return formfield

class blc_listingAdmin(admin.OSMGeoAdmin):
    search_fields = ('Property__streetAddress','Property__parcel', 'blc_id')
    list_display = ('Property', 'get_property_status', 'blc_id', 'active', 'date_time')
    readonly_fields = ['get_property_status',]
    def get_property_status(self, obj):
        if obj.Property:
            return '{}'.format(obj.Property.status,)
        return '-'

class yard_signAdmin(admin.OSMGeoAdmin):
    search_fields = ('Property__streetAddress','Property__parcel', 'note')

class take_backAdmin(admin.OSMGeoAdmin):
    raw_id_fields = ('application',)

class lockboxAdmin(admin.OSMGeoAdmin):
    search_fields = ('Property__streetAddress','Property__parcel',)


class PropertyMapAdmin(PropertyAdmin):
    change_list_template = 'admin/property_inventory/change_list_map.html'
    def changelist_view(self, request, extra_context=None):
            extra_context = extra_context or {}
            #response.context_data['cl'].queryset
            #extra_context['popup_link'] = """<a target="_blank" href="/admin/property_inquiry/propertyshowing/add/?Property='+details['id']+'">Create a property showing.</a>"""
            return super(PropertyMapAdmin, self).changelist_view(
                request, extra_context=extra_context
            )


admin.site.register(price_change, price_changeAdmin)
#admin.site.register(Property, PropertyAdmin)
admin.site.register(CDC)
admin.site.register(Neighborhood)
admin.site.register(take_back, take_backAdmin)
admin.site.register(ContextArea, ContextAreaAdmin)
admin.site.register(featured_property)
admin.site.register(blc_listing, blc_listingAdmin)
admin.site.register(yard_sign, yard_signAdmin)
admin.site.register(lockbox, lockboxAdmin)
admin.site.register(Property, PropertyMapAdmin)
