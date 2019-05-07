from django.contrib import admin
from .models import annual_report
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

class AnnualReportAdmin(admin.ModelAdmin):
        list_display = ('created','Property', 'name', 'organization')
        #list_filter = ()
        search_fields = ('name', 'organization', 'email', 'Property__parcel', 'Property__streetAddress')
        readonly_fields = ('Property','created', 'lot_picture_download', 'front_exterior_picture_download', 'back_exterior_picture_download', 'kitchen_picture_download', 'bathroom_picture_download', 'other_picture_download')

        def lot_picture_download(self, obj):
            if obj.id is None:
                return '-'
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'user_files', 'class_name': 'UploadedFile', 'pk':obj.id, 'field_name':'lot_picture'}),
                    "Download"
                ))
        def front_exterior_picture_download(self, obj):
            if obj.id is None:
                return '-'
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'user_files', 'class_name': 'UploadedFile', 'pk':obj.id, 'field_name':'front_exterior_picture'}),
                    "Download"
                ))
        def back_exterior_picture_download(self, obj):
            if obj.id is None:
                return '-'
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'user_files', 'class_name': 'UploadedFile', 'pk':obj.id, 'field_name':'back_exterior_picture'}),
                    "Download"
                ))
        def kitchen_picture_download(self, obj):
            if obj.id is None:
                return '-'
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'user_files', 'class_name': 'UploadedFile', 'pk':obj.id, 'field_name':'kitchen_picture'}),
                    "Download"
                ))
        def bathroom_picture_download(self, obj):
            if obj.id is None:
                return '-'
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'user_files', 'class_name': 'UploadedFile', 'pk':obj.id, 'field_name':'bathroom_picture'}),
                    "Download"
                ))
        def other_picture_download(self, obj):
            if obj.id is None:
                return '-'
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'user_files', 'class_name': 'UploadedFile', 'pk':obj.id, 'field_name':'other_picture'}),
                    "Download"
                ))


        fieldsets = (
            ('Property', {
                'fields': (
                    ('Property','parcel'),
                    ('name', 'organization'),
                    ('email', 'phone'),
                    'created'

                ),
            }),
            ('Status', {
                'fields': (
                    ('sold', 'resale_buyer'),
                    ('certificate_of_completion_ready', 'property_occupied'),
                    ('percent_completed', 'past_expenses', 'future_expenses'),
                ),

            }),
            (None, {
                'fields': (
                'work_completed', 'work_remaining', 'feedback',
                )
            }),
            ('Photos', {
                'fields': (
                    ('lot_picture', 'lot_picture_download'),
                    ('front_exterior_picture', 'front_exterior_picture_download'),
                    ('back_exterior_picture', 'back_exterior_picture_download'),
                    ('kitchen_picture', 'kitchen_picture_download'),
                    ('bathroom_picture', 'bathroom_picture_download'),
                    ('other_picture', 'other_picture_download'),

                ),

            }),

        )

admin.site.register(annual_report, AnnualReportAdmin)
