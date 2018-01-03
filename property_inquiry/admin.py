from django.contrib import admin
from .models import propertyInquiry, PropertyInquirySummary
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

class propertyInquiryAdmin(admin.ModelAdmin):
    list_display = ('Property', 'user_name', 'user_phone', 'showing_scheduled', 'timestamp')
    fields = ('Property', 'user_name', 'user_phone','applicant_ip_address','showing_scheduled', 'timestamp')
    search_fields = ('Property__parcel', 'Property__streetAddress', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('applicant_ip_address','timestamp','user_name','user_phone','Property')

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

admin.site.register(propertyInquiry, propertyInquiryAdmin)
