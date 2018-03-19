from django.contrib import admin
from .models import ConditionReport, Room
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django import forms

class RoomInline(admin.StackedInline):
    model = Room
    #fields = ('date_purchased', 'date_expiring', 'amount_paid', )
    #readonly_fields=('closing',)
    extra = 3

class ConditionReportAdmin(admin.ModelAdmin):
    inlines = [RoomInline,]
    readonly_fields = ('upload_photo_page', 'scope_download', 'pic_download')

    def upload_photo_page(self, obj):
        upload_photo_page_link = '<a target="_blank" href="{}">{}</a>'.format(
            reverse("admin_add_photos"), "Add photos page")
        return mark_safe(upload_photo_page_link)

    def scope_download(self, obj):
        if obj.id is None:
            return '<none>'
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("condition_report_file", kwargs={'id':obj.id, 'file_type':'scope'}),
                "Download"
            ))

    def pic_download(self, obj):
        if obj.id is None:
            return '<none>'
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("condition_report_file", kwargs={'id':obj.id, 'file_type':'photo'}),
                "Download"
            ))

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ConditionReportAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if 'notes' in db_field.name:
            formfield.widget = forms.Textarea(attrs={'rows':4})
        return formfield


    fieldsets = (
        ('Property', {
            'fields':
                (
                    'Property',
                    'general_property_notes',
                    ('picture','pic_download'),
                    'upload_photo_page',
                    ('scope_of_work', 'scope_download',),
                )
            }
        ),
        ('Roof', {
            'fields':
                (
                    'roof_shingles',
                    'roof_shingles_notes',
                    'roof_framing',
                    'roof_framing_notes',
                    'roof_gutters',
                    'roof_gutters_notes'
                )
            }
        ),
        ('Foundation', {
            'fields':
                (
                    'foundation_slab',
                    'foundation_slab_notes',
                    'foundation_crawl',
                    'foundation_crawl_notes'
                )
            }
        ),
        ('Exterior Siding', {
            'fields':
                (
                'exterior_siding_brick',
                'exterior_siding_brick_notes',
                'exterior_siding_wood',
                'exterior_siding_wood_notes',
                'exterior_siding_vinyl',
                'exterior_siding_vinyl_notes',
                'exterior_siding_other',
                'exterior_siding_other_notes'
                )
            }
        ),
        ('Windows/Doors/Kitchen', {
            'fields':
                (
                'windows',
                'windows_notes',
                'doors',
                'doors_notes',
                'kitchen_cabinets',
                'kitchen_cabinets_notes',
                )
            }
        ),
        ('Electrical', {
            'fields':
                (
                'electrical_knob_tube_cloth',
                'electrical_knob_tube_cloth_notes',
                'electrical_standard',
                'electrical_standard_notes',
                )
            }
        ),
        ('Plumbing', {
            'fields':
                (
                'plumbing_metal',
                'plumbing_metal_notes',
                'plumbing_plastic',
                'plumbing_plastic_notes',
                )
            }
        ),
        ('Interior Walls', {
            'fields':
                (
                'walls_drywall',
                'walls_drywall_notes',
                'walls_lathe_plaster',
                'walls_lathe_plaster_notes'
                )
            }
        ),
        ('HVAC', {
            'fields':
                (
                'hvac_furance',
                'hvac_furance_notes',
                'hvac_air_conditioner',
                'hvac_air_conditioner_notes',
                'hvac_duct_work',
                'hvac_duct_work_notes',
                )
            }
        ),

        ('Lot Features', {
            'fields':
                (
                'garage',
                'garage_notes',
                'landscaping',
                'landscaping_notes',
                'fencing',
                'fencing_notes',
                )
            }
        ),


    )

admin.site.register(ConditionReport, ConditionReportAdmin)
# Register your models here.
