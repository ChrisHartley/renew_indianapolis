from django.contrib import admin
from .models import Parcel
# Register your models here.

class ParcelAdmin(admin.ModelAdmin):
    search_fields = ['parcel_number', 'street_address', 'notes']


admin.site.register(Parcel, ParcelAdmin)
