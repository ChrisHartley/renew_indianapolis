from django.contrib import admin
from django.db.models import Q
from .models import location, company_contact, mailing_address, title_company, closing
from applications.models import Application

class ClosingAdmin(admin.ModelAdmin):

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(ClosingAdmin, self).get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ClosingAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "application":
            formfield.queryset = Application.objects.filter(
                    (Q(Property__renew_owned__exact=True) & Q(
                        Property__status__icontains='Sale approved by Board of Directors'))
                    | Q(Property__status__icontains='Sale approved by MDC')
                )

        return formfield


admin.site.register(location)
admin.site.register(company_contact)
admin.site.register(mailing_address)
admin.site.register(title_company)
admin.site.register(closing, ClosingAdmin)
