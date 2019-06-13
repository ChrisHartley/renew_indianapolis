from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import UploadedFile
# Register your models here.
class UploadedFileAdmin(admin.ModelAdmin):
    model = UploadedFile
    list_display = ('user','organization','application','supporting_document', 'send_with_neighborhood_notification')
    readonly_fields = ('file_download',)
    search_fields = ['application__Property__parcel', 'application__Property__streetAddress', 'user__email', 'user__first_name', 'user__last_name']
    def file_download(self, obj):
        if obj is None:
            return '-'
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("send_class_file", kwargs={'app_name': 'user_files', 'class_name': 'UploadedFile', 'pk':obj.id, 'field_name':'supporting_document'}),
                "Download"
            ))

admin.site.register(UploadedFile,UploadedFileAdmin)
