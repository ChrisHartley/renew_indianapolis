# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Property, Note, Application, Document, Entity, Person, Photo
from .forms import NoteInlineForm
from django.forms.widgets import Textarea
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

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
    readonly_fields = ('created', 'modified', 'submitted_timestamp', 'generate_application_summary')
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
                    'conflict_renew_city',
                    'conflict_renew_city_name',
                ),
                'active_citations',
                'prior_tax_foreclosure',
                'tax_status_of_properties_owned',
                'existing_liens',
                )
        }),
        ('Entity', {
            'fields': (
                'entity',
                'entity_affiliates',
            )

        }),
        ('Other Questions', {
            'fields': (
                'applicant_work_character',
                'applicant_experience',
                'applicant_brownfield_experience',
                'applicant_joint_venture',
                'applicant_partnerships',
                'applicant_skills_environmental_remediation',
                'applicant_skills_brownfields',
                'applicant_skills_commercial_real_estate_development',
                'applicant_skills_entitlement_process',
                'applicant_skills_incentives',
                'applicant_skills_other',
                'applicant_skills_environmental_remediation_boolean',
                'applicant_skills_brownfields_boolean',
                'applicant_skills_commercial_real_estate_development_boolean',
                'applicant_skills_entitlement_process_boolean',
                'applicant_skills_incentives_boolean',
                'applicant_skills_other_boolean',
            )
        }),
        ('Project Description', {
            'fields': (
                'applicant_offer_price',
                'proposed_end_use',
                'project_type',
                'allignment_with_current_plans',
                'allignment_with_current_plans_details',
                'stakeholders_contacted',
                'stakeholders_contacted_details',
                'total_number_of_jobs',
                'total_annual_new_salaries',
                'blended_hourly_wage_rate',
                'hired_participant',
                'low_mod_daycare',
                'low_mod_transportation_support',
                'youth_employment_opportunity',
                'neighborhood_hiring_opportunity',
                'subbaccalaureate_training_opportunity',
                'arts_consideration',
                'arts_consideration_explanation',
                'minority_owned_business_question',
                'minority_owned_business_question_detail',
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
                ),
                (
                    'generate_application_summary',
                )
            )

        })

    )

    def generate_application_summary(self, obj):
        if obj.id is None:
            return '-'
        return mark_safe('<a target="_blank" href="{}">{}</a>'.format(
            reverse("commind_application_detail", kwargs={'pk':obj.id,}),
                "Summary"
            ))

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ApplicationAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.max_length > 255:
            formfield.widget = Textarea(attrs=formfield.widget.attrs)
        return formfield

admin.site.register(Property,PropertyAdmin)
admin.site.register(Note)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Document)
admin.site.register(Photo)
admin.site.register(Entity, EntityAdmin)
