from django.contrib import admin
from django.db.models import Q, F
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from django.utils.text import slugify
from datetime import date
from .models import location, company_contact, mailing_address, title_company, closing, processing_fee, purchase_option, closing_proxy, closing_proxy2, buyer_demographic
from .forms import ClosingAdminForm, ClosingScheduleAdminForm
from applications.models import Application, Meeting, MeetingLink
from property_inventory.models import Property, blc_listing

class ProcessingFeeAdmin(admin.ModelAdmin):
    list_display = ['__str__','due_date', 'date_paid', 'paid']
    search_fields = ['closing__application__Property__streetAddress', 'closing__application__Property__parcel', 'closing__application__user__email','closing__application__user__first_name', 'closing__application__user__last_name']

class PurchaseOptionInline(admin.TabularInline):
    model = purchase_option
    fields = ('date_purchased', 'date_expiring', 'amount_paid', )
    readonly_fields=('closing',)
    extra = 1

class BuyerDemographicInline(admin.TabularInline):
    model = buyer_demographic
    extra = 0


class PurchaseOptionFilter(admin.SimpleListFilter):
    title = 'purchase option'
    parameter_name = 'purchase_option'

    def lookups(self, request, model_admin):
        return (
            ('no', 'No option purchased or is expired'),
            ('yes', 'Yes, option purchased and current'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(Q(purchase_option__isnull=True) | Q(purchase_option__date_expiring__lte=date.today()) ).exclude(purchase_option__date_expiring__gte=date.today())
        if self.value() == 'yes':
            return queryset.filter(purchase_option__date_expiring__gte=date.today())

class ProccessingFeePaidFilter(admin.SimpleListFilter):
    title = 'processing fee paid'
    parameter_name = 'processing_fee_payment'

    def lookups(self, request, model_admin):
        return (
            ('no', 'No, processing fee not paid'),
            ('yes', 'Yes, prcessing fee paid'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(processing_fee__paid__exact=False)
        if self.value() == 'yes':
            return queryset.filter(processing_fee__paid__exact=True)


from utils.utils import batch_update_view
def custom_batch_editing__admin_action(self, request, queryset):
    return batch_update_view(
        model_admin=self,
        request=request,
        queryset=queryset,
        # this is the name of the field on the YourModel model
        field_names=['closed', 'notes', 'city_proceeds', 'city_loan_proceeds', 'ri_proceeds', 'ri_closing_fee', 'archived', 'date_time', 'location', 'title_company'],
        #exclude_field_names=['parcel', 'street_address']
    )
custom_batch_editing__admin_action.short_description = "Batch Update"


class ClosingAdmin(admin.ModelAdmin):

    form = ClosingAdminForm
    list_display = ['__str__','title_company','renew_owned', 'date_time', 'processing_fee_paid', 'assigned_city_staff']
    search_fields = ['prop__streetAddress', 'application__Property__streetAddress', 'prop__parcel', 'application__Property__parcel', 'application__organization__name', 'application__user__first_name', 'application__user__last_name', 'application__user__email']
    list_filter = ('title_company', 'closed', PurchaseOptionFilter, ProccessingFeePaidFilter, 'application__Property__renew_owned', 'archived')
    readonly_fields = (
        'recorded_ri_deed_download', 'purchase_agreement', 'nsp', 'processing_fee_url',
        'processing_fee_paid', 'print_deposit_slip','blc_listed',
        'blc_expiration', 'title_commitment_download', 'closing_statement_download',
    'deed_download', 'recorded_city_deed_download', 'ri_deed_download',
    'nsp_convenants_download',
    'project_agreement_download', 'assignment_and_assumption_agreement_download',
     'signed_purchase_agreement_download',
     'renew_sales_disclosure_form_download',
     'city_sales_disclosure_form_download',)
    actions = [custom_batch_editing__admin_action]
    inlines = [PurchaseOptionInline,BuyerDemographicInline]
    raw_id_fields = ('application',)

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(ClosingAdmin, self).get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ClosingAdmin, self).formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == 'notes':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)

        # terrible? way to get object id if we are editting an existing object
        try:
            # http://stackoverflow.com/a/18318866/2731298 -- changed -1 to -2 to grab second to last argument in url since changed in django 1.11 I think
            obj_id = int([i for i in str(kwargs['request'].path).split('/') if i][-2])
        except ValueError:
            obj_id = None

        # If we are edding an existing closing, don't restrict application choices
        if obj_id != None:
            return formfield
        # If we are adding a new closing, restrict choices to only approved unsold applications/properties
        else:
            if db_field.name == "application":
                formfield.queryset = Application.objects.filter(
                    ( Q(meeting__meeting_outcome__exact=MeetingLink.APPROVED_STATUS) & Q(meeting__meeting__meeting_type__exact=Meeting.MDC) & Q(Property__renew_owned__exact=False) ) |
                        ( Q(meeting__meeting_outcome__exact=MeetingLink.APPROVED_STATUS) & Q(meeting__meeting__meeting_type__exact=Meeting.BOARD_OF_DIRECTORS) & Q(Property__renew_owned__exact=True) )
                ).exclude(Property__status__icontains='Sold').filter(closing_set__isnull=True).filter(status=Application.COMPLETE_STATUS)
            if db_field.name == "prop":
                formfield.queryset = Property.objects.filter(
                    (Q(propertyType__exact='in') & Q(status__icontains='Available')) |
                    (Q(renew_owned__exact=True) & Q(
                        status__icontains='Sale approved by Board of Directors'))
                    | Q(status__icontains='Sale approved by MDC')
                )

        return formfield

    def title_commitment_in_place(self, obj):
        file_fields_to_check = [obj.title_commitment]
        if all(file_fields_to_check):
            return True
        else:
            return False
    title_commitment_in_place.boolean = True

    def ri_documents_in_place(self, obj):
        file_fields_to_check = [obj.assignment_and_assumption_agreement, obj.ri_deed]
        if all(file_fields_to_check):
            return True
        else:
            return False
    ri_documents_in_place.boolean = True

    def title_company_documents_in_place(self, obj):
        file_fields_to_check = [obj.closing_statement, obj.title_commitment]
        if all(file_fields_to_check):
            return True
        else:
            return False
    title_company_documents_in_place.boolean = True

    def nsp(self, obj):
        if obj.application:
            return obj.application.Property.nsp
        if obj.prop:
            return obj.prop.nsp
        return None
    nsp.boolean = True

    def processing_fee_paid(self, obj):
        processing_fee = obj.processing_fee.first()
        if processing_fee:
            return processing_fee.paid
        else:
            return False
    processing_fee_paid.boolean = True

    def city_documents_in_place(self, obj):
        file_fields_to_check = [obj.deed, obj.project_agreement]
        if all(file_fields_to_check):
            return True
        else:
            return False
    city_documents_in_place.boolean = True

    def purchase_agreement(self, obj):
        if obj.id is not None:
            pa_link = '<a target="_blank" href="{}">{}</a>'.format(
                reverse("application_purchase_agreement", args=(obj.application.id,)), "Purchase Agreement")
            return mark_safe(pa_link)

    purchase_agreement.short_description = 'Generate Purchase Agreement'

    def processing_fee_url(self, obj):
        pf = processing_fee.objects.filter(closing=obj).first()
        if pf is None:
            return '(none)'
        pf_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_pay_processing_fee", args=(slugify(pf.slug), pf.id,)), reverse("application_pay_processing_fee", args=(slugify(pf.slug), pf.id,)))
        return mark_safe(pf_link)

    def closing_statement_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'closing_statement'}),
                    "Download"
                ))

    def title_commitment_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'title_commitment'}),
                    "Download"
                ))

    def deed_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'deed'}),
                    "Download"
                ))

    def recorded_city_deed_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'recorded_city_deed'}),
                    "Download"
                ))
    def ri_deed_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'ri_deed'}),
                    "Download"
                ))

    def recorded_ri_deed_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'recorded_ri_deed'}),
                    "Download"
                    ))
    def nsp_convenants_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'nsp_convenants'}),
                    "Download"
                ))

    def project_agreement_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'project_agreement'}),
                    "Download"
                ))
    def assignment_and_assumption_agreement_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'assignment_and_assumption_agreement'}),
                    "Download"
                ))

    def signed_purchase_agreement_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'signed_purchase_agreement'}),
                    "Download"
                ))

    def renew_sales_disclosure_form_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'renew_sales_disclosure_form'}),
                    "Download"
                ))

    def city_sales_disclosure_form_download(self, obj):
        if obj.id is not None:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'closings', 'class_name': 'closing', 'pk': obj.id, 'field_name': 'city_sales_disclosure_form'}),
                    "Download"
                ))

    def print_deposit_slip(self, obj):
        if obj.id is None:
            return '-'
        closing_deposit_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("closing_deposit_slip", args=(obj.id,)), "Print deposit sheet")
        return mark_safe(closing_deposit_link)

    def renew_owned(self, obj):
        if obj.application is not None:
            return obj.application.Property.renew_owned
        if obj.prop is not None:
            return obj.prop.renew_owned
        return None
    renew_owned.boolean = True

    def blc_listed(self, obj):
        if obj.application is not None:
            return blc_listing.objects.filter(Property=obj.application.Property).count() > 0
        if obj.prop is not None:
            return blc_listing.objects.filter(Property=obj.prop).count()
        return None
    blc_listed.boolean = True

    def blc_expiration(self, obj):
        if obj.application is not None:
            return blc_listing.objects.filter(Property=obj.application.Property).filter(active=True).first()
        if obj.prop is not None:
            return blc_listing.objects.filter(Property=obj.prop).filter(active=True).first()
        return None


    fieldsets = (
        (None, {
            'fields': (
                ('application', 'prop'),
                ('title_company', 'title_company_freeform'),
                ('date_time', 'location', 'assigned_city_staff'),
                ('processing_fee_paid', 'processing_fee_url'),
            )
            }
        ),
        ('Status',{
            'fields': (
                ('closed','archived',),
                'notes',
            )
        }),
        ('Distributions',{
            'fields': (
                ('print_deposit_slip', 'purchase_agreement'),
                ('city_proceeds', 'city_loan_proceeds'),
                ('ri_proceeds', 'ri_closing_fee'),
                ('other_closing_amount', 'other_closing_amount_note'),
            )
        }),
        ('Documents', {
            'fields': (
            ('recorded_city_deed', 'recorded_city_deed_download','recorded_city_deed_instrument_number',),
            ('recorded_ri_deed', 'recorded_ri_deed_download', 'recorded_ri_deed_instrument_number',),
            # ('title_commitment','title_commitment_download'),
            # ('closing_statement','closing_statement_download'),
            # ('deed', 'deed_download',),
            # ('ri_deed', 'ri_deed_download'),
            # ('nsp_convenants','nsp_convenants_download'),
            # ('project_agreement','project_agreement_download'),
            # ('assignment_and_assumption_agreement','assignment_and_assumption_agreement_download'),
            # ('signed_purchase_agreement','signed_purchase_agreement_download'),
            # ('renew_sales_disclosure_form','renew_sales_disclosure_form_download'),
            # ('city_sales_disclosure_form','city_sales_disclosure_form_download'),
            ),
        }),
    )

class ClosingScheduleViewAdmin(ClosingAdmin):
    model = closing_proxy
    list_display = ['application', 'date_time', 'assigned_city_staff', 'title_company', 'title_commitment_in_place', 'all_documents_in_place', 'city_sales_disclosure_in_place']
    list_filter = ['assigned_city_staff', 'closed', PurchaseOptionFilter, 'archived']
    readonly_fields = ('all_documents_in_place', 'application', 'title_company', 'location', 'date_time', 'deed_in_place','project_agreement_in_place', 'assignment_and_assumption_agreement_in_place', 'closed')
    actions = None

    inlines = []

    fieldsets = (
        (None, {
            'fields': (
                'application', 'assigned_city_staff', 'title_company', 'location', 'date_time', 'deed_in_place','project_agreement_in_place', 'assignment_and_assumption_agreement_in_place', 'city_sales_disclosure_form', 'closed'
            )
        }),

    )

    # This admin view is used by city employees so it shows a limited about of information and only properties owned by the city.
    def get_queryset(self, request):
        qs = super(ClosingScheduleViewAdmin, self).get_queryset(request)
        return qs.filter(application__Property__renew_owned=False).order_by(F('date_time').desc(nulls_last=True))

    def city_sales_disclosure_in_place(self, obj):
#        return obj.city_sales_disclosure_form is not None
        file_fields_to_check = [ obj.city_sales_disclosure_form ]
        if all(file_fields_to_check):
            return True
        else:
            return False
    city_sales_disclosure_in_place.boolean = True




    def deed_in_place(self, obj):
        return obj.deed is not None
    deed_in_place.boolean = True

    def project_agreement_in_place(self, obj):
        return obj.project_agreement is not None
    project_agreement_in_place.boolean = True

    def assignment_and_assumption_agreement_in_place(self, obj):
        return obj.assignment_and_assumption_agreement is not None
    assignment_and_assumption_agreement_in_place.boolean = True

    def all_documents_in_place(self, obj):
        file_fields_to_check = [obj.deed, obj.ri_deed, obj.project_agreement, obj.assignment_and_assumption_agreement]
        if all(file_fields_to_check):
            return True
        else:
            return False
    all_documents_in_place.boolean = True



from django.db.models import Count, Sum, Min, Max
from django.db.models.functions import Trunc
from django.db.models import DateField, DateTimeField

def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy + '__day' in request.GET:
        return 'hour'

    if date_hierarchy + '__month' in request.GET:
        return 'day'

    if date_hierarchy + '__year' in request.GET:
        return 'month'

    return 'month'

class ClosingDistributionAdmin(admin.ModelAdmin):
    change_list_template = 'closing_summary_change_list.html'
    date_hierarchy = 'date_time'
    list_filter = ('application__Property__renew_owned', 'title_company')

    def get_queryset(self, request):
        return super(ClosingDistributionAdmin, self).get_queryset(request).filter(closed=True)

    def changelist_view(self, request, extra_context=None):
        response = super(ClosingDistributionAdmin, self).changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset.filter(closed=True)
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('id'),
            'total_sale_price': Sum(F('ri_proceeds') + F('city_proceeds') + F('city_loan_proceeds') ),
            'total_city_proceeds': Sum('city_proceeds'),
            'total_city_loan_proceeds': Sum('city_loan_proceeds'),
            'total_ri_proceeds': Sum('ri_proceeds'),
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

        period = get_next_in_date_hierarchy(
                    request,
                    self.date_hierarchy,
                )

        response.context_data['scale'] = period
        summary_over_time = qs.annotate(
            period=Trunc(
                'date_time',
                period,
                output_field=DateTimeField(),
            ),
        ).values('period').annotate(total=Sum(F('ri_proceeds') + F('city_proceeds') + F('city_loan_proceeds')), count=Count('id')).order_by('period')

        summary_range = summary_over_time.aggregate(
            low=Min('count'),
            high=Max('count'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)

        response.context_data['summary_over_time'] = [{
            'period': x['period'],
            'total': x['total'] or 0,
            'count': x['count'],
            'high': high,
            'low': low,
            'pct': \
                float( float(x['count'] - 0) / float(high-0) ) * 100,# if x['count'] != low else 1,
        } for x in summary_over_time]

        return response

class BuyerDemographicAdmin(admin.ModelAdmin):
    raw_id_fields = ('closing',)

admin.site.register(purchase_option)
admin.site.register(location)
admin.site.register(company_contact)
admin.site.register(mailing_address)
admin.site.register(title_company)
admin.site.register(closing, ClosingAdmin)
admin.site.register(closing_proxy, ClosingScheduleViewAdmin)
admin.site.register(closing_proxy2, ClosingDistributionAdmin)
admin.site.register(processing_fee, ProcessingFeeAdmin)
admin.site.register(buyer_demographic, BuyerDemographicAdmin)
