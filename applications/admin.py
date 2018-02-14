from django.contrib import admin
from .models import Application, Meeting, MeetingLink, NeighborhoodNotification, PriceChangeMeetingLink, ApplicationMeetingSummary
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
    extra = 1

    def file_download(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("download_file", kwargs={'id':obj.id}),
                "Download"
            ))

class MeetingLinkInline(admin.TabularInline):
    model = MeetingLink
    fields = ('meeting', 'meeting_outcome', 'application_link', 'notes', )
    readonly_fields=('application','application_link')
    extra = 1

    def application_link(self, obj):
       return mark_safe('<a href="{}" target="_blank">{}</a>'.format(
            reverse("admin:applications_application_change", args=(obj.application.id,)),
                obj.application
            ))
    application_link.short_description = 'application'

class PriceChangeMeetingLinkInline(admin.TabularInline):
    model = PriceChangeMeetingLink
    fields = ('meeting','meeting_outcome', 'price_change', 'notes', )
    readonly_fields=('price_change','price_change_link',)
    extra = 1

    def price_change_link(self, obj):
       return mark_safe('<a href="{}" target="_blank">{}</a>'.format(
            reverse("admin:property_inventory_price_change_change", args=(obj.price_change.id,)),
                obj.application
            ))
    price_change_link.short_description = 'price change'



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
    list_display = ('modified','Property', 'num_scheduled_apps', 'user_link', 'organization','application_type','scheduled_meeting', 'status')
    list_filter = ('status','application_type')
    search_fields = ('Property__parcel', 'Property__streetAddress', 'user__email', 'user__first_name', 'user__last_name', 'organization__name')
    readonly_fields = ('created', 'modified', 'user_readable', 'property_type', 'property_status','property_vacant_lot','property_sidelot','scheduled_meeting','application_summary_page','application_detail_page','n_notification', 'submitted_timestamp', 'price_at_time_of_submission')
    fieldsets = (
        (None, {
            'fields': ( ('user','user_readable','organization'), ('created', 'modified', 'submitted_timestamp'), ('Property', 'property_type','property_status','property_vacant_lot','property_sidelot'), 'status', ('application_summary_page','application_detail_page'))

        }),
        ('Qualifying Questions', {
            'fields': ( ('conflict_board_rc', 'conflict_board_rc_name'), 'active_citations', 'prior_tax_foreclosure', 'tax_status_of_properties_owned', 'other_properties_names_owned', 'landlord_in_marion_county', 'landlord_registry')
        }),
        ('Application Details', {
            'fields': ('application_type','planned_improvements','estimated_cost','source_of_financing','is_rental','nsp_income_qualifier','long_term_ownership','timeline','sidelot_eligible')

        }),
        ('Staff fields', {
            'classes': ('collapse',),
            'fields': ('staff_summary','staff_notes','neighborhood_notification_details','neighborhood_notification_feedback','staff_sow_total',('staff_pof_total', 'staff_pof_description'),('staff_recommendation','staff_recommendation_notes','staff_points_to_consider','frozen', 'staff_sidelot_waiver_required','n_notification', 'price_at_time_of_submission'))

        })

    )
    inlines = [ UploadedFileInline, NeighborhoodNotificationAdmin, MeetingLinkInline ]
    list_select_related = True

    def application_summary_page(self, obj):
        summary_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_summary_page", args=(obj.id,)), "View Summary Page")
        return mark_safe(summary_link)

    def application_detail_page(self, obj):
        summary_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_detail_page", args=(obj.id,)), "View Detail Page")
        return mark_safe(summary_link)

    def user_readable(self, obj):
        email_link = '<a target="_blank" href="https://mail.google.com/a/landbankofindianapolis.org/mail/u/1/?view=cm&fs=1&to={0}&su={1}&body={2}&tf=1">{3}</a>'.format(obj.user.email, 'Application: '+str(obj.Property), 'Dear ' +obj.user.first_name+', I have received your application for '+str(obj.Property)+'', obj.user.email)
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

    def property_vacant_lot(self, obj):
        return obj.Property.vacant_lot_eligible

    def property_sidelot(self, obj):
        return obj.Property.sidelot_eligible

    def property_status(self, obj):
        return obj.Property.status

    def user_link(self, obj):
       return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:applicants_applicantprofile_change", args=(obj.user.profile.id,)),
                u'{0} {1} {2}'.format(obj.user.first_name, obj.user.last_name, obj.user.email).encode('utf-8').strip()
            ))
    user_link.short_description = 'user'

    def n_notification(self, obj):
        return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_neighborhood_notification", kwargs={'pk':obj.id}),
                "Neighborhood Notification"
            ))
        #pass
    n_notification.short_description = 'Neighborhood Notification'


    def num_scheduled_apps(self, obj):
        count = Application.objects.filter(Property__exact=obj.Property).filter(status__exact=Application.COMPLETE_STATUS).filter(meeting__isnull=False).count()
        if obj.Property is not None:
            summary_link = '<a href="{}">{}</a>'.format(
                reverse("admin:app_list", args=('applications',))+'application/?q={}'.format(obj.Property.parcel,), count)
        else:
            summary_link = '-'
        return mark_safe(summary_link)

    num_scheduled_apps.short_description = 'Number of completed, schedule apps'

class MeetingAdmin(admin.ModelAdmin):
    model = Meeting
    list_filter = ('meeting_type',)
    list_display = ('meeting_type', 'meeting_date')
    inlines = [MeetingLinkInline, PriceChangeMeetingLinkInline]
    readonly_fields = ('agenda', 'applications', 'create_mdc_spreadsheet', 'create_packet', 'create_packet_support_documents', 'price_change_summary_page','price_change_CMA_zip','price_change_csv', 'create_meeting_outcome_notification_spreadsheet', 'create_epp_update_spreadsheet', 'create_epp_party_spreadsheet', 'generate_neighborhood_notifications')
#    list_select_related = True


    def price_change_csv(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        summary_link = '<a target="_blank" href="{}?export=csv">{}</a>'.format(
            reverse("price_change_summary_view_all", args=(obj.id,)), "View Price Change CSV Spreadsheet")
        return mark_safe(summary_link)
    price_change_csv.short_description = 'Price Changes CSV spreadsheet'

    def create_mdc_spreadsheet(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        summary_link = '<a target="_blank" href="{}?export=csv">{}</a>'.format(
            reverse("mdc_spreadsheet", args=(obj.id,)), "View CSV Spreadsheet for MDC Resolution")
        return mark_safe(summary_link)
    create_mdc_spreadsheet.short_description = 'MDC Resolution CSV spreadsheet'

    def create_meeting_outcome_notification_spreadsheet(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        summary_link = '<a target="_blank" href="{}?export=csv">{}</a>'.format(
            reverse("meeting_outcome_notification_spreadsheet", args=(obj.id,)), "View CSV Spreadsheet for Meeting Outcome Mail Merge")
        return mark_safe(summary_link)
    create_meeting_outcome_notification_spreadsheet.short_description = 'Meeting Outcome Mail Merge CSV spreadsheet'


    def create_epp_update_spreadsheet(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        summary_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("epp_update_spreadsheet", args=(obj.id,)), "Generate Spreadsheet for ePP Price and Status Property Update")
        return mark_safe(summary_link)
    create_epp_update_spreadsheet.short_description = 'ePropertyPlus Update spreadsheet'

    def create_epp_party_spreadsheet(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        summary_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("epp_update_party_spreadsheet", args=(obj.id,)), "Generate Spreadsheet for ePP Party Update")
        return mark_safe(summary_link)
    create_epp_party_spreadsheet.short_description = 'ePropertyPlus Update Party spreadsheet'




    def agenda(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
            reverse("rc_agenda", kwargs={'pk':obj.id}),
                "Generate Agenda"
            ))
    agenda.short_description = 'Agenda'

    def applications(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_packet", kwargs={'pk':obj.id}),
                "Generate Applications"
            ))
    applications.short_description = 'Applications'

    def price_change_summary_page(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        summary_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("price_change_summary_view_all", args=(obj.id,)), "View Price Change Summary Page")
        return mark_safe(summary_link)
    price_change_summary_page.short_description = 'Price Changes'

    def generate_neighborhood_notifications(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        summary_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("generate_neighborhood_notifications", args=(obj.id,)), "Generate neighborhood notifications")
        return mark_safe(summary_link)
    generate_neighborhood_notifications.short_description = 'Notifications'



    def price_change_CMA_zip(self, obj):
        if obj.id is None:
            return mark_safe('<a href="">(none)</a>')
        return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
            reverse("staff_packet_price_change_CMA_attachements", kwargs={'pk':obj.id}),
                "Generate CMA Archive"
            ))
    price_change_CMA_zip.short_description = 'CMA Archive'



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


from django.db.models import Count, Sum, Min, Max
from django.db.models.functions import Trunc
from django.db.models import DateField
class ApplicationMeetingSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'app_summary_change_list.html'
    date_hierarchy = 'meeting__meeting_date'
    list_filter = ('meeting__meeting_type', 'meeting_outcome',)

    def changelist_view(self, request, extra_context=None):
        response = super(ApplicationMeetingSummaryAdmin, self).changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('id'),
            'total_sales': Sum('application__Property__price'),
        }

        response.context_data['summary'] = list(
            qs
            .values('application__application_type')
            .annotate(**metrics)
            .order_by('-application__application_type')
        )

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)

        )

        summary_over_time = qs.annotate(
            period=Trunc(
                'meeting__meeting_date',
                'day',
                output_field=DateField(),
            ),
        ).values('period').annotate(total=Sum('application__Property__price'), count=Count('application')).order_by('period')

        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)

        response.context_data['summary_over_time'] = [{
            'period': x['period'],
            'total': x['total'] or 0,
            'count': x['count'],
            'pct': \
               ((x['total'] or 0) - low) / (high - low) * 100
               if high > low else 0,
        } for x in summary_over_time]

        return response


admin.site.register(ApplicationMeetingSummary, ApplicationMeetingSummaryAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(MeetingLink)
admin.site.register(PriceChangeMeetingLink)
