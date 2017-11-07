from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, Button, HTML, Div, Reset
from crispy_forms.bootstrap import FormActions
from django.forms.widgets import HiddenInput, SelectMultiple

from .models import parcel

class UniSearchForm(forms.ModelForm):

    general_search = forms.CharField(max_length=30, label='Address, parcel number')
    #geometry_type = forms.CharField()

    class Meta:
        model = parcel
        exclude = []
        #fields = ['geometry_type','general_search','has_building', 'township', 'notes', 'interesting', 'classification', 'demolition_order', 'repair_order','requested_from_commissioners', 'previously_held_gateway_area']

    def __init__(self, *args, **kwargs):
        super(UniSearchForm, self).__init__(*args, **kwargs)
        #self.fields['general_search'].widget = HiddenInput() # because we want the search box up top, so we copy the value from that box to this hidden one prior to submission
        #self.fields['geometry_type'].widget = HiddenInput() # because we need to indicate we are looking for centroid points

        self.helper = FormHelper()
        self.helper.form_id = 'UniSearchForm'
        self.helper.form_class = 'form-inline'
        #self.helper.label_class = 'col-sm-3'
        #self.helper.field_class = 'col-sm-5'
        self.helper.render_unmentioned_fields = False

        self.helper.form_method = 'get'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            FormActions(
                Reset('cancel', 'Reset'),
                Submit('submit', 'Search', css_class='top-search-button'),
                #HTML('<button id="modal_toggle" class="btn btn-info btn-modal" data-toggle="modal" data-target="#fsModal">Show Results Table</button>'),
            ),
            Field('has_building', css_class='input-sm'),
            Field('general_search', css_class='input-sm'),
            Field('property_type', css_class='input-sm'),
            Field('flagged', css_class='input-sm'),
        #    Field('township', css_class='input-sm'),
            Field('notes', css_class='input-sm'),
        )
