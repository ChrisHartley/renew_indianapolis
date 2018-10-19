from django.contrib import admin
from .models import propertyInquiry, PropertyInquirySummary, propertyShowing, PropertyInquiryMapProxy
from .forms import propertyShowingAdminForm
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.admin import SimpleListFilter

from property_condition.models import ConditionReport
from applications.models import Application
from property_inventory.models import Property

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
        )
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(timestamp__year=self.value())
        return queryset


from utils.utils import batch_update_view
def custom_batch_editing__admin_action(self, request, queryset):
    return batch_update_view(
        model_admin=self,
        request=request,
        queryset=queryset,
        # this is the name of the field on the YourModel model
        field_names=['showing_scheduled','status','notes'],
        #exclude_field_names=['parcel', 'street_address']
    )
custom_batch_editing__admin_action.short_description = "Batch Update"


class propertyInquiryAdmin(admin.ModelAdmin):
    list_display = ('Property', 'renew_owned', 'user_name', 'user_phone', 'status', 'showing_scheduled', 'timestamp')
    fields = (
        'Property', 'user_name', 'user_phone','applicant_ip_address',
        'showing_scheduled', 'timestamp', 'status', 'notes',
        'number_of_pictures', 'condition_report_link',
        'number_completed_apps',
    )
    search_fields = ('Property__parcel', 'Property__streetAddress', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('applicant_ip_address','timestamp','user_name','user_phone','Property', 'number_of_pictures', 'condition_report_link', 'number_completed_apps')
    list_filter = ['status', 'Property__renew_owned', PropertyInquiryYearListFilter]
    actions = [custom_batch_editing__admin_action]


    def renew_owned(self, obj):
        return obj.Property.renew_owned

    def number_of_pictures(self, obj):
        url = reverse('property_photos', kwargs={'parcel':obj.Property.parcel,})
        count = obj.Property.photo_set.get_queryset().count()
        link = '<a href="{}">{}</a>'.format(url,count)
        return mark_safe(link)
    number_of_pictures.short_description = 'Number of photos of property in BlightFight'

    def condition_report_link(self,obj):
        cr = ConditionReport.objects.filter(Property__exact=obj.Property).order_by('timestamp').first()
        if cr is not None:
            url = reverse('admin:property_condition_conditionreport_change', args=(cr.id,))
            name_link = '<a href="{}">{}</a>'.format(url,cr.timestamp)
        else:
            url = reverse('admin:property_condition_conditionreport_add')
            name_link = '<a href="{}">{}</a>'.format(url,'Add')
        return mark_safe(name_link)
    condition_report_link.short_description = 'Condition Report'

    def number_completed_apps(self,obj):
        return Application.objects.filter(Property=obj.Property).filter(status=Application.COMPLETE_STATUS).count()

    def user_name(self, obj):
        email_link = '<a target="_blank" href="https://mail.google.com/a/landbankofindianapolis.org/mail/u/1/?view=cm&fs=1&to={0}&su={1}&body={2}&tf=1">{3}</a>'.format(obj.user.email, 'Property visit: '+str(obj.Property), 'Hi ' +obj.user.first_name+',', obj.user.email)
        name_link = '<a href="{}">{}</a>'.format(
             reverse("admin:applicants_applicantprofile_change", args=(obj.user.profile.id,)),
                 obj.user.first_name + ' ' + obj.user.last_name
             )
        return mark_safe(name_link + ' - ' + email_link)
    user_name.short_description = 'user'

    def user_phone(self, obj):
        return obj.user.profile.phone_number


class PropertyInquiryMapAdmin(propertyInquiryAdmin):
    change_list_template = 'admin/property_inquiry/change_list_map.html'


from icalendar import Calendar, Event, vCalAddress, vText
from datetime import timedelta
class propertyShowingAdmin(admin.ModelAdmin):
    search_fields = ('Property__streetAddress', 'Property__parcel',)
    readonly_fields = ('create_ics','create_email_template')
    form = propertyShowingAdminForm

    def create_ics(self, obj):
        if obj.pk is None:
            return '-'
        return mark_safe(
            '<a target="_blank" href="{}">{}</a>'.format(
                reverse('property_inquiry_create_showing_ics', kwargs={'id': obj.pk}),
                'Generate Calendar Event')
            )
    def create_email_template(self, obj):
        if obj.pk is None:
            return '-'
        return mark_safe(
            '<a target="_blank" href="{}">{}</a>'.format(
                reverse('property_inquiry_showing_email', kwargs={'pk': obj.pk}),
                'Generate Showing Email Template')
            )



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
