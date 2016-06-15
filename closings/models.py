from django.db import models
from localflavor.us.models import PhoneNumberField, USStateField, USZipCodeField
from applications.models import Application
from property_inventory.models import Property

class location(models.Model):
    name = models.CharField(max_length=254)
    def __unicode__(self):
        return self.name

class company_contact(models.Model):
    company = models.ForeignKey('title_company')
    title = models.CharField(blank=True, max_length=255)
    first_name = models.CharField(blank=False, max_length=255)
    last_name = models.CharField(blank=False, max_length=255)
    phone_number = PhoneNumberField()
    email_address = models.CharField(max_length=254)
    address = models.ForeignKey('mailing_address', blank=True, null=True)

    class Meta:
        verbose_name = "company contacts"
        verbose_name_plural = "company contacts"

    def __unicode__(self):
        return '{0} {1} ({2})'.format(self.last_name, self.first_name, self.company)


class mailing_address(models.Model):
    mailing_address_line1 = models.CharField(max_length=254)
    mailing_address_line2 = models.CharField(max_length=254)
    mailing_address_line3 = models.CharField(max_length=254)
    mailing_address_city = models.CharField(max_length=254)
    mailing_address_state = USStateField()
    mailing_address_zip = USZipCodeField()

    class Meta:
        verbose_name = "mailing address"
        verbose_name_plural = "mailing addresses"

    def __unicode__(self):
        return '{0} {1} {2} {3} {4} {5}'.format(mailing_address_line1, self.mailing_address_line2, self.mailing_address_line3, self.mailing_address_city, self.mailing_address_state, self.mailing_address_zip)

class title_company(models.Model):
    name = models.CharField(max_length=254)
    primary_contact = models.ForeignKey('company_contact', blank=True, null=True)
    address = models.ForeignKey('mailing_address', blank=True, null=True)

    class Meta:
        verbose_name = "title company"
        verbose_name_plural = "title companies"
    def __unicode__(self):
        return self.name

def save_location(instance, filename):
    if instance.application:
        return 'closings/{0}/{1}'.format(instance.application.Property, filename)
    return 'closings/{0}/{1}'.format(instance.prop, filename)

class closing(models.Model):
    application = models.ForeignKey(Application, help_text="Select the application if it is in the system", null=True, blank=True)
    prop = models.ForeignKey(Property, verbose_name="Property", help_text="Select the property only if this is a legacy application that is not listed under Application", null=True, blank=True)
    date_time = models.DateTimeField(blank=True, null=True)
    location = models.ForeignKey('location', blank=True, null=True)
    title_company = models.ForeignKey(title_company)
    closing_statement = models.FileField(upload_to=save_location, blank=True, null=True)
    deed = models.FileField(upload_to=save_location, blank=True, null=True)
    nsp_convenants = models.FileField(upload_to=save_location, blank=True, null=True)
    project_agreement = models.FileField(upload_to=save_location, blank=True, null=True)
    assignment_and_assumption_agreement = models.FileField(upload_to=save_location, blank=True, null=True)
#    scope_of_work = models.FileField(upload_to=save_location)
    def __unicode__(self):
            if self.application:
                if self.application.organization:
                        return '{0} - {1} {2} ({3})'.format(self.application.Property, self.application.user.first_name, self.application.user.last_name, self.application.orgnization)
                return '{0} - {1} {2}'.format(self.application.Property, self.application.user.first_name, self.application.user.last_name)
            else:
                return '{0} - {1}'.format(self.prop, "Legacy Application")
