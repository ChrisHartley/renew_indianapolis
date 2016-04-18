from django.contrib.gis import admin

from .models import Neighborhood_Association

class Neighborhood_AssociationAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'last_updated')
    search_fields = ('name', 'contact_first_name', 'contact_last_name', 'contact_email_address', )
admin.site.register(Neighborhood_Association, Neighborhood_AssociationAdmin)
