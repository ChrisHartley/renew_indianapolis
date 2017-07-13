from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, Button, HTML, Div #, InlineRadios
from crispy_forms.bootstrap import FormActions, InlineRadios
from django.forms.widgets import HiddenInput, SelectMultiple
from property_inventory.models import Property, Zipcode, CDC, Zoning

class PropertySearchForm(forms.ModelForm):
    #zoning = forms.ModelMultipleChoiceField(queryset=Zoning.objects.all().order_by('name'), required=False)
    #zipcodes = forms.ModelMultipleChoiceField(queryset=Zipcode.objects.all().order_by('name'), required=False)
    #zipcode1 = forms.ModelChoiceField(queryset=Zipcode.objects.all().order_by('name'), required=False)
    #cdc = forms.ModelMultipleChoiceField(queryset=CDC.objects.all().order_by('name'), required=False)
    searchArea = forms.CharField(required=False, widget=HiddenInput())
    status_choices = (('Available', 'Available'), ('Sale', 'Application under review'),
                      ('MDC', 'Approved for Sale'), ('Sold', 'Sold'))
    status = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(choices=status_choices), required=False)
    parcel_or_street_address = forms.CharField(required=False)
    #featured_properties_only = forms.BooleanField(label='Boolean!!!!')
    featured_properties_only = forms.MultipleChoiceField(label='Boolean!!!!')


    class Meta:
        model = Property
        fields = ['nsp', 'zipcode', 'neighborhood', 'zone', 'sidelot_eligible', 'vacant_lot_eligible',
                  'homestead_only', 'bep_demolition', 'renew_owned', 'price_obo', 'hhf_demolition', 'searchArea']

    def __init__(self, *args, **kwargs):
        super(PropertySearchForm, self).__init__(*args, **kwargs)
        self.fields['searchArea'].widget = HiddenInput()
        #self.fields['featured_properties_only']
        self.helper = FormHelper()
        self.helper.form_id = 'PropertySearchForm'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-8'
        self.helper.render_unmentioned_fields = False

        self.helper.form_method = 'get'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Fieldset(
                'Search',
                HTML(
                    '<input type="checkbox" onclick="toggleDraw(this);" name="searchPolygon" value="polygon">Draw search area on map</input>'),
                #Field('parcel'),
                #Field('streetAddress'),
                Field('parcel_or_street_address'),
                InlineRadios('featured_properties_only'),
                Field('status'),
            ),
            Fieldset('', HTML(
                '<a href="javascript:void(0);" class="btn btn-default" id="searchToggle" role="button">Show more search options >>></a><br/>')),
            Fieldset(
                '',
                Field('nsp'),
                Field('structureType'),
                Field('cdc'),
                Field('neighborhood'),
                Field('zone'),
                Field('zipcode'),
                Field('sidelot_eligible'),
                Field('vacant_lot_eligible'),
                Field('homestead_only'),
                Field('bep_demolition'),
                Field('hhf_demolition'),
                Field('renew_owned'),
                Field('price_obo'),
                css_class='moreSearchOptions'),
            FormActions(
                #Button('cancel', 'Reset'),
                Submit('save', 'Search')
            )
        )
