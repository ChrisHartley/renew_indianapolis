from django.contrib import admin
from .models import ConditionReport, Room, ConditionReportProxy
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms

class RoomInline(admin.StackedInline):
    model = Room
    #fields = ('date_purchased', 'date_expiring', 'amount_paid', )
    #readonly_fields=('closing',)
    extra = 3

class ConditionReportAdmin(admin.ModelAdmin):
    inlines = [RoomInline,]
    readonly_fields = ('upload_photo_page', 'scope_download', 'pic_download', 'get_condition_avg', 'timestamp', 'modified')
    search_fields = ('Property__parcel', 'Property__streetAddress')


    def get_condition_avg(self, obj):
        return obj.condition_avg


    def upload_photo_page(self, obj):
        if obj.Property_ncst is not None:
            upload_photo_page_link = '<a target="_blank" href="{}?Property_ncst={}">{}</a>'.format(
                reverse("admin_add_photos"), obj.Property_ncst.pk, "Add photos page")
        elif obj.Property_surplus is not None:
            upload_photo_page_link = '<a target="_blank" href="{}?Property_surplus={}">{}</a>'.format(
                reverse("admin_add_photos"), obj.Property_surplus.pk, "Add photos page")
        else:
            upload_photo_page_link = '<a target="_blank" href="{}?Property={}">{}</a>'.format(
                reverse("admin_add_photos"), obj.Property.pk, "Add photos page")

        return mark_safe(upload_photo_page_link)

    def scope_download(self, obj):
        if obj.id is None:
            return '<none>'
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("send_class_file", kwargs={'app_name': 'property_condition', 'class_name': 'ConditionReport', 'pk':obj.id, 'field_name':'scope_of_work'}),
                "Download"
            ))

    def pic_download(self, obj):
        if obj.id is None:
            return '<none>'
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("send_class_file", kwargs={'app_name': 'property_condition', 'class_name': 'ConditionReport', 'pk':obj.id, 'field_name':'picture'}),
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
                    ('Property', 'Property_ncst', 'Property_surplus', 'get_condition_avg' ),
                    'general_property_notes',
                    ('picture','pic_download'),
                    ('upload_photo_page', 'timestamp', 'modified'),
                    ('scope_of_work', 'scope_download',),
                    ('secure', 'occupied', 'major_structural_issues', 'quick_condition'),
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


#class PhotoInline(admin.StackedInline):
#    model = Photo
    #fields = ('date_purchased', 'date_expiring', 'amount_paid', )
    #readonly_fields=('closing',)
#    extra = 3

class ConditionReportProxyAdmin(admin.ModelAdmin):
    readonly_fields = ('upload_photo_page', 'pic_download', 'timestamp')
    list_display = ('Property','Property_surplus', 'Property_ncst', 'timestamp')
    def upload_photo_page(self, obj):
        if obj.Property_ncst is not None:
            upload_photo_page_link = '<a target="_blank" href="{}?Property_ncst={}">{}</a>'.format(
                reverse("admin_add_photos"), obj.Property_ncst.pk, "Add photos page")
        elif obj.Property_surplus is not None:
            upload_photo_page_link = '<a target="_blank" href="{}?Property_surplus={}">{}</a>'.format(
                reverse("admin_add_photos"), obj.Property_surplus.pk, "Add photos page")
        else:
            upload_photo_page_link = '<a target="_blank" href="{}?Property={}">{}</a>'.format(
                reverse("admin_add_photos"), obj.Property.pk, "Add photos page")

        return mark_safe(upload_photo_page)

    def pic_download(self, obj):
        if obj.id is None or obj.picture == '':
            return '<none>'
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("send_class_file", kwargs={'app_name': 'property_condition', 'class_name': 'ConditionReport', 'pk':obj.id, 'field_name':'picture'}),
                "Download"
            ))

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ConditionReportProxyAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if 'notes' in db_field.name:
            formfield.widget = forms.Textarea(attrs={'rows':4})
        return formfield


    fieldsets = (
        ('Property', {
            'fields':
                (
                    ('Property','Property_surplus', 'Property_ncst'),
                    'general_property_notes',
                    ('picture','pic_download'),
                    ('upload_photo_page', 'timestamp'),
                    ('secure', 'occupied', 'major_structural_issues', 'quick_condition'),
                )
            }
        ),
    )

admin.site.register(ConditionReport, ConditionReportAdmin)
admin.site.register(ConditionReportProxy, ConditionReportProxyAdmin)
