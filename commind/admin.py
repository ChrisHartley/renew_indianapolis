# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Property, Note, Application, Document, Entity, Person, Photo
from .forms import NoteInlineForm

class PersonInline(admin.TabularInline):
    model = Person
#    fields = ('file_purpose', 'file_purpose_other_explanation', 'supporting_document', 'file_download', 'send_with_neighborhood_notification', 'user','application')
#    readonly_fields = ('file_download',)
    extra = 1

# class UploadedFileInline(admin.TabularInline):
#     model = UploadedFile
#     fields = ('file_purpose', 'file_purpose_other_explanation', 'supporting_document', 'file_download', 'send_with_neighborhood_notification', 'user','application')
#     readonly_fields = ('file_download',)
#     extra = 1

class EntityAdmin(admin.OSMGeoAdmin):
    model = Entity
    inlines = [ PersonInline, ]
    extra = 0

class EntityInline(GenericTabularInline):
    model = Entity
    #inlines = [ PersonInline, ]
    extra = 0

class DocumentInline(GenericTabularInline):
    model = Document
    extra = 2
    def get_queryset(self, request):
        qs = super(DocumentInline, self).get_queryset(request)
        return qs.filter(photo__isnull=True)

class PhotoInline(GenericTabularInline):
    model = Photo
    extra = 2

class NotesInline(GenericTabularInline):
    model = Note
    extra = 0
    form = NoteInlineForm

class PropertyAdmin(admin.OSMGeoAdmin):
    inlines = [DocumentInline, PhotoInline, NotesInline]

class ApplicationAdmin(admin.OSMGeoAdmin):
    inlines = [DocumentInline, NotesInline, ]#EntityInline]
    readonly_fields = ('created', 'modified', 'submitted_timestamp')
    list_filter = ('status',)
    fieldsets = (
        (None, {
            'fields': (
                        ('user',),
                        ('created', 'modified', 'submitted_timestamp'),
                        ('Properties','Property'),#  'property_type','property_status','property_vacant_lot','property_sidelot'),
                        'status',
                        )
        }),
        ('Qualifying Questions', {
            'fields': (
                (
                    'conflict_board_rc',
                    'conflict_board_rc_name',
                    'conflict_city',
                    'conflict_city_name',
                ),
                'active_citations',
                'prior_tax_foreclosure',
                'tax_status_of_properties_owned',)
        }),
        ('Entity', {
            'fields': (
                'entity',
            )

        }),
        ('Other Questions', {
            'fields': (
                'applicant_work_character',
                'applicant_experience',
                'applicant_brownfield_experience',
                'applicant_joint_venture',
                'applicant_partnerships',
            )
        }),
        ('Project Description', {
            'fields': (
                'applicant_offer_price',
                'proposed_end_use',

            )
        }),
        ('Staff fields', {
            'fields': (
                'staff_summary',
                'neighborhood_notification_details',
                'neighborhood_notification_feedback',
                'staff_sow_total',
                (
                    'staff_pof_total',
                    'staff_pof_description'
                ),
                (
                    'staff_recommendation',
                    'staff_recommendation_notes',
                    'staff_points_to_consider',
                    'frozen',
                )
            )

        })

    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ApplicationAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        print db_field.__dict__
        if db_field.name == 'notes':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield

admin.site.register(Property,PropertyAdmin)
admin.site.register(Note)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Document)
admin.site.register(Photo)
admin.site.register(Entity, EntityAdmin)
