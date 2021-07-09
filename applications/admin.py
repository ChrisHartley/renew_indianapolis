from django.contrib import admin
from .models import Application, Meeting, MeetingLink, PriceChangeMeetingLink, ApplicationMeetingSummary
from user_files.models import UploadedFile
from property_inquiry.models import propertyInquiry
from .forms import ScheduleInlineForm
from property_inventory.models import Property
from django.utils.safestring import mark_safe
from django.urls import reverse
from functools import partial
from django.shortcuts import render
from django.http import HttpResponseRedirect
from utils.admin import ExportCsvMixin

class UploadedFileInline(admin.TabularInline):
    model = UploadedFile
    fields = ('file_purpose', 'file_purpose_other_explanation', 'supporting_document', 'file_download', 'send_with_neighborhood_notification', 'user','application')
    readonly_fields = ('file_download',)
    raw_id_fields = ('user',)
    extra = 1

    def file_download(self, obj):
        if obj.id is None:
            return '-'
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("send_class_file", kwargs={'app_name': 'user_files', 'class_name': 'UploadedFile', 'pk':obj.id, 'field_name':'supporting_document'}),
                "Download"
            ))

class MeetingLinkInline(admin.TabularInline):
    model = MeetingLink
    fields = ('meeting', 'meeting_outcome', 'application_link', 'get_structure_type', 'conditional_approval', 'notes', 'schedule_weight' )
    readonly_fields=('application','application_link', 'get_structure_type')
    ordering = ('application__application_type', 'application__Property__streetAddress', 'schedule_weight')
    extra = 1

    def get_structure_type(self, obj):
        if obj.Property is not None:
            return obj.Property.structureType
        else:
            return '-'

    def get_application_type(self, obj):
        return get_a



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


class MeetingScheduledFilter(admin.SimpleListFilter):
    title = 'scheduled for a meeting'
    parameter_name = 'scheduled'
    def lookups(self, request, model_admin):
        return (
            ('true','Scheduled'),
            ('false', 'Not scheduled'),
            )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(meeting__isnull=False)
        if self.value() == 'false':
            return queryset.filter(meeting__isnull=True)





class ApplicationAdmin(admin.ModelAdmin, ExportCsvMixin):

    list_display = ('modified','submitted_timestamp','Property', 'property_status', 'user_link', 'organization','application_type','scheduled_meeting', 'status')
    list_filter = ('status','application_type', MeetingScheduledFilter)
    search_fields = ('Property__parcel', 'Property__streetAddress', 'user__email', 'user__first_name', 'user__last_name', 'organization__name')
    readonly_fields = ('created', 'modified', 'user_readable', 'property_type',
        'property_status','property_fdl',
        'scheduled_meeting','application_summary_page','application_detail_page',
        'n_notification', 'submitted_timestamp', 'price_at_time_of_submission',
        'property_inquiry_count', 'other_applications')


    raw_id_fields = ('user','Property', 'organization')
    fieldsets = (
        (None, {
            'fields': (
                ('user','user_readable','organization', 'other_applications'),
                ('created', 'modified', 'submitted_timestamp'),
                ('Property', 'property_type','property_status','property_fdl',),
                ('status', 'property_inquiry_count'),
                ('application_summary_page','application_detail_page')
                )

        }),
        ('Qualifying Questions', {
            'fields': ( ('conflict_board_rc', 'conflict_board_rc_name', 'conflict_city', 'conflict_city_name'), 'active_citations', 'prior_tax_foreclosure', 'tax_status_of_properties_owned', 'other_properties_names_owned', 'landlord_in_marion_county', 'landlord_registry')
        }),
        ('Application Details', {
            'fields': ('application_type','planned_improvements','previous_experience','previous_experience_explanation','who_will_perform_work','finished_square_footage', 'single_or_multi_family', 'estimated_cost','source_of_financing', 'why_this_house', 'is_rental','nsp_income_qualifier','long_term_ownership','timeline','sidelot_eligible', 'vacant_lot_end_use')

        }),
        ('Affordable Housing Addendum', {
            'fields': (
                ('aha_application', 'aha_non_profit', 'aha_non_profit_type'),
                ('aha_program_type','aha_unit_breakdown_30','aha_unit_breakdown_40','aha_unit_breakdown_50','aha_unit_breakdown_60','aha_unit_breakdown_80'),
                ('aha_narative'),
                ('aha_funding_lihtc','aha_funding_home','aha_funding_cdbg','aha_funding_tenant_based','aha_funding_nhtf','aha_funding_oz','aha_funding_other'),
                )
        }),
        ('Staff fields', {
            #'classes': ('collapse',),
            'fields': ('staff_summary','staff_notes', 'represented_by_agent', 'staff_intent_neighborhood_notification','neighborhood_notification_details','neighborhood_notification_feedback','staff_sow_total',('staff_pof_total', 'staff_pof_description'),('staff_recommendation','staff_recommendation_notes','staff_points_to_consider','staff_qualifies_for_affordable_housing_price','frozen', 'staff_sidelot_waiver_required','n_notification', 'price_at_time_of_submission'))

        })

    )
    inlines = [ UploadedFileInline, MeetingLinkInline ]
    list_select_related = True
    actions = ['batch_schedule_action','export_as_csv']
    def application_summary_page(self, obj):
        if obj.id is not None:
            summary_link = '<a target="_blank" href="{}">{}</a>'.format(
                reverse("application_summary_page", args=(obj.id,)), "View Summary Page")
        else:
            summary_link = '(none)'
        return mark_safe(summary_link)

    def application_detail_page(self, obj):
        if obj.id is not None:
            summary_link = '<a target="_blank" href="{}">{}</a>'.format(
                reverse("application_detail_page", args=(obj.id,)), "View Detail Page")
        else:
            summary_link = '(none)'

        return mark_safe(summary_link)

    def user_readable(self, obj):
        email_link = '<a target="_blank" href="https://outlook.office.com/mail/deeplink/compose?to={0}&subject={1}&body={2}">{3}</a>'.format(obj.user.email, 'Application: '+str(obj.Property), 'Dear ' +obj.user.first_name+', I have received your application for '+str(obj.Property)+'', obj.user.email)
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

    def property_fdl(self, obj):
        return obj.Property.future_development_program_eligible
    property_fdl.short_description = 'Future Development Lot Program eligible'
    property_fdl.boolean = True

    def property_status(self, obj):
        if obj.Property is None:
            return '-'
        return obj.Property.status

    def property_inquiry_count(self, obj):
        if obj.Property is None:
            return False
        return propertyInquiry.objects.filter(Property__exact=obj.Property).filter(user__exact=obj.user).exclude(status__exact=None).count() > 0
    property_inquiry_count.short_description = 'Property Shown to Applicant'
    property_inquiry_count.boolean = True

    def user_link(self, obj):
       return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:applicants_applicantprofile_change", args=(obj.user.profile.id,)),
                u'{0} {1} {2}'.format(obj.user.first_name, obj.user.last_name, obj.user.email).encode('utf-8')
            ))
    user_link.short_description = 'user'

    def other_applications(self, obj):
        count = Application.objects.filter(user__exact=obj.user).exclude(status__exact=Application.INITIAL_STATUS).count()
        props_purchased = Property.objects.filter(buyer_application__user=obj.user).count()
        props_released = Property.objects.filter(buyer_application__user=obj.user).filter(project_agreement_released=True).count()
        return 'Applications by this user: {0} - Properties Purchased by this user: {1} - Properties purchased and released: {2}'.format(count, props_purchased, props_released)
    other_applications.short_description = 'Application Activity'

    def n_notification(self, obj):
        if obj.id is not None:
            return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
                reverse("application_neighborhood_notification", kwargs={'pk':obj.id}),
                    "Neighborhood Notification"
                ))
        else:
            return '(none)'
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

    def batch_schedule_action(self, request, queryset):
        if 'schedule' in request.POST:
            form = ScheduleInlineForm(request.POST)
            if form.is_valid():
                meeting = form.cleaned_data['meeting']
                meeting_outcome = form.cleaned_data['meeting_outcome']
                for app in queryset:
                    ml = MeetingLink(application=app, meeting=meeting, meeting_outcome=meeting_outcome)
                    ml.save()
                if queryset.count() == 1:
                    message_bit = '1 application was'
                else:
                    message_bit = '{0} applications were'.format(queryset.count(),)
                self.message_user(request, "{0} successfully scheduled for {1}.".format(message_bit, meeting) )

            return HttpResponseRedirect(request.get_full_path())
        else:
            form = ScheduleInlineForm()

        return render(
            request,
            'admin/batch_schedule_intermediary.html',
            context={
                'objects': queryset,
                'form': form,
            }
        )

    batch_schedule_action.short_description = "Schedule for meeting"




class MeetingAdmin(admin.ModelAdmin):
    model = Meeting
    list_filter = ('meeting_type',)
    list_display = ('meeting_type', 'meeting_date')
    inlines = [MeetingLinkInline, PriceChangeMeetingLinkInline]
    ordering = ('-meeting_date',)
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
        summary_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("mdc_resolution", args=(obj.id,)), "View MDC Resolution")
        return mark_safe(summary_link)
    create_mdc_spreadsheet.short_description = 'MDC Resolution'

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
            low=Min('count'),
            high=Max('count'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)

        response.context_data['summary_over_time'] = [{
            'period': x['period'],
            'high': high,
            'low': low,
            'total': x['total'] or 0,
            'count': x['count'] or 0,
            #            'pct': float( float(x['count'] - low) / float(high-low) ) * 100 if x['count'] != low else 1,
            'pct': float( float(x['count'] - 0) / float(high-0) ) * 100,# if x['count'] != low else 1,
            #'pct': (x['count'] - low) / (high-low) * 100,
               #if high > low else 0,
        } for x in summary_over_time]

        return response


admin.site.register(ApplicationMeetingSummary, ApplicationMeetingSummaryAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(MeetingLink)
admin.site.register(PriceChangeMeetingLink)
