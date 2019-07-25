from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, Button, HTML, Div
from crispy_forms.bootstrap import FormActions
from django.forms.widgets import HiddenInput, SelectMultiple

from .models import Parcel

class SurplusSearchForm(forms.ModelForm):

    general_search = forms.CharField(widget=HiddenInput())
    geometry_type = forms.CharField(widget=HiddenInput())

    class Meta:
        model = Parcel
        exclude = []
        fields = [
    #        'geometry_type',
    #        'general_search',
            'has_building',
    #        'township',
            'notes',
            'interesting',
    #        'classification',
        #    'demolition_order_count',
        #    'repair_order_count',
        #    'vbo_count',
        #    'requested_from_commissioners',
        #    'previously_held_gateway_area',
            'vetted',
        #    'vetting_notes'
            ]

    def __init__(self, *args, **kwargs):
        super(SurplusSearchForm, self).__init__(*args, **kwargs)
        self.fields['general_search'].widget = HiddenInput() # because we want the search box up top, so we copy the value from that box to this hidden one prior to submission
    #    self.fields['geometry_type'].widget = HiddenInput() # because we need to indicate we are looking for centroid points

        self.helper = FormHelper()
        self.helper.form_id = 'SurplusSearchForm'
        self.helper.form_class = 'form-inline'
        #self.helper.label_class = 'col-sm-3'
        #self.helper.field_class = 'col-sm-5'
        self.helper.render_unmentioned_fields = False

        self.helper.form_method = 'get'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            #Field('street_address', css_class='input-sm'),
            #Field('parcel_number', css_class='input-sm'),
            Field('interesting', css_class='input-sm'),
            #Field('area', css_class='input-sm'),
            Field('has_building', css_class='input-sm'),
    #        Field('big_ask', css_class='input-sm'),
            Field('township', css_class='input-sm'),
            #Field('land_value', css_class='input-sm'),
            #Field('improved_value', css_class='input-sm'),
        #    Field('classification', css_class='input-sm'),
    #        Field('demolition_order', css_class='input-sm'),
    #        Field('repair_order', css_class='input-sm'),
            Field('repair_order_count', css_class='input-sm'),
            Field('demolition_order_count', css_class='input-sm'),
            Field('vbo_count', css_class='input-sm'),
            Field('vetted', css_class='input-sm'),
            Field('general_search'),
            Field('geometry_type'),

        #    Field('requested_from_commissioners', css_class='input-sm'),
        #    Field('previously_held_gateway_area', css_class='input-sm'),
            Field('notes', css_class='input-sm'),
        )
