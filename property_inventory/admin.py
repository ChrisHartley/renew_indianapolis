from django.contrib.gis import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


from .models import Property, CDC, Neighborhood

class PropertyAdmin(admin.OSMGeoAdmin):
    search_fields = ('parcel', 'streetAddress')
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    modifiable = False
    readonly_fields = ('applications_search',)

    def applications_search(self, obj):
        summary_link = '<a href="{}">{}</a>'.format(
            reverse("admin:app_list", args=('applications',))+'application/?q={}'.format(obj.parcel,), "View Applications")
        return mark_safe(summary_link)


admin.site.register(Property, PropertyAdmin)
admin.site.register(CDC)
admin.site.register(Neighborhood)
