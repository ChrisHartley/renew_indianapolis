from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import InspectionRequest
from property_inventory.models import Property
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail


class InspectionRequestForm(forms.ModelForm):
    note = forms.CharField(
        max_length=1024,
        required=False,
        widget=forms.Textarea
    )

    def send_email(self, prop):
        subject = 'New inspection request - {0}'.format(prop,)
        message = 'Hello, an inspection for {0} has been submitted. View here: https://build.renewindianapolis.org{1}'.format(prop, reverse('admin:project_agreement_management_inspectionrequest_changelist'))#, args=(self.pk,)))
        from_email = 'info@renewindianapolis.org'
        if prop.renew_owned == True:
            to_email = settings.COMPANY_SETTINGS['RENEW_PA_RELEASE']
        else:
            to_email = settings.COMPANY_SETTINGS['CITY_PA_RELEASE']
        send_mail(subject, message, from_email, [to_email,])


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
