from django.contrib import admin
from .models import photo
# Register your models here.
class PhotoAdmin(admin.ModelAdmin):
    fields = ( 'prop', 'Property_ncst' 'main_photo', 'image', 'image_tag', 'created')
    readonly_fields = ('image_tag', 'created')
    search_fields = ( 'prop__streetAddress', 'prop__parcel', 'Property_ncst__street_address', 'Property_ncst__parcel')
    list_display = ('prop', 'Property_ncst', 'image', 'main_photo')

admin.site.register(photo, PhotoAdmin)
