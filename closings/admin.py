from django.contrib import admin
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from .models import location, company_contact, mailing_address, title_company, closing
from .forms import ClosingAdminForm
from applications.models import Application, Meeting, MeetingLink
from property_inventory.models import Property

class ClosingAdmin(admin.ModelAdmin):

    form = ClosingAdminForm
    list_display = ['__unicode__','title_company','date_time', 'city_documents_in_place', 'title_company_documents_in_place']
    search_fields = ['prop__streetAddress', 'application__Property__streetAddress', 'application__user__first_name', 'application__user__last_name', 'application__user__email']
    list_filter = ('title_company', 'closed')
    readonly_fields = ('purchase_agreement',)

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(ClosingAdmin, self).get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ClosingAdmin, self).formfield_for_dbfield(db_field, **kwargs)

        # terrible? way to get object id if we are editting an existing object
        try:
            # http://stackoverflow.com/a/18318866/2731298
            obj_id = int([i for i in str(kwargs['request'].path).split('/') if i][-1])
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

                ).exclude(Property__status__icontains='Sold').filter(closing_set__isnull=True)
            if db_field.name == "prop":
                formfield.queryset = Property.objects.filter(
                    (Q(renew_owned__exact=True) & Q(
                        status__icontains='Sale approved by Board of Directors'))
                    | Q(status__icontains='Sale approved by MDC')
                )

        return formfield

    def title_company_documents_in_place(self, obj):
        file_fields_to_check = [obj.closing_statement, obj.assignment_and_assumption_agreement]
        if all(file_fields_to_check):
            return True
        else:
            return False

    def city_documents_in_place(self, obj):
        file_fields_to_check = [obj.deed, obj.project_agreement]
        if all(file_fields_to_check):
            return True
        else:
            return False

    def purchase_agreement(self, obj):
        pa_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("application_purchase_agreement", args=(obj.application.id,)), "Purchase Agreement")
        return mark_safe(pa_link)

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
