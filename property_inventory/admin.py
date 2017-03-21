from django.contrib.gis import admin
from django.contrib.admin import SimpleListFilter
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.db.models import Q


from .models import Property, CDC, Neighborhood

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

class PropertyStatusListFilter(SimpleListFilter):
    title = 'Property Status'
    parameter_name = 'status'
    def lookups(self, request, model_admin):
        return (
            ('sold', 'Sold'),
            ('approved', 'Received Final Approval'),
            ('consideration', 'Application under consideration')
        )

    def queryset(self, request, queryset):
        if self.value() == 'sold':
            return queryset.filter(status__contains='Sold')
        if self.value() == 'approved':
            return queryset.filter( ( Q(status__contains='Sale approved by MDC') & Q(renew_owned__exact=False) ) | (Q(status__contains='Sale approved by Board of Directors') & Q(renew_owned__exact=True)) )
        if self.value() == 'consideration':
            return queryset.filter( Q(status__contains='Sale approved by Review Committee') | (Q(status__contains='Sale approved by Board of Directors') & Q(renew_owned__exact=False)))
        return queryset



class PropertyAdmin(admin.OSMGeoAdmin):
    search_fields = ('parcel', 'streetAddress', 'zipcode__name')
    list_display = ('parcel', 'streetAddress', 'structureType','status')
    list_filter = (PropertyStatusListFilter,'structureType', PropertyStatusYearListFilter )

    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    modifiable = False
    readonly_fields = ('applications_search','view_photos')

    def applications_search(self, obj):
        summary_link = '<a href="{}">{}</a>'.format(
            reverse("admin:app_list", args=('applications',))+'application/?q={}'.format(obj.parcel,), "View Applications")
        return mark_safe(summary_link)

    def view_photos(self, obj):
        photo_page_link = '<a href="{}">{}</a>'.format(
                    reverse("property_photos", kwargs={'parcel': obj.parcel}), "View Photos")

#https://www.renewindianapolis.org/map/property/1062924/photos/
        return mark_safe(photo_page_link)


admin.site.register(Property, PropertyAdmin)
admin.site.register(CDC)
admin.site.register(Neighborhood)
