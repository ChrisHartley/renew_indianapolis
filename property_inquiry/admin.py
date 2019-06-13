from django.contrib import admin, messages
from .models import propertyInquiry, PropertyInquirySummary, propertyShowing, PropertyInquiryMapProxy
from .forms import propertyShowingAdminForm
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.admin import SimpleListFilter

from property_condition.models import ConditionReport
from applications.models import Application
from property_inventory.models import Property
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Q
from utils.admin import ExportCsvMixin

# add additional filter, year, and allow null status filter
class PropertyInquiryYearListFilter(SimpleListFilter):
    title = 'Property Inquiry Year'
    parameter_name = 'inquiry-year'

    def lookups(self, request, model_admin):
        return (
            ('2014','2014'),
            ('2015','2015'),
            ('2016','2016'),
            ('2017','2017'),
            ('2018','2018'),
            ('2019','2019'),

        )
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(timestamp__year=self.value())
        return queryset


class WorkQueueFilter(SimpleListFilter):
    title = 'Outstanding Inquiries'
    parameter_name = 'outstanding'
    def lookups(self, request, model_admin):
        return (
            (True, 'Yes'),
            (False, 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(Q(status=propertyInquiry.REQUESTED_ANOTHER_INVITATION) | Q(status__isnull=True))
        if self.value() == 'False':
            return queryset.exclude(Q(status=propertyInquiry.REQUESTED_ANOTHER_INVITATION) | Q(status__isnull=True))
        return queryset

class statusFilter(SimpleListFilter):
    title = 'status filter'
    parameter_name = 'status'
    def lookups(self, request, model_admin):
        ALL = 0
        SOLD_STATUS = 1
        USER_CANCELLED_STATUS = 2
        USER_NON_RESPONSIVE_STATUS = 3
        USER_CONTACTED_STATUS = 4
        SCHEDULED_STATUS = 5
        COMPLETED_STATUS = 6
        DUPLICATE_REQUEST_STATUS = 7
        USER_DID_NOT_SHOW = 8
        REQUESTED_ANOTHER_INVITATION = 9
        NULL_STATUS = 10

        STATUS_CHOICES = (
            #(ALL, 'All'),
            (SOLD_STATUS,'Property was sold/pending after request submitted'),
            (USER_CANCELLED_STATUS,'User cancelled request'),
            (USER_NON_RESPONSIVE_STATUS,'User was unresponsive'),
            (USER_CONTACTED_STATUS,'Contacted user to schedule'),
            (SCHEDULED_STATUS,'Showing scheduled'),
            (COMPLETED_STATUS,'Showing completed'),
            (DUPLICATE_REQUEST_STATUS, 'Duplicate request'),
            (USER_DID_NOT_SHOW, 'User did not appear at appointment'),
            (REQUESTED_ANOTHER_INVITATION, 'User would like to be invited to subsequent showing'),
            (NULL_STATUS, 'Initial Status'),
        )
        return STATUS_CHOICES



    def queryset(self, request, queryset):
        if self.value() == None:
           return queryset
        if self.value() == '10':
            return queryset.filter(status__isnull=True)
        if self.value() == '0':
            return queryset
        else:
            qs = queryset.filter(status=int( self.value() ) )
            return qs

from utils.utils import batch_update_view
def custom_batch_editing__admin_action(self, request, queryset):
    return batch_update_view(
        model_admin=self,
        request=request,
        queryset=queryset,
        field_names=['showing_scheduled','status','notes'],
    )
custom_batch_editing__admin_action.short_description = "Batch Update"


class propertyInquiryAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('Property', 'renew_owned', 'user_name', 'user_phone', 'status', 'showing_scheduled', 'timestamp')
    fields = (
        'Property', 'user_name', 'user_phone','applicant_ip_address',
        'showing_scheduled', 'timestamp', 'status', 'notes',
        'number_of_pictures', 'condition_report_link',
        'number_completed_apps',
    )
    search_fields = ('Property__parcel', 'Property__streetAddress', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('applicant_ip_address','timestamp','user_name','user_phone','Property', 'number_of_pictures', 'condition_report_link', 'number_completed_apps')
    list_filter = [WorkQueueFilter, 'Property__renew_owned', PropertyInquiryYearListFilter]
    actions = [custom_batch_editing__admin_action, 'export_as_csv']


    def renew_owned(self, obj):
        return obj.Property.renew_owned

    def number_of_pictures(self, obj):
        url = reverse('property_photos', kwargs={'parcel':obj.Property.parcel,})
        count = obj.Property.photo_set.get_queryset().count()
        link = u'<a href="{}">{}</a>'.format(url,count)
        return mark_safe(link)
    number_of_pictures.short_description = 'Number of photos of property in BlightFight'

    def condition_report_link(self,obj):
        cr = ConditionReport.objects.filter(Property__exact=obj.Property).order_by('timestamp').first()
        if cr is not None:
            url = reverse('admin:property_condition_conditionreport_change', args=(cr.id,))
            name_link = u'<a href="{}">{}</a>'.format(url,cr.timestamp)
        else:
            url = reverse('admin:property_condition_conditionreport_add')
            name_link = u'<a href="{}">{}</a>'.format(url,'Add')
        return mark_safe(name_link)
    condition_report_link.short_description = 'Condition Report'

    def number_completed_apps(self,obj):
        return Application.objects.filter(Property=obj.Property).filter(status=Application.COMPLETE_STATUS).count()

    def user_name(self, obj):
        email_link = u'<a target="_blank" href="https://mail.google.com/a/landbankofindianapolis.org/mail/u/1/?view=cm&fs=1&to={0}&su={1}&body={2}&tf=1">{3}</a>'.format(obj.user.email, 'Property visit: '+str(obj.Property), 'Hi ' +obj.user.first_name+',', obj.user.email)
        name_link = u'<a href="{}">{}</a>'.format(
             reverse("admin:applicants_applicantprofile_change", args=(obj.user.profile.id,)),
                 obj.user.first_name + ' ' + obj.user.last_name
             )
        return mark_safe(name_link + ' - ' + email_link)
    user_name.short_description = 'user'

    def user_phone(self, obj):
        return obj.user.profile.phone_number


class PropertyInquiryMapAdmin(propertyInquiryAdmin):
    change_list_template = 'admin/property_inquiry/change_list_map.html'
    def changelist_view(self, request, extra_context=None):
            extra_context = extra_context or {}
            #response.context_data['cl'].queryset
            extra_context['popup_link'] = """<a target="_blank" href="/admin/property_inquiry/propertyshowing/add/?Property='+details['id']+'">Create a property showing.</a>"""
            return super(PropertyInquiryMapAdmin, self).changelist_view(
                request, extra_context=extra_context
            )

def admin_really_delete(self, request, queryset):
    for obj in queryset:
        obj.delete()
    messages.add_message(request, messages.INFO, '{} objects deleted.'.format(queryset.count(),))
admin_really_delete.short_description = 'Delete selected showings'


from icalendar import Calendar, Event, vCalAddress, vText
from datetime import timedelta
from django.shortcuts import render

class propertyShowingAdmin(admin.ModelAdmin):
    search_fields = ('Property__streetAddress', 'Property__parcel',)
    #readonly_fields = ('create_ics','create_email_template', 'property_status', 'google_private_calendar_event_id', 'google_public_calendar_event_id' 'show_release_template')
    readonly_fields = (
        'create_ics',
        'create_email_template',
        'property_status',
        'show_release_template',
        'google_public_calendar_event_id',
        'google_private_calendar_event_id',
        'download_signin_sheet',
        'get_inquiry_rsvp_id'
    )
    form = propertyShowingAdminForm
    actions = ['batch_calendar_and_email', 'showing_batch_update__admin_action']
#    inlines = [propertyInquiryInlineAdmin,]
    #exclude = ('inquiries',)
    def property_status(self, obj):
        return obj.Property.status

    def create_ics(self, obj):
        if obj.pk is None:
            return '-'
        return mark_safe(
            u'<a target="_blank" href="{}">{}</a>'.format(
                reverse('property_inquiry_create_showing_ics', kwargs={'pks': obj.pk}),
                'Add to Calendar and Publish')
            )
    def create_email_template(self, obj):
        if obj.pk is None:
            return '-'
        return mark_safe(
            u'<a target="_blank" href="{}">{}</a>'.format(
                reverse('property_inquiry_showing_emails', args={obj.pk}),
                'Generate Showing Email Template')
            )

    def show_release_template(self, obj):
        if obj.pk is None:
            return '-'
        return mark_safe(
            u'<a target="_blank" href="{}">{}</a>'.format(
                reverse('property_inquiry_showing_release', args={obj.pk}),
                'Generate Sign-in Sheet and Release')
        )

    def download_signin_sheet(self, obj):
        if obj.pk is None:
            return '-'
        url = reverse("send_class_file", kwargs={'app_name': 'property_inquiry', 'class_name': 'propertyShowing', 'pk':obj.id, 'field_name':'signin_sheet'})
        link = u'<a href="{}">Download</a>'.format(url,)
        return mark_safe(link)
    download_signin_sheet.short_description = 'Download Signin Sheet'


    def save_related(self, request, form, formsets, change):
        super(propertyShowingAdmin, self).save_related(request, form, formsets, change)
        # Update inquiries, if they are initial status set them to contacted user to schedule
        for inquiry in form.instance.inquiries.all():
            if inquiry.status == propertyInquiry.NULL_STATUS:
                inquiry.status = propertyInquiry.USER_CONTACTED_STATUS
            if inquiry.showing_scheduled is None or inquiry.showing_scheduled.date() < form.instance.datetime.date():
                inquiry.showing_scheduled = form.instance.datetime
            inquiry.save()


    def batch_calendar_and_email(self, request, queryset):
        return render(
            request,
            'admin/property_inquiry/showing_batch_calendar_and_email.html',
            context={
                'objects': queryset,
                'object_pks': ','.join(str(e) for e in list(queryset.values_list('id', flat=True))),
            }
        )

    batch_calendar_and_email.short_description = 'Create calendar and email invites'

    def showing_batch_update__admin_action(self, request, queryset):
        return batch_update_view(
            model_admin=self,
            request=request,
            queryset=queryset,
            field_names=['signin_sheet','notes',],
        )
    showing_batch_update__admin_action.short_description = "Batch Update"

    def get_actions(self, request):
        actions = super(propertyShowingAdmin, self).get_actions(request)
        #print actions
        del actions['delete_selected']
        return actions

    def get_inquiry_rsvp_id(self, obj):
        #print self.request
        #print(self.request.build_absolute_uri(reverse('submit_property_inquiry')))
        if obj.id is not None and obj.Property is not None:
           url = '{}?parcel={}&rsvpId={}'.format(reverse('submit_property_inquiry'), obj.Property.parcel, obj.id)
        else:
           return '-'
        link = u'<a href="{}">Link</a>'.format(url,)
        return mark_safe(link)
    get_inquiry_rsvp_id.short_description = 'URL for inquiry with auto RSVP'

    def save_model(self, request, obj, form, change):
        if change:
            inqs = form.cleaned_data.get('inquiries_to_complete', None)
            if inqs is not None:
                for inq in inqs:
                    pi = propertyInquiry.objects.get(id=inq)
                    pi.status = propertyInquiry.COMPLETED_STATUS
                    pi.save()
        super(propertyShowingAdmin, self).save_model(request, obj, form, change)


from django.db.models import Count, Sum, Min, Max
from django.db.models.functions import Trunc
from django.db.models import DateTimeField

def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy + '__day' in request.GET:
        return 'hour'

    if date_hierarchy + '__month' in request.GET:
        return 'day'

    if date_hierarchy + '__year' in request.GET:
        return 'month'

    return 'month'

class PropertyInquirySummaryAdmin(admin.ModelAdmin):
    change_list_template = 'property_inquiry_summary_change_list.html'
    date_hierarchy = 'timestamp'
    list_filter = ('Property__renew_owned',)

    def changelist_view(self, request, extra_context=None):
        response = super(PropertyInquirySummaryAdmin, self).changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'count': Count('id'),
            'total_sales': Sum('Property__price'),
        }

        response.context_data['summary'] = list(
            qs
            .values('Property__zipcode__name')
            .annotate(**metrics)
            .order_by('Property__zipcode__name')
        )

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        period = get_next_in_date_hierarchy(
                request,
                self.date_hierarchy,
        )
        response.context_data['scale'] = period

        summary_over_time = qs.annotate(
            period=Trunc(
                'timestamp',
                period,
                output_field=DateTimeField(),
            ),
        ).values('period').annotate(count=Count('id')).order_by('period')

        summary_range = summary_over_time.aggregate(
            low=Min('count'),
            high=Max('count'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)

        response.context_data['summary_over_time'] = [{
            'period': x['period'],
            #'total': x['total'] or 0,
            'count': x['count'],
            'pct': \
               ( (x['count']*1.0 or 0) - low) / (high - low) * 100
               if high > low else 0,
        } for x in summary_over_time]

        return response


admin.site.register(PropertyInquirySummary, PropertyInquirySummaryAdmin)
admin.site.register(PropertyInquiryMapProxy, PropertyInquiryMapAdmin)
admin.site.register(propertyInquiry, propertyInquiryAdmin)
admin.site.register(propertyShowing, propertyShowingAdmin)
