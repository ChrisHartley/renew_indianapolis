# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from django import forms
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.safestring import mark_safe

from .models import Document, Note, Release, InspectionRequest, Inspection
from .models import BreechType, Enforcement, WorkoutMeeting, BreechStatus
from applications.models import Application
from property_inventory.models import take_back
from closings.models import closing

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

class InspectionAdmin(admin.ModelAdmin):
    inlines = [NoteInline, DocumentInline]
    raw_id_fields = ('user',)
    readonly_fields = ('closing_link',)


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

class InspectionRequestAdmin(admin.ModelAdmin):
    inlines = [NoteInline, DocumentInline]
    raw_id_fields = ('user','Application')
    readonly_fields = ('inspection_link', 'inspection_exists')
    list_display = ('Property', 'Application', 'inspection_exists')

    def inspection_exists(self, obj):
        return Inspection.objects.filter(request=obj).count() > 0
    inspection_exists.boolean = True

    def inspection_link(self, obj):
        tb_link = ''
        url = ''
        try:
            url = reverse("admin:project_agreement_management_inspection_change", args=(Inspection.objects.get(request=obj).id,) )
        except NoReverseMatch:
            print('exceiption')
        else:
            tb_link = '<a target="_blank" href="{}">{}</a>'.format(
                url,
                'Inspection'
            )
        return mark_safe(tb_link)


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


class BreechStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ('enforcement',)
    inlines = [NoteInline,DocumentInline]


class EnforcementAdmin(admin.ModelAdmin):
    inlines = [NoteInline,BreechTypesInlineAdmin]
    readonly_fields=('user','current_property_status', 'closing_info', 'find_takeback', 'open_breech_count', 'person', 'contact_info', 'last_sale_date')
    #fields = ('breech_types',)
    list_filter = ('level_of_concern','open_breech_count')
    list_display = ('Property', 'person', 'last_sale_date', 'created', 'modified', 'level_of_concern', 'open_breech_count')
    search_fields = ('Property__parcel', 'Property__streetAddress', 'Application__user__first_name','Application__user__last_name', 'Application__organization__name')

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

class WorkoutMeetingAdmin(admin.ModelAdmin):
    inlines = [EnforcementInlineAdmin,]

class ReleaseAdmin(admin.ModelAdmin):
    inlines = [NoteInline,]

admin.site.register(Document)
admin.site.register(Note)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(InspectionRequest, InspectionRequestAdmin)
admin.site.register(Inspection, InspectionAdmin)
admin.site.register(BreechType)
admin.site.register(BreechStatus, BreechStatusAdmin)
admin.site.register(Enforcement, EnforcementAdmin)
admin.site.register(WorkoutMeeting,WorkoutMeetingAdmin)
