from django.forms import ModelForm, ValidationError, Form, ModelChoiceField, CharField
from .models import closing, processing_fee, title_company

class TitleCompanyChooser(Form):
    title_company = ModelChoiceField(queryset=title_company.objects.filter(offer_to_users__exact=True).order_by('?'), help_text='This is a list of title companies we have worked with successfully in the past, in no particular order.')
    manual_title_company_choice = CharField(max_length=50, required=False, label='Other choice', help_text='You are free to pick whichever title company you wish. If your preferred title company is not shown in the dropdown list above, please enter it here.')

class ClosingAdminForm(ModelForm):
    def clean(self):
        cleaned_data = super(ClosingAdminForm, self).clean()
        prop = cleaned_data.get("prop")
        application = cleaned_data.get("application")
        if prop and application:
            raise ValidationError("Can't have both a property and an application - please select one or another")
        if not prop and not application:
            raise ValidationError("Please select either an application or a property")
        # Always return the full collection of cleaned data.
        return cleaned_data

class ClosingScheduleAdminForm(ModelForm):
    pass
