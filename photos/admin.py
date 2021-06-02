from django.contrib import admin
from .models import photo
# Register your models here.
class PhotoAdmin(admin.ModelAdmin):
    fields = ( 'prop', 'prop_ncst', 'main_photo', 'image', 'image_tag', 'created')
    readonly_fields = ('image_tag', 'created')
    search_fields = ( 'prop__streetAddress', 'prop__parcel', 'prop_ncst__street_address', 'prop_ncst__parcel', 'prop_surplus__street_address', 'prop_surplus__parcel_number',  )
    list_display = ('prop', 'prop_ncst', 'prop_surplus', 'image', 'main_photo')

admin.site.register(photo, PhotoAdmin)
