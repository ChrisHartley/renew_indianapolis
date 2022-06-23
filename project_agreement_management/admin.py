# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from django import forms
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta
from .models import Document, Note, Release, InspectionRequest, Inspection
from .models import BreechType, Enforcement, WorkoutMeeting, BreechStatus
from applications.models import Application
from property_inventory.models import take_back
from closings.models import closing
import csv
from django.http import HttpResponse
from django.core import management
from django.core.management.commands import loaddata
from django.shortcuts import render
from django.http import HttpResponseRedirect

from utils.utils import batch_update_view
def custom_batch_editing__admin_action(self, request, queryset):
    return batch_update_view(
        model_admin=self,
        request=request,
        queryset=queryset,
        field_names=['showing_scheduled','status','notes'],
    )
custom_batch_editing__admin_action.short_description = "Batch Update"



def add_note(modeladmin, request, queryset):
    if request.method == 'POST':
        print("HERE")
        print(request.POST)
        if 'form-post' in request.POST:
            print("THERE")
            for p in queryset:
                print('Here on {}'.format(p,))
                p.notes.create(text=request.POST.get('note_text'))
                #return HttpResponseRedirect(request.get_full_path())
                return HttpResponseRedirect(request.get_full_path())

        return render(
            request,
            'admin/batch_add_note_object.html',
        )
#        p.notes.create(text='Sample text')





class NoteInline(GenericStackedInline):
    model = Note
    fields = ('text', 'created', 'modified', )
    readonly_fields=('created', 'modified',)
    extra = 0
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(NoteInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'text':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield

class DocumentInline(GenericTabularInline):
    model = Document
    fields = ('file', 'file_purpose',)
    extra = 0

class DocumentAdmin(admin.ModelAdmin):
    search_fields = ('file_purpose',)


class ReleaseInlineAdmin(admin.TabularInline):
    model = Release
    extra = 0
    fields = ('instrument_number', 'recorded_document','date_recorded',)
    #can_delete = False
    show_change_link = True

class InspectionAdmin(admin.ModelAdmin):
    inlines = [NoteInline, DocumentInline, ReleaseInlineAdmin]
    raw_id_fields = ('user',)
    readonly_fields = ('closing_link','application_link')
    search_fields = ('request__Property__streetAddress','request__Property__parcel')


    def closing_link(self, obj):
        tb_link = 'None linked'
        if obj.request.Application is not None:
            try:
                url = reverse("admin:closings_closing_change", args=(closing.objects.filter(application=obj.request.Application).first().id,) )
            except NoReverseMatch:
                pass
            else:
                tb_link = '<a target="_blank" href="{}">{}</a>'.format(
                    url,
                    obj.request.Application.closing_set.first().date_time.strftime('%m/%d/%Y')
                )
        return mark_safe(tb_link)

    def application_link(self, obj):
        tb_link = 'None linked'
        if obj.request.Application is not None:
            url = reverse("admin:applications_application_change", args=(obj.request.Application.id,) )
            tb_link = '<a target="_blank" href="{}">{}</a>'.format(
                url,
                obj.request.Application
            )
        return mark_safe(tb_link)


class InspectionRequestStageFilter(admin.SimpleListFilter):
    title = 'request stage'
    parameter_name = 'stage'

    def lookups(self, request, model_admin):
        return (
            ('new', 'No inspection'),
            ('inspection_passed', 'Inspection passed, no release'),
            ('released', 'Completed and released'),
            ('inspected_unreleased','Inspected, not released'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'new':
            return queryset.filter(inspection__isnull=True).distinct()
        if self.value() == 'inspection_passed':
            return queryset.filter(inspection__pass_outcome__exact=True).filter(inspection__release__isnull=True).distinct()
        if self.value() == 'released':
            return queryset.filter(inspection__release__isnull=False).distinct()
        if self.value() == 'inspected_unreleased':
            return queryset.filter(inspection__isnull=False).filter(inspection__release__isnull=True).distinct()
        return queryset



class PropertyOwnerFilter(admin.SimpleListFilter):
    title = 'property owner'
    parameter_name = 'owner'
    def lookups(self, request, model_admin):
        return (
            ('true','Renew'),
            ('false', 'DMD'),
            )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(Property__renew_owned__exact=True)
        if self.value() == 'false':
            return queryset.filter(Property__renew_owned__exact=False)


class InspectionRequestAdmin(admin.ModelAdmin):
    inlines = [NoteInline, DocumentInline]
    raw_id_fields = ('user','Application')
    readonly_fields = ('inspection_status','get_contact_info_on_file', 'get_application_and_property_type', 'get_property_owner')
    list_display = ('Property', 'get_application_or_applicant', 'created', 'inspection_status',)
    search_fields = ('Property__parcel', 'Property__streetAddress', 'Application__Property__parcel', 'Application__Property__streetAddress', 'Application__user__last_name', 'Application__user__first_name', 'Application__organization__name')
    list_filter = (InspectionRequestStageFilter,PropertyOwnerFilter)


    ## release exists field
    def inspection_status(self, obj):
        insp = Inspection.objects.filter(request=obj).first()
        result = '-'
        url = ''
        if insp is None:
            result = 'add inspection'
            url = '{}{}{}'.format(reverse("admin:project_agreement_management_inspection_add"), '?request=',obj.id)
        else:
            result = 'add release'
            url = '{}{}{}'.format(reverse("admin:project_agreement_management_release_add"),'?Inspection=',insp.id)
            rel = Release.objects.filter(Inspection=insp).first()
            if rel != None:
#                return mark_safe('done')
                result = 'done'
                url = reverse("admin:project_agreement_management_release_change", args=(rel.id,) )
        il = '<a target="_blank" href="{}">{}</a>'.format(
            url,
            result,
        )
        return mark_safe(il)

    def get_application_and_property_type(self, obj):
        application_type = ''
        property_type = ''
        if obj.Application is not None:
            application_type = obj.Application.get_application_type_display()
        if obj.Property is not None:
            property_type = obj.Property.structureType
        return 'Application Type: {} Property Type: {}'.format(application_type, property_type)

    def get_property_owner(self, obj):
        if obj.Property is not None:
            if obj.Property.renew_owned == True:
                return 'Renew owned'
            else:
                return 'DMD owned'

    def get_application_or_applicant(self, obj):
        if obj.Application is not None:
            url = reverse("admin:applications_application_change", args=(obj.Application.id,) )
            return mark_safe('<a target="_blank" href="{}">{}</a>'.format(url, obj.Application) )
        else:
            return obj.Property.applicant


    def get_contact_info_on_file(self, obj):
        if obj.Application is not None:
            name = '{} {}'.format(obj.Application.user.first_name, obj.Application.user.last_name)
            email = obj.Application.user.email
            phone = obj.Application.user.profile.phone_number
            return '{} {} {}'.format(name, email, phone)
        return 'nothing on file'



    def export_as_csv_custom_action(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format('Inspect-Request')
        writer = csv.writer(response)

        field_names = [
            'Street Address',
            'Parcel',
            'Legal Description',
            'Transaction Date',
            'Instrument Number',
            ]

        writer.writerow(field_names)
        for obj in queryset:
            prop = None
            app = None
            if obj.Application is not None:
                prop = obj.Application.Property
                app = obj.Application
            elif obj.Property is not None:
                prop = obj.Property
                app = obj.Property.buyer_application

            try:
                clo = closing.objects.get(application=app).filter().last()
                closing_date = clo.date_time.strftime('%x')
                instrument_number = clo.recorded_city_deed_instrument_number
            except closing.DoesNotExist:
                closing_date = '-'
                instrument_number = '-'
            data = [
                prop.streetAddress,
                prop.parcel,
                prop.short_legal_description,
                closing_date,
                instrument_number,
                ]
            row = writer.writerow(data)

        return response
    export_as_csv_custom_action.short_description = 'Export as CSV for Release Creation'

class EnforcementInlineAdmin(admin.TabularInline):
    model = Enforcement.meeting.through
    extra = 0
    can_delete = False
    show_change_link = True

class BreechTypesInlineAdmin(admin.TabularInline):
    model = Enforcement.breech_types.through
    extra = 0
    show_change_link = True
    can_delete = False


class ApplicationTypeFilter(admin.SimpleListFilter):
    title = 'Application Type'
    parameter_name = 'application_type'
    def lookups(self, request, model_admin):
        return (
            ('1','Homestead'),
            ('2', 'Standard'),
            ('3', 'Sidelot'),
            ('4', 'Vacant Lot'),
            ('5', 'Future Development Lot'),
            ('no-development-commitment', 'No development commitment'),
            )

    def queryset(self, request, queryset):
        if self.value() == 'no-development-commitment':
            return queryset.filter(enforcement__Application__application_type__in=[3,4,5])
        elif self.value() is not None:
            return queryset.filter(enforcement__Application__application_type__exact=int(self.value()))
        else:
             return queryset

class StructureTypeFilter(admin.SimpleListFilter):
    title = 'Structure Type'
    parameter_name = 'structure_type'
    def lookups(self, request, model_admin):
        return (
            ('structure','Structure'),
            ('lot', 'Lot'),
            )

    def queryset(self, request, queryset):
        if self.value() == 'structure':
            return queryset.filter(enforcement__Application__Property__structureType__in=['Residential Dwelling', 'Mixed Use Commercial'])
        elif self.value() == 'lot':
            return queryset.filter(enforcement__Application__Property__structureType__in=['Vacant Lot', 'Detached Garage/Boat House'])
        else:
             return queryset

class OwnerFilter(admin.SimpleListFilter):
    title = 'Owner'
    parameter_name = 'owner'
    def lookups(self, request, model_admin):
        return (
            ('dmd','DMD'),
            ('renew', 'Renew'),
            )

    def queryset(self, request, queryset):
        if self.value() == 'dmd':
            return queryset.filter(enforcement__Application__Property__renew_owned=False)
        elif self.value() == 'renew':
            return queryset.filter(enforcement__Application__Property__renew_owned=True)
        else:
             return queryset


class AgeFilter(admin.SimpleListFilter):
    title = 'Years since Sale'
    parameter_name = 'age'
    def lookups(self, request, model_admin):
        return (
            ('0-1','0-1'),
            ('1-2', '1-2'),
            ('2-4', '2-4'),
            ('4-5', '4-5'),
            ('5', '5+'),
            ('invalid', 'Missing Data'),
            )

    def queryset(self, request, queryset):
        if self.value() == 'invalid':
            return queryset.filter(enforcement__Application__closing_set__isnull=True)
        if self.value() == '5':
            return queryset.filter(enforcement__Application__closing_set__date_time__lte=timezone.now()-timezone.timedelta(days=365*5))
        elif self.value() == '4-5':
            return queryset.filter(
                enforcement__Application__closing_set__date_time__lte=timezone.now()-timezone.timedelta(days=365*4)).filter(
                enforcement__Application__closing_set__date_time__gt=timezone.now()-timezone.timedelta(days=365*5)
            )
        elif self.value() == '2-4':
            return queryset.filter(
                enforcement__Application__closing_set__date_time__lte=timezone.now()-timezone.timedelta(days=365*2)).filter(
                enforcement__Application__closing_set__date_time__gt=timezone.now()-timezone.timedelta(days=365*4)
            )
        elif self.value() == '1-2':
            return queryset.filter(
                enforcement__Application__closing_set__date_time__lte=timezone.now()-timezone.timedelta(days=365*2)).filter(
                enforcement__Application__closing_set__date_time__gt=timezone.now()-timezone.timedelta(days=365*1)
            )
        elif self.value() == '0-1':
            return queryset.filter(enforcement__Application__closing_set__date_time__gte=timezone.now()-timezone.timedelta(days=365*1))
        else:
             return queryset


class BreechStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ('enforcement',)
    inlines = [NoteInline,DocumentInline]
    list_display = ('enforcement','breech', 'status', 'sale_date')
    list_filter = ('status', 'breech', ApplicationTypeFilter, StructureTypeFilter,AgeFilter,OwnerFilter)
    search_fields = (
        'enforcement__Property__parcel',
        'enforcement__Property__streetAddress',
        'enforcement__Application__user__first_name',
        'enforcement__Application__user__last_name',
        'enforcement__Application__organization__name',
        'enforcement__Application__user__email',
        )
    actions = ['export_as_csv_custom_action', 'add_bulk_breach', 'run_management_command']
    change_list_template = 'admin/project_agreement_management/breech_status_change_list.html' # definitely not 'admin/change_list.html'

    def sale_date(self,obj):
        if obj.enforcement is not None:
            if obj.enforcement.Application is not None:
                if obj.enforcement.Application.closing_set.count() > 0:
                    return obj.enforcement.Application.closing_set.first().date_time
        return ''

    def add_bulk_breach(self, request, queryset):
      command_output = ''
      command_output2 = ''
      returned_result = ''
      if 'apply' in request.POST:
          print(request.POST)
          parcels = request.POST.get('parcels').replace('\n', ' ').replace('\r', ' ').strip()
          breach_type = request.POST.get('breach_type')
          if request.POST.get('comprehensive') == 'on':
              management.call_command('add_bulk_breach', '--comprehensive', parcels, breach_type=breach_type, stdout=command_output)
          else:
              management.call_command('add_bulk_breach', parcels, breach_type=breach_type,  stdout=command_output)

          self.message_user(request,
                "Add Breaches Completed. {} {} {}.".format(command_output,command_output2,returned_result))
          #print('{} {} {}'.format(command_output,command_output2,returned_result))
          return HttpResponseRedirect(request.get_full_path())

      return render(request,
            'admin/project_agreement_management/add_bulk_breach.html',
            context={
                'objects':queryset,
                'breach_types': BreechType.objects.all(),
            }
            )
    def run_management_command(self, request, queryset):
        # Run either add_missing_annual_report, add_two_year_breaches or close_released_breaches
        command_output = ''
        command = ''
        if 'apply' in request.POST:
            if request.POST.get('command') == 'Create missing annual report breaches':
                command = 'add_missing_annual_report'
            if request.POST.get('command') == 'Create two years past sale breaches':
                command = 'add_two_year_breaches'
            if request.POST.get('command') == 'Close breaches on released properties':
                command = 'close_released_breaches'
            if command != '':
                management.call_command(command, stdout=command_output)
                self.message_user(request,
                    "Command Completed. {} {} {}.".format(command_output,))
            else:
                self.message_user(request, 'Command not run.')
          return HttpResponseRedirect(request.get_full_path())

        return render(request,
            'admin/project_agreement_management/run_management_command.html',
            context={
                'objects':queryset,
            }
            )

    def export_as_csv_custom_action(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format('Breech-enforcement')
        writer = csv.writer(response)

        field_names = [
            'Street Address',
            'Parcel',
            'Renew Owned',
            'Structure Type',
            'Application Type',
            'Sale Date',
            'Last Annual Report Submitted',
            'Buyer Name',
            'Organization Name',
            'Buyer email',
            'Buyer phone',
            'Buyer mailing street address',
            'Buyer mailing city',
            'Buyer mailing state',
            'Buyer mailing postal code',
            'Breech Type',
            'Breech opened date',
            'Breech status',
            'Breech closed date',
            'Notes',
            ]

        writer.writerow(field_names)
        for obj in queryset:
            if obj.enforcement.Application is not None:
                from annual_report_form.models import annual_report
                annual_report = annual_report.objects.filter(Property=obj.enforcement.Application.Property).last()
                if annual_report is not None:
                    annual_report_date = annual_report.created
                else:
                    annual_report_date = '-'
                data = [
                    obj.enforcement.Property.streetAddress,
                    obj.enforcement.Property.parcel,
                    obj.enforcement.Property.renew_owned,
                    obj.enforcement.Property.structureType,
                    obj.enforcement.Application.get_application_type_display(),
                    obj.enforcement.Property.status[5:], # sale date
                    annual_report_date,
                    '{} {}'.format(obj.enforcement.Application.user.first_name, obj.enforcement.Application.user.last_name),
                    obj.enforcement.Application.organization,
                    obj.enforcement.Application.user.email,
                    obj.enforcement.Application.user.profile.phone_number,
                    '{} {} {}'.format(obj.enforcement.Application.user.profile.mailing_address_line1, obj.enforcement.Application.user.profile.mailing_address_line2, obj.enforcement.Application.user.profile.mailing_address_line3),
                    obj.enforcement.Application.user.profile.mailing_address_city,
                    obj.enforcement.Application.user.profile.mailing_address_state,
                    obj.enforcement.Application.user.profile.mailing_address_zip,
                    obj.breech.name,
                    obj.date_created,
                    obj.status,
                    obj.date_resolved,
                    ' - '.join(['{} - {}.'.format(n.text, n.modified.strftime('%x')) for n in obj.notes.all()]),
                ]
            else:
                from annual_report_form.models import annual_report
                annual_report = annual_report.objects.filter(Property=obj.enforcement.Property).last()
                if annual_report is not None:
                    annual_report_date = annual_report.created
                else:
                    annual_report_date = '-'
                data = [
                    obj.enforcement.Property.streetAddress,
                    obj.enforcement.Property.parcel,
                    obj.enforcement.Property.renew_owned,
                    obj.enforcement.Property.structureType,
                    'Legacy application not in system',
                    obj.enforcement.Property.status[5:],
                    annual_report_date, # no annual report lookup
                    obj.enforcement.Property.applicant,
                    '', # org
                    '', # email
                    '', # phone
                    '', # mailing address
                    '', # mailing city
                    '', # mailing state
                    '', # mailing zip
                    obj.breech.name,
                    obj.date_created,
                    obj.status,
                    obj.date_resolved,
                    ' - '.join(['{} - {}.'.format(n.text, n.modified.strftime('%x')) for n in obj.notes.all()]),
                ]

            row = writer.writerow(data)

        return response
    export_as_csv_custom_action.short_description = 'Export as CSV'

class EnforcementAdmin(admin.ModelAdmin):
    inlines = [NoteInline,BreechTypesInlineAdmin]
    readonly_fields=('user','current_property_status', 'closing_info', 'find_takeback', 'open_breech_count', 'person', 'contact_info', 'last_sale_date', 'open_breech_types')
    #fields = ('breech_types',)
    list_filter = ('level_of_concern','open_breech_count')
    list_display = ('Property', 'person', 'last_sale_date', 'created', 'modified', 'level_of_concern', 'open_breech_count', 'open_breech_types')
    search_fields = ('Property__parcel', 'Property__streetAddress', 'Application__user__first_name','Application__user__last_name', 'Application__organization__name')
    actions = ['export_as_csv_custom_action',]

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(EnforcementAdmin, self).formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == 'Application':
            formfield.queryset = Application.objects.none()
            # terrible? way to get object id if we are editting an existing object
            try:
                # http://stackoverflow.com/a/18318866/2731298 -- changed -1 to -2 to grab second to last argument in url since changed in django 1.11 I think
                obj_id = int([i for i in str(kwargs['request'].path).split('/') if i][-2])
            except ValueError:
                obj_id = None

            # If we are edding an existing Enforcement, restrict application choices if property selected
            if obj_id != None:
                obj = Enforcement.objects.get(id=obj_id)
                if obj.Property is not None: # and obj.Application is None:
                    formfield.queryset = Application.objects.filter(Property__exact=obj.Property)
        return formfield


    def person(self, obj):
        if obj.Application is not None:
            name = '{} {}'.format(obj.Application.user.first_name, obj.Application.user.last_name)
            if obj.Application.organization is not None:
                name = '{} ({})'.format(name, obj.Application.organization)
        else:
            name = obj.owner
        return name

    def contact_info(self, obj):
        if obj.Application is not None:
            email = obj.Application.user.email
            phone = obj.Application.user.profile.phone_number
            return '{} {}'.format(email, phone)
        return ''


    def last_sale_date(self, obj):
        if 'Sold' in obj.Property.status:
            return obj.Property.status[5:]
        return '-'


    def save_model(self, request, obj, form, change):
    #    if obj is None and obj.user is None:
    #        obj.user = request.user
        super(EnforcementAdmin, self).save_model(request, obj, form, change)

    def current_property_status(self, obj):
        if obj is not None and obj.Property is not None:
            return obj.Property.status
        else:
            return '-'


    def closing_info(self, obj):
        if obj is not None and obj.Application is not None:
            try:
                url = reverse("admin:closings_closing_change", args=(obj.Application.closing_set.first().id,) )
            except NoReverseMatch:
                pass
            else:
                closing_link = '<a target="_blank" href="{}">{}</a>'.format(
                    url,
                    obj.Application.closing_set.first().date_time
                )
                return mark_safe(closing_link)
        return 'No closing linked to application selected'

    def find_takeback(self, obj):
        if obj is not None and obj.Application is not None:
            try:
                url = reverse("admin:property_inventory_take_back_change", args=(take_back.objects.get(application=obj.Application).id,) )
            except NoReverseMatch:
                print('exceiption')
            else:
                tb_link = '<a target="_blank" href="{}">{}</a>'.format(
                    url,
                    obj.Application.closing_set.first().date_time
                )
                return mark_safe(tb_link)
        return 'No take back linked to application selected'

    def open_breech_types(self, obj):
        values = ''
        for b in obj.breech_types.filter(breechstatus__status=BreechStatus.OPEN):
            values = '{}{}/'.format(values, b)
        return values


    def export_as_csv_custom_action(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format('Breech-enforcement')
        writer = csv.writer(response)

        field_names = [
            'Street Address',
            'Parcel',
            'Structure Type',
            'Application Type',
            'Sale Date',
            'Buyer Name',
            'Organization Name',
            'Buyer email',
            'Buyer phone',
            'Buyer mailing street address',
            'Buyer mailing city',
            'Buyer mailing state',
            'Buyer mailing postal code',
            'Open Breaches',
            ]

        writer.writerow(field_names)
        for obj in queryset:
            breaches = ''

            for b in BreechStatus.objects.filter(enforcement=obj, status=False):
                    breaches = '{}\n{}'.format(breaches, b)
            if obj.Application is not None:
                from annual_report_form.models import annual_report
                annual_report = annual_report.objects.filter(Property=obj.Application.Property).last()
                if annual_report is not None:
                    annual_report_date = annual_report.created
                else:
                    annual_report_date = '-'
                data = [
                    obj.Property.streetAddress,
                    obj.Property.parcel,
                    obj.Property.structureType,
                    obj.Application.get_application_type_display(),
                    obj.Property.status[5:], # sale date
                    '{} {}'.format(obj.Application.user.first_name, obj.Application.user.last_name),
                    obj.Application.organization,
                    obj.Application.user.email,
                    obj.Application.user.profile.phone_number,
                    '{} {} {}'.format(obj.Application.user.profile.mailing_address_line1, obj.Application.user.profile.mailing_address_line2, obj.Application.user.profile.mailing_address_line3),
                    obj.Application.user.profile.mailing_address_city,
                    obj.Application.user.profile.mailing_address_state,
                    obj.Application.user.profile.mailing_address_zip,
                    breaches,
                ]
            else:
                from annual_report_form.models import annual_report
                annual_report = annual_report.objects.filter(Property=obj.enforcement.Property).last()
                if annual_report is not None:
                    annual_report_date = annual_report.created
                else:
                    annual_report_date = '-'
                data = [
                    obj.enforcement.Property.streetAddress,
                    obj.enforcement.Property.parcel,
                    obj.enforcement.Property.structureType,
                    'Legacy application not in system',
                    obj.enforcement.Property.status[5:],
                    obj.enforcement.Property.applicant,
                    '', # org
                    '', # email
                    '', # phone
                    '', # mailing address
                    '', # mailing city
                    '', # mailing state
                    '', # mailing zip
                    breaches,
                ]

            row = writer.writerow(data)

        return response
    export_as_csv_custom_action.short_description = 'Export as CSV'



class WorkoutMeetingAdmin(admin.ModelAdmin):
    inlines = [EnforcementInlineAdmin,]




class ReleaseAdmin(admin.ModelAdmin):
    inlines = [NoteInline,]
    raw_id_fields = ('Property','Application')
    search_fields = (
        'Property__streetAddress',
        'Property__parcel',
        'Application__Property__streetAddress',
        'Application__Property__parcel',
        'Inspection__request__Property__streetAddress',
        'Inspection__request__Property__parcel',
        'Inspection__request__Application__Property__streetAddress',
        'Inspection__request__Application__Property__parcel',

    )
    list_display = ('created', 'Inspection', 'Property', 'Application', 'owner', 'date_recorded')


admin.site.register(Document, DocumentAdmin)
admin.site.register(Note)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(InspectionRequest, InspectionRequestAdmin)
admin.site.register(Inspection, InspectionAdmin)
admin.site.register(BreechType)
admin.site.register(BreechStatus, BreechStatusAdmin)
admin.site.register(Enforcement, EnforcementAdmin)
admin.site.register(WorkoutMeeting,WorkoutMeetingAdmin)
