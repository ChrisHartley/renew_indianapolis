from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import InspectionRequest
from property_inventory.models import Property
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail


class InspectionRequestForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InspectionRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields = True
        self.fields['request_notes'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.add_input(Submit('submit', 'Submit'))


    class Meta:
        model = InspectionRequest
        fields = ['Property', 'email', 'phone_number', 'request_notes']
