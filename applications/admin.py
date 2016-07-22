from django.contrib import admin
from .models import Application, Meeting, MeetingLink, NeighborhoodNotification
from neighborhood_associations.models import Neighborhood_Association
from user_files.models import UploadedFile

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from import_export.admin import ExportMixin
from functools import partial


class UploadedFileInline(admin.TabularInline):
    model = UploadedFile
    fields = ('file_purpose', 'file_purpose_other_explanation', 'supporting_document', 'file_download','user','application')
    readonly_fields = ('file_download',)
    extra = 0

    def file_download(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("download_file", kwargs={'id':obj.id}),
                "Download"
            ))

class MeetingLinkInline(admin.TabularInline):
    model = MeetingLink
    extra = 1

class NeighborhoodNotificationAdmin(admin.TabularInline):
    model = NeighborhoodNotification
    extra = 1
    fields = ('neighborhood','neighborhood_contact','feedback')
    readonly_fields = ('neighborhood_contact',)

    def neighborhood_contact(self, obj):
        return obj.neighborhood.contact_email_address
    # I am very proud of this. Source: http://stackoverflow.com/questions/14950193/how-to-get-the-current-model-instance-from-inlineadmin-in-django
    # This limits the neighborhood associations shown in the dropdown to only the ones that contain the property.
    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(NeighborhoodNotificationAdmin, self).get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        app = kwargs.pop('obj', None)
        formfield = super(NeighborhoodNotificationAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "neighborhood" and app is not None and app.Property:
            formfield.queryset = Neighborhood_Association.objects.filter(receive_notifications__exact=True).filter(geometry__contains=app.Property.geometry)
        return formfield

class ApplicationAdmin(admin.ModelAdmin, ExportMixin):
    list_display = ('modified','Property', 'user_link', 'organization','application_type','scheduled_meeting', 'status')
    list_filter = ('status','application_type')
    search_fields = ('Property__parcel', 'Property__streetAddress', 'user__email', 'user__first_name', 'user__last_name', 'organization__name')
    readonly_fields = ('created', 'modified', 'user_readable', 'property_type', 'property_status','property_nsp','property_sidelot','scheduled_meeting','application_summary_page','application_detail_page','n_notification')
    fieldsets = (
        (None, {
            'fields': ( ('user','user_readable','organization'), ('created', 'modified'), ('Property', 'property_type','property_status','property_nsp','property_sidelot'), 'status', ('application_summary_page','application_detail_page'))

        }),
        ('Qualifying Questions', {
            'fields': ( ('conflict_board_rc', 'conflict_board_rc_name'), 'active_citations', 'prior_tax_foreclosure', 'tax_status_of_properties_owned', 'other_properties_names_owned')
        }),
        ('Application Details', {
            'fields': ('application_type','planned_improvements','estimated_cost','source_of_financing','is_rental','nsp_income_qualifier','long_term_ownership','timeline','sidelot_eligible')

        }),
        ('Staff fields', {
            'classes': ('collapse',),
            'fields': ('staff_summary','staff_notes','neighborhood_notification_details','staff_sow_total',('staff_pof_total', 'staff_pof_description'),('staff_recommendation','staff_recommendation_notes','staff_points_to_consider','frozen','n_notification'))

        })

    )
    inlines = [ UploadedFileInline, NeighborhoodNotificationAdmin, MeetingLinkInline ]

    def application_summary_page(self, obj):
        summary_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_summary_page", args=(obj.id,)), "View Summary Page")
        return mark_safe(summary_link)

    def application_detail_page(self, obj):
        summary_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_detail_page", args=(obj.id,)), "View Detail Page")
        return mark_safe(summary_link)

    def user_readable(self, obj):
        email_link = '<a target="_blank" href="https://mail.google.com/a/landbankofindianapolis.org/mail/u/1/?view=cm&fs=1&to={0}&su={1}&body={2}&tf=1">{3}</a>'.format(obj.user.email, 'Application: '+str(obj.Property), 'Hi ' +obj.user.first_name+',', obj.user.email)
        name_link = '<a href="{}">{}</a>'.format(
             reverse("admin:applicants_applicantprofile_change", args=(obj.user.profile.id,)),
                 obj.user.first_name + ' ' + obj.user.last_name
             )
        return mark_safe(name_link + ' - ' + email_link)
    user_readable.short_description = 'user'

    def property_type(self, obj):
        return obj.Property.structureType

    def scheduled_meeting(self, obj):
        return obj.meeting.latest('meeting')
    scheduled_meeting.admin_order_field = 'meeting'

    def property_nsp(self, obj):
        return obj.Property.nsp

    def property_sidelot(self, obj):
        return obj.Property.sidelot_eligible

    def property_status(self, obj):
        return obj.Property.status

    def user_link(self, obj):
       return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:applicants_applicantprofile_change", args=(obj.user.profile.id,)),
                obj.user.first_name + ' ' + obj.user.last_name + ' - ' + obj.user.email
            ))
    user_link.short_description = 'user'

    def n_notification(self, obj):
        return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_neighborhood_notification", kwargs={'pk':obj.id}),
                "Neighborhood Notification"
            ))
        #pass
    n_notification.short_description = 'Neighborhood Notification'

class MeetingAdmin(admin.ModelAdmin):
    model = Meeting
    list_filter = ('meeting_type',)
    list_display = ('meeting_type', 'meeting_date')
    inlines = [MeetingLinkInline]
    readonly_fields = ('agenda', 'create_packet', 'create_packet_support_documents')

    def agenda(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
            reverse("rc_agenda", kwargs={'pk':obj.id}),
                "Generate Agenda"
            ))
    agenda.short_description = 'Agenda'

    def create_packet(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
            reverse("staff_packet", kwargs={'pk':obj.id}),
                "Generate Staff Recommendations and Summary Packet"
            ))
    create_packet.short_description = 'Packet'

    def create_packet_support_documents(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
            reverse("staff_packet_attachements", kwargs={'pk':obj.id}),
                "Generate Supporting Documents Archive"
            ))
    create_packet_support_documents.short_description = 'Supporting Documents'






admin.site.register(Application, ApplicationAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(MeetingLink)
