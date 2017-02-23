from django.contrib.gis import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


from .models import Property, CDC, Neighborhood

class PropertyAdmin(admin.OSMGeoAdmin):
    search_fields = ('parcel', 'streetAddress')
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
