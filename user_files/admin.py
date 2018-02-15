from django.contrib import admin
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from .models import UploadedFile
# Register your models here.
class UploadedFileAdmin(admin.ModelAdmin):
    model = UploadedFile
    list_display = ('user','organization','application','supporting_document', 'send_with_neighborhood_notification')
    readonly_fields = ('file_download',)

    def file_download(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("download_file", kwargs={'id':obj.id}),
                "Download"
            ))

admin.site.register(UploadedFile,UploadedFileAdmin)
