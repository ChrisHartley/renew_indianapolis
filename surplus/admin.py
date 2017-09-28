from django.contrib import admin
from .models import Parcel
# Register your models here.

class ParcelAdmin(admin.ModelAdmin):
    list_filter = ('has_building','classification','interesting','assessor_classification')
    search_fields = ['parcel_number', 'street_address', 'notes']
    list_display = ('parcel_number', 'street_address', 'requested_from_commissioners_date', 'intended_end_use', 'commissioners_response', 'commissioners_response_note', 'commissioners_resolution_number', 'mdc_acquire_resolution_number')


admin.site.register(Parcel, ParcelAdmin)
