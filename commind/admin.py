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
    fieldsets = (
        (None, {
            'fields': (
                        ('user',),
                        ('created', 'modified', 'submitted_timestamp'),
                        ('Properties',),#  'property_type','property_status','property_vacant_lot','property_sidelot'),
                        'status',
                        )
        }),
        ('Qualifying Questions', {
            'fields': (
                ('conflict_board_rc', 'conflict_board_rc_name', 'conflict_city', 'conflict_city_name',),
                'active_citations', 'prior_tax_foreclosure', 'tax_status_of_properties_owned',)
        }),
        ('Entity', {
            'fields': ('entity',)

        }),
        ('Sources of Finacing', {
            'fields': ('source_of_financing',)
        }),
        ('Staff fields', {
            'fields': ('staff_summary','neighborhood_notification_details','neighborhood_notification_feedback','staff_sow_total',('staff_pof_total', 'staff_pof_description'),('staff_recommendation','staff_recommendation_notes','staff_points_to_consider','frozen', ))

        })

    )

admin.site.register(Property,PropertyAdmin)
admin.site.register(Note)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Document)
admin.site.register(Photo)
admin.site.register(Entity, EntityAdmin)
