from django.db import models
from django.conf import settings
from localflavor.us.models import PhoneNumberField, USStateField, USZipCodeField
from applications.models import Application
from property_inventory.models import Property
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from datetime import timedelta, date

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
        return '{0} {1} {2} {3} {4} {5}'.format(self.mailing_address_line1, self.mailing_address_line2, self.mailing_address_line3, self.mailing_address_city, self.mailing_address_state, self.mailing_address_zip)

class title_company(models.Model):
    name = models.CharField(max_length=254)
    primary_contact = models.ForeignKey('company_contact', blank=True, null=True)
    address = models.ForeignKey('mailing_address', blank=True, null=True)
    offer_to_users = models.BooleanField(default=True)

    class Meta:
        verbose_name = "title company"
        verbose_name_plural = "title companies"
    def __unicode__(self):
        return self.name

def save_location(instance, filename):
    if instance.application:
        return 'closings/{0}/{1}'.format(instance.application.Property, filename)
    return 'closings/{0}/{1}'.format(instance.prop, filename)

class processing_fee(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    closing = models.ForeignKey('closing', blank=False, editable=False, related_name='processing_fee')
    timestamp = models.DateTimeField(auto_now_add=True)
    stripe_token = models.CharField(max_length=30, blank=True, editable=False)
    paid = models.BooleanField(default=False)
    date_paid = models.DateField(blank=True, null=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    check_number = models.CharField(max_length=255, blank=True, help_text="If a buyer pays the processing fee with a cashier's check then the check number is entered manually by staff")
    notes = models.CharField(max_length=2048, blank=True)
    slug = models.SlugField(max_length=50, allow_unicode=False, blank=False, editable=False)
    stripeTokenType = models.CharField(max_length=1024, blank=True, editable=False)
    stripeEmail = models.CharField(max_length=1024, blank=True, editable=False)

    def __unicode__(self):
        return 'Processing Fee - {0}'.format(self.closing,)

    class Meta:
        verbose_name = "processing fee"
        verbose_name_plural = "processing fees"


def today_plus_1_year():
    return date.today()+timedelta(days=365)


class purchase_option(models.Model):
    closing = models.ForeignKey('closing')
    date_purchased = models.DateField(blank=False, null=False, default=date.today)
    date_expiring = models.DateField(blank=False, null=False, default=today_plus_1_year)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __unicode__(self):
        return 'Purchase Option - {0} - exp {1}'.format(self.closing, self.date_expiring)

    def save(self, *args, **kwargs):
        super(purchase_option, self).save(*args, **kwargs)
        if self.date_expiring > date.today():
            print self.closing.application.Property.status
            self.closing.application.Property.status = 'this is fake!'
            print self.closing.application.Property.status

    class Meta:
        verbose_name = "purchase option"
        verbose_name_plural = "purchase options"


class closing(models.Model):
    application = models.ForeignKey(Application, help_text="Select the application if it is in the system", null=True, blank=True, related_name='closing_set')
    prop = models.ForeignKey(Property, verbose_name="Property", help_text="Select the property only if this is a legacy application that is not listed under Application", null=True, blank=True)
    date_time = models.DateTimeField(blank=True, null=True)
    location = models.ForeignKey('location', blank=True, null=True)
    title_company = models.ForeignKey(title_company, blank=True, null=True)
    title_company_freeform = models.CharField(max_length=50, blank=True, null=True)
    title_commitment = models.FileField(upload_to=save_location, blank=True, null=True)
    closing_statement = models.FileField(upload_to=save_location, blank=True, null=True)
    deed = models.FileField(upload_to=save_location, blank=True, null=True)
    ri_deed = models.FileField(upload_to=save_location, blank=True, null=True)
    nsp_convenants = models.FileField(upload_to=save_location, blank=True, null=True)
    project_agreement = models.FileField(upload_to=save_location, blank=True, null=True)
    assignment_and_assumption_agreement = models.FileField(upload_to=save_location, blank=True, null=True)
    closed = models.BooleanField(default=False, help_text="Has this transaction been completed?")
    notes = models.CharField(max_length=2048, blank=True, help_text="Internal notes")
    city_proceeds = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount for the City of Indianapolis", blank=True, null=True)
    ri_proceeds = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount for Renew Indianapolis", blank=True, null=True)

    def save(self, *args, **kwargs):
        super(closing, self).save(*args, **kwargs)
        if not processing_fee.objects.filter(closing=self).exists():
            if self.application.application_type == Application.SIDELOT:
                amount = settings.COMPANY_SETTINGS['SIDELOT_PROCESSING_FEE']
            else:
                amount = settings.COMPANY_SETTINGS['STANDARD_PROCESSING_FEE']
            fee = processing_fee(amount_due=amount, closing=self, slug=slugify(self.application.Property))
            fee.save()

    def __unicode__(self):
            if self.application:
                if self.application.organization:
                        return '{0} - {1} {2} ({3})'.format(self.application.Property, self.application.user.first_name, self.application.user.last_name, self.application.organization)
                return '{0} - {1} {2}'.format(self.application.Property, self.application.user.first_name, self.application.user.last_name)
            else:
                return '{0} - {1}'.format(self.prop, "Legacy Application")
