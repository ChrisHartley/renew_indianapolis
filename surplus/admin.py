from django.contrib.gis import admin
from .models import Parcel
# Register your models here.

class ParcelAdmin(admin.OSMGeoAdmin):
    modifiable = False
    list_filter = ('has_building','classification','interesting','assessor_classification', 'requested_from_commissioners')
    search_fields = ['parcel_number', 'street_address', 'notes']
    list_display = (
        'parcel_number', 'street_address', 'requested_from_commissioners', 'requested_from_commissioners_date',
        'intended_end_use', 'commissioners_response', 'commissioners_response_note',
        'commissioners_resolution_number', 'mdc_acquire_resolution_number',
        'mdc_dispose_resolution_number', 'parcel_in_inventory',

        )
    readonly_fields = ('parcel_in_inventory',)

admin.site.register(Parcel, ParcelAdmin)
