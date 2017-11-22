from django.contrib.gis import admin
from django.contrib import admin as regular_admin
from django.contrib.admin import SimpleListFilter

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.forms import Textarea
from django.urls import NoReverseMatch
from .models import Property, CDC, Neighborhood, ContextArea, price_change, note, featured_property, blc_listing
from applications.admin import PriceChangeMeetingLinkInline
from property_inquiry.models import propertyInquiry
import datetime

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
            ('consideration', 'Application under consideration')
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
        return queryset

class NoteInlineAdmin(regular_admin.TabularInline):
    model = featured_property
    fields = ('Property', 'start_date', 'end_date', 'note')
    #readonly_fields=('created','modified',  'Property')
    extra = 0

class FeaturedPropertyInlineAdmin(regular_admin.TabularInline):
    model = note
    fields = ('text', 'created', 'modified', 'Property')
    readonly_fields=('created','modified',  'Property')
    extra = 0


class PropertyAdmin(admin.OSMGeoAdmin):
    search_fields = ('parcel', 'streetAddress', 'zipcode__name')
    list_display = ('parcel', 'streetAddress', 'structureType','status')
    list_filter = (PropertyStatusListFilter,'structureType', PropertyStatusYearListFilter, 'renew_owned' )
    inlines = [ NoteInlineAdmin, FeaturedPropertyInlineAdmin]

    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    modifiable = False
    readonly_fields = ('applications_search','view_photos','context_area_strategy','context_area_name', 'number_of_inquiries')

    def context_area_strategy(self, obj):
        return ContextArea.objects.filter(geometry__contains=obj.geometry).first().disposition_strategy

    def context_area_name(self, obj):
        return ContextArea.objects.filter(geometry__contains=obj.geometry).first()

    def applications_search(self, obj):
        summary_link = '<a href="{}">{}</a>'.format(
            reverse("admin:app_list", args=('applications',))+'application/?q={}'.format(obj.parcel,), "View Applications")
        return mark_safe(summary_link)

    def number_of_inquiries(self, obj):
        inquiries = {}
        for duration in (30,60,90,180):
            end_day = datetime.date.today()
            start_day = end_day - datetime.timedelta(duration)
            inquiries['previous {0} days'.format(duration,)] = propertyInquiry.objects.filter(Property=obj).filter(timestamp__range=(start_day, end_day)).count()
        inquiries['all time'] = propertyInquiry.objects.filter(Property=obj).count()
        return inquiries
        #return propertyInquiry.objects.filter(Property__exact=obj).count()

    def view_photos(self, obj):
        photo_page_link = '<a href="{}">{}</a>'.format(
                    reverse("property_photos", kwargs={'parcel': obj.parcel}), "View Photos")
        return mark_safe(photo_page_link)

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

admin.site.register(price_change, price_changeAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(CDC)
admin.site.register(Neighborhood)
admin.site.register(ContextArea, ContextAreaAdmin)
admin.site.register(featured_property)
admin.site.register(blc_listing)
