from django.forms import ModelForm, ValidationError
from .models import closing

class ClosingAdminForm(ModelForm):
    def clean(self):
        cleaned_data = super(ClosingAdminForm, self).clean()
        prop = cleaned_data.get("prop")
        application = cleaned_data.get("application")
        print "!!!!!!!!!"
        if prop and application:
            raise ValidationError("Can't have both a property and an application - please select one or another")
        # Always return the full collection of cleaned data.
        return cleaned_data
