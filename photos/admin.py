from django.contrib import admin
from .models import photo
# Register your models here.
class PhotoAdmin(admin.ModelAdmin):
    fields = ( 'prop', 'main_photo', 'image', 'image_tag', 'created')
    readonly_fields = ('image_tag', 'created')
    search_fields = ('prop',)

admin.site.register(photo, PhotoAdmin)
