from django.contrib.gis import admin
from .models import Parcel
# Register your models here.

def convert_to_landbank_inventory(modeladmin, request, queryset):
    queryset.update(convert_to_landbank_inventory_on_save=True)
    for p in queryset:
        p.save()
convert_to_landbank_inventory.short_description = 'Convert selected properties to landbank inventory'

class ParcelAdmin(admin.OSMGeoAdmin):
    modifiable = False
    list_filter = ('has_building','classification','interesting','assessor_classification', 'requested_from_commissioners', 'vetted')
    search_fields = ['parcel_number', 'street_address', 'notes']
    list_display = (
        'parcel_number', 'street_address', 'requested_from_commissioners', 'requested_from_commissioners_date',
        'intended_end_use', 'commissioners_response', 'commissioners_response_note',
        'commissioners_resolution_date', 'mdc_acquire_resolution_number',
        'mdc_dispose_resolution_number', 'parcel_in_inventory', 'city_deed_recorded', 'number_of_pictures'
        )
    readonly_fields = ('parcel_in_inventory','number_of_pictures',)
    actions = [convert_to_landbank_inventory,]

admin.site.register(Parcel, ParcelAdmin)
