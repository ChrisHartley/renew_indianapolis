from django.contrib import admin
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from .models import location, company_contact, mailing_address, title_company, closing
from .forms import ClosingAdminForm
from applications.models import Application
from property_inventory.models import Property

class ClosingAdmin(admin.ModelAdmin):

    form = ClosingAdminForm
    list_display = ['__unicode__','title_company','date_time', 'documents_in_place']
    search_fields = ['prop__streetAddress', 'application__Property__streetAddress', 'application__user__first_name', 'application__user__last_name', 'application__user__email']
    list_filter = ('title_company',)
    readonly_fields = ('purchase_agreement',)

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(ClosingAdmin, self).get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ClosingAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        app = kwargs.pop('obj', None)
        prop = kwargs.pop('obj', None)
        if db_field.name == "application":
            formfield.queryset = Application.objects.filter(
                (Q(Property__renew_owned__exact=True) & Q(
                    Property__status__icontains='Sale approved by Board of Directors'))
                | Q(Property__status__icontains='Sale approved by MDC')
            )
        if db_field.name == "prop":
            formfield.queryset = Property.objects.filter(
                (Q(renew_owned__exact=True) & Q(
                    status__icontains='Sale approved by Board of Directors'))
                | Q(status__icontains='Sale approved by MDC')
            )

        return formfield

    def documents_in_place(self, obj):
        file_fields_to_check = [obj.closing_statement, obj.deed, obj.project_agreement, obj.assignment_and_assumption_agreement]
        if all(file_fields_to_check):
            return True
        else:
            return False

    def purchase_agreement(self, obj):
        return mark_safe('<a target="_blank" href="/application/view/purchase_agreement/{}">{}</a>'.format(
            obj.application.id, "Purchase Agreement"
            ))
        #pass
    purchase_agreement.short_description = 'Purchase Agreement'


    def file_download(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("download_file", kwargs={'id':obj.id}),
                "Download"
            ))


admin.site.register(location)
admin.site.register(company_contact)
admin.site.register(mailing_address)
admin.site.register(title_company)
admin.site.register(closing, ClosingAdmin)
