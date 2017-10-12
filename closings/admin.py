from django.contrib import admin
from django.db.models import Q, F
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django import forms
from django.utils.text import slugify
from datetime import date
from .models import location, company_contact, mailing_address, title_company, closing, processing_fee, purchase_option, closing_proxy
from .forms import ClosingAdminForm, ClosingScheduleAdminForm
from applications.models import Application, Meeting, MeetingLink
from property_inventory.models import Property

class PurchaseOptionInline(admin.TabularInline):
    model = purchase_option
    fields = ('date_purchased', 'date_expiring', 'amount_paid', )
    readonly_fields=('closing',)
    extra = 1


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
            return queryset.filter(Q(purchase_option__isnull=True) | Q(purchase_option__date_expiring__lt=date.today()) )
        if self.value() == 'yes':
            return queryset.filter(purchase_option__date_expiring__gte=date.today())

class ClosingAdmin(admin.ModelAdmin):

    form = ClosingAdminForm
    list_display = ['__unicode__','title_company','date_time', 'processing_fee_paid','nsp', 'title_commitment_in_place', 'city_documents_in_place', 'ri_documents_in_place', 'title_company_documents_in_place']
    search_fields = ['prop__streetAddress', 'application__Property__streetAddress', 'application__user__first_name', 'application__user__last_name', 'application__user__email']
    list_filter = ('title_company', 'closed', PurchaseOptionFilter)
    readonly_fields = ('purchase_agreement', 'nsp', 'processing_fee_url', 'processing_fee_paid')

    inlines = [PurchaseOptionInline,]


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
                    ( Q(meeting__meeting_outcome__exact=MeetingLink.APPROVED_STATUS) & Q(meeting__meeting__meeting_type__exact=Meeting.MDC) ) |
                        ( Q(meeting__meeting_outcome__exact=MeetingLink.APPROVED_STATUS) & Q(meeting__meeting__meeting_type__exact=Meeting.BOARD_OF_DIRECTORS) & Q(Property__renew_owned__exact=True) )
                ).exclude(Property__status__icontains='Sold').filter(closing_set__isnull=True).filter(status=Application.COMPLETE_STATUS)
            if db_field.name == "prop":
                formfield.queryset = Property.objects.filter(
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
        pa_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_purchase_agreement", args=(obj.application.id,)), "Purchase Agreement")
        return mark_safe(pa_link)

    purchase_agreement.short_description = 'Purchase Agreement'

    def processing_fee_url(self, obj):
        pf = processing_fee.objects.filter(closing=obj).first()
        if pf is None:
            return '(none)'
        pf_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_pay_processing_fee", args=(slugify(pf.slug), pf.id,)), reverse("application_pay_processing_fee", args=(slugify(pf.slug), pf.id,)))
        return mark_safe(pf_link)

    def file_download(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("download_file", kwargs={'id':obj.id}),
                "Download"
            ))


class ClosingScheduleViewAdmin(ClosingAdmin):
    model = closing_proxy
    list_display = ['application', 'date_time', 'assigned_city_staff', 'title_company', 'title_commitment_in_place', 'all_documents_in_place', 'city_sales_disclosure_in_place']
    list_filter = ['assigned_city_staff', 'closed', PurchaseOptionFilter]
    readonly_fields = ('all_documents_in_place', 'application', 'title_company', 'location', 'date_time', 'deed','project_agreement', 'assignment_and_assumption_agreement', 'closed')
    fields = ('application','assigned_city_staff', 'title_company', 'location', 'date_time', 'deed','project_agreement', 'assignment_and_assumption_agreement', 'city_sales_disclosure_form', 'closed')
    form = ClosingScheduleAdminForm

    inlines = []

    def get_queryset(self, request):
        qs = super(ClosingScheduleViewAdmin, self).get_queryset(request)
        return qs.filter(application__Property__renew_owned=False).order_by(F('date_time').desc(nulls_last=True))

    def city_sales_disclosure_in_place(self, obj):
        return obj.city_sales_disclosure_form == True
    city_sales_disclosure_in_place.boolean = True

    def all_documents_in_place(self, obj):
        file_fields_to_check = [obj.deed, obj.ri_deed, obj.project_agreement, obj.assignment_and_assumption_agreement]
        if all(file_fields_to_check):
            return True
        else:
            return False
    all_documents_in_place.boolean = True


admin.site.register(purchase_option)
admin.site.register(location)
admin.site.register(company_contact)
admin.site.register(mailing_address)
admin.site.register(title_company)
admin.site.register(closing, ClosingAdmin)
admin.site.register(closing_proxy, ClosingScheduleViewAdmin)
admin.site.register(processing_fee)
