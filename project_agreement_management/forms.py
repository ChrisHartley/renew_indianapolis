from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import InspectionRequest
from property_inventory.models import Property

class InspectionRequestForm(forms.ModelForm):
    note = forms.CharField(
        max_length=1024,
        required=False,
        widget=forms.Textarea
    )

    

    def __init__(self, *args, **kwargs):
        super(InspectionRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = True
        #self.helper.form_id = 'propertyInquiryForm'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.add_input(Submit('submit', 'Submit'))


    class Meta:
        model = InspectionRequest
        fields = ['Property', 'note']
