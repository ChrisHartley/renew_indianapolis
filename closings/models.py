from django.db import models
from django.db.models import Q
from django.conf import settings
from localflavor.us.models import PhoneNumberField, USStateField, USZipCodeField
from applications.models import Application, MeetingLink, Meeting
from property_inventory.models import Property
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from datetime import timedelta, date, datetime
from django.utils.timezone import localtime, now
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone # use this for timezone aware times

class location(models.Model):
    name = models.CharField(max_length=254)
    def __unicode__(self):
        return self.name

class company_contact(models.Model):
    company = models.ForeignKey('title_company', on_delete=models.CASCADE)
    title = models.CharField(blank=True, max_length=255)
    first_name = models.CharField(blank=False, max_length=255)
    last_name = models.CharField(blank=False, max_length=255)
    phone_number = PhoneNumberField()
    email_address = models.CharField(max_length=254)
    address = models.ForeignKey('mailing_address', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "company contacts"
        verbose_name_plural = "company contacts"

    def __unicode__(self):
        return '{0} {1} ({2})'.format(self.last_name, self.first_name, self.company)


class mailing_address(models.Model):
    mailing_address_line1 = models.CharField(max_length=254)
    mailing_address_line2 = models.CharField(max_length=254, blank=True)
    mailing_address_line3 = models.CharField(max_length=254, blank=True)
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
    primary_contact = models.ForeignKey('company_contact', blank=True, null=True, on_delete=models.CASCADE)
    address = models.ForeignKey('mailing_address', blank=True, null=True, on_delete=models.CASCADE)
    offer_to_users = models.BooleanField(default=True)

    class Meta:
        verbose_name = "title company"
        verbose_name_plural = "title companies"
    def __unicode__(self):
        return '{0}'.format(self.name,)

def save_location(instance, filename):
    if instance.application:
        return 'closings/{0}/{1}'.format(instance.application.Property, filename)
    return 'closings/{0}/{1}'.format(instance.prop, filename)

class processing_fee(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    closing = models.ForeignKey('closing', blank=False, editable=False, related_name='processing_fee', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    stripe_token = models.CharField(max_length=30, blank=True, editable=False)
    paid = models.BooleanField(default=False)
    date_paid = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
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
        ordering = ['-timestamp']

def today_plus_1_year():
    return date.today()+timedelta(days=365)


class purchase_option(models.Model):
    closing = models.ForeignKey('closing', on_delete=models.CASCADE)
    date_purchased = models.DateField(blank=False, null=False, default=date.today)
    date_expiring = models.DateField(blank=False, null=False, default=today_plus_1_year)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __unicode__(self):
        return 'Purchase Option - {0} - exp {1}'.format(self.closing, self.date_expiring)

    def save(self, *args, **kwargs):
        super(purchase_option, self).save(*args, **kwargs)
        #if self.date_expiring > date.today():
        #    print self.closing.application.Property.status
        #    self.closing.application.Property.status = 'this is fake!'
        #    print self.closing.application.Property.status

    class Meta:
        verbose_name = "purchase option"
        verbose_name_plural = "purchase options"


class closing(models.Model):
    application = models.ForeignKey(Application, help_text="Select the application if it is in the system", null=True, blank=True, related_name='closing_set', on_delete=models.CASCADE)
    prop = models.ForeignKey(Property, verbose_name="Property", help_text="Select the property only if this is a legacy application that is not listed under Application", null=True, blank=True, on_delete=models.CASCADE)
    date_time = models.DateTimeField(blank=True, null=True)
    location = models.ForeignKey('location', blank=True, null=True, on_delete=models.CASCADE)
    title_company = models.ForeignKey(title_company, blank=True, null=True, on_delete=models.CASCADE)
    title_company_freeform = models.CharField(max_length=255, blank=True, null=True)
    title_commitment = models.FileField(upload_to=save_location, blank=True, null=True)
    closing_statement = models.FileField(upload_to=save_location, blank=True, null=True)
    deed = models.FileField(upload_to=save_location, blank=True, null=True)
    recorded_city_deed = models.FileField(upload_to=save_location, blank=True, null=True)
    recorded_city_deed_instrument_number = models.CharField(max_length=255, blank=True, default='')
    ri_deed = models.FileField(upload_to=save_location, blank=True, null=True)
    recorded_ri_deed = models.FileField(upload_to=save_location, blank=True, null=True)
    recorded_ri_deed_instrument_number = models.CharField(max_length=255, blank=True, default='')

    nsp_convenants = models.FileField(upload_to=save_location, blank=True, null=True)
    project_agreement = models.FileField(upload_to=save_location, blank=True, null=True)
    assignment_and_assumption_agreement = models.FileField(upload_to=save_location, blank=True, null=True)
    signed_purchase_agreement = models.FileField(upload_to=save_location, blank=True, null=True)
    renew_sales_disclosure_form = models.FileField(upload_to=save_location, blank=True, null=True)
    city_sales_disclosure_form = models.FileField(upload_to=save_location, blank=True, null=True)
    assigned_city_staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, limit_choices_to={'groups__name__in': ["City Staff",]}, on_delete=models.CASCADE)
    closed = models.BooleanField(default=False, help_text="Has this transaction been completed?")
    notes = models.CharField(max_length=2048, blank=True, help_text="Internal notes")
    city_proceeds = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount for the City of Indianapolis", blank=False, default=0)
    city_loan_proceeds = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount due to the City of Indianapolis, but not paid at closing", blank=False, default=0)
    ri_proceeds = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount for Renew Indianapolis", blank=True, default=0)
    ri_closing_fee = models.DecimalField(max_digits=10, decimal_places=2, help_text="Renew Indianapolis Closing Fee", blank=True, default=0)

    #scanned_receipt = models.FileField(upload_to=save_location, blank=True, null=True)

    archived = models.BooleanField(default=False, help_text="Closing did not occur and should be archived.")

    def save(self, *args, **kwargs):
        try:
            orig_closing = closing.objects.get(pk=self.pk)
        except closing.DoesNotExist:
            pass
        else:
            if self.closed == False and self.assigned_city_staff is not None and self.application and settings.SEND_CLOSING_ASSIGNMENT_EMAILS:
                if orig_closing.assigned_city_staff != self.assigned_city_staff:
                    subject = 'New closing assigned - {0} {1}'.format(self.application.Property, datetime.strftime(localtime(self.date_time), "%A %B %d at %-I:%M %p"))
                    message = 'Hello, the closing for {0} has been assigned to you, scheduled for {1} with {2}. Details and documents: https://build.renewindianapolis.org{3}'.format(self.application.Property, datetime.strftime(localtime(self.date_time), "%A %B %d at %-I:%M %p"), self.title_company, reverse('admin:closings_closing_proxy_change', args=(self.pk,)))
                    from_email = 'info@renewindianapolis.org'
                    send_mail(subject, message, from_email, [self.assigned_city_staff.email,settings.COMPANY_SETTINGS['APPLICATION_CONTACT_EMAIL']])

            if self.closed == True and orig_closing.closed == False and self.application and self.application.Property.renew_owned == False and settings.SEND_CITY_CLOSED_NOTIFICATION_EMAIL:
                subject = 'City owned property closed by Renew Indianapolis - {0}'.format(self.application.Property,)
                message = 'This is a courtesy notification that the property at {0} was sold, please update your files as necessary.'.format(self.application.Property,)
                recipient = [settings.CITY_PROPERTY_MANAGER_EMAIL,]
                if self.application.Property.urban_garden == True:
                    message = message + ' Our records show there was an active urban garden license on this property.'
                    recipient.append(settings.CITY_URBAN_GARDENING_MANAGER_EMAIL)
                from_email = 'info@renewindianapolis.org'
                send_mail(subject, message, from_email, recipient,)

            if self.closed == True and orig_closing.closed == False and self.application and self.application.Property.blc_listing.count() > 0 and settings.SEND_BLC_ACTIVITY_NOTIFICATION_EMAIL:
                subject = 'BLC listed property closed - {0}'.format(self.application.Property,)
                message = 'This is a courtesy notification that the BLC property at {0} was sold, please update your files as necessary.'.format(self.application.Property,)
                recipient = [settings.BLC_MANAGER_EMAIL,]
                from_email = 'info@renewindianapolis.org'
                send_mail(subject, message, from_email, recipient,)

        super(closing, self).save(*args, **kwargs)
        # we can only do fancy stuff if there is an application associated with the closing, which legacy closings don't have. so skip allt he fancy stuff in that case.
        if self.application:
            # create a new processing fee object with the correct price if necessary
            if not processing_fee.objects.filter(closing=self).exists():
                if self.application.application_type == Application.SIDELOT or self.application.application_type == Application.VACANT_LOT or self.application.application_type == Application.FDL:
                    amount = settings.COMPANY_SETTINGS['SIDELOT_PROCESSING_FEE']
                else:
                    amount = settings.COMPANY_SETTINGS['STANDARD_PROCESSING_FEE']
                fee = processing_fee(amount_due=amount, closing=self, slug=slugify(self.application.Property), due_date=now()+timedelta(days=9))
                fee.save()

            # Change the status of the property to 'Sold mm/dd/yyyy' based on the closing date, if it isn't already.
            if 'Sold' not in self.application.Property.status and self.closed == True and self.date_time is not None:
                prop = self.application.Property
                prop.status = 'Sold {0}'.format(self.date_time.strftime('%m/%d/%Y'))
                prop.buyer_application = self.application
                prop.save()

            if self.archived == True and orig_closing.archived != True:
                prop = self.application.Property
                prop.status = 'Available'
                prop.applicant = ''
                prop.buyer_application = None
                prop.save()
                app = self.application
                app.status = Application.WITHDRAWN_STATUS
                app.staff_notes = 'Application marked as withdrawn when closing archived - {0}\n{1}'.format(timezone.now(),app.staff_notes)
                app.save()
                # This is where we would look for a backup application and create a new closing, processing fee, etc.

                backup_app_ml = MeetingLink.objects.filter(application__Property__exact=self.application.Property).filter(meeting_outcome__exact=MeetingLink.BACKUP_APPROVED_STATUS).filter(
                        Q(
                            Q(
                                Q(application__Property__renew_owned__exact=True),
                                Q(meeting__meeting_type__exact=Meeting.BOARD_OF_DIRECTORS)
                            )
                            |
                            Q(
                                Q(application__Property__renew_owned__exact=False),
                                Q(meeting__meeting_type__exact=Meeting.MDC)
                            )
                        )
                ).order_by('application__submitted_timestamp').first()
                if backup_app_ml is not None:
                    backup_app_ml.meeting_outcome = MeetingLink.APPROVED_STATUS
                    backup_app_ml.notes = 'Automatically promoted to approved after primary application closing archived - {} - {}'.format(timezone.now(), backup_app_ml.notes,)
                    backup_app_ml.save()
                    subject = 'Backup application promoted - {0}'.format(backup_app_ml.application,)
                    message = 'This is a courtesy notification that the backup application {} was promoted and a closing created.'.format(backup_app_ml.application,)
                    recipient = [settings.COMPANY_SETTINGS['APPLICATION_CONTACT_EMAIL'],]
                    from_email = 'info@renewindianapolis.org'
                    send_mail(subject, message, from_email, recipient,)

                if self.application.Property.blc_listing.count() > 0 and settings.SEND_BLC_ACTIVITY_NOTIFICATION_EMAIL:
                    subject = 'BLC listed property closing cancelled - {0}'.format(self.application.Property,)
                    message = 'This is a courtesy notification that the closing on BLC property at {0} was cancelled. Please update your files as necessary.'.format(self.application.Property,)
                    recipient = [settings.BLC_MANAGER_EMAIL,]
                    from_email = 'info@renewindianapolis.org'
                    send_mail(subject, message, from_email, recipient,)


    def __unicode__(self):
            if self.application:
                if self.application.organization:
                        return '{0} - {1} {2} ({3})'.format(self.application.Property, self.application.user.first_name, self.application.user.last_name, self.application.organization)
                return '{0} - {1} {2}'.format(self.application.Property, self.application.user.first_name, self.application.user.last_name)
            else:
                return '{0} - {1}'.format(self.prop, "Legacy Application")

class closing_proxy(closing):
    class Meta:
        proxy = True
        verbose_name = 'Closing Scheduling'

class closing_proxy2(closing):
    class Meta:
        proxy = True
        verbose_name = 'Closing Summary'
        verbose_name_plural = 'Closing Summaries'


#class project_agreement(models.Model):
#    prop = models.ForeignKey(Property)
#    start_date = models.DateField(null=False, blank=False, help_text='When the Project Agreement begins, either at closing or upon assumption')
#    expiration_date = models.DateField(null=False, blank=False)
#    buyer_name = models.CharField(max_length=254)
#    released = models.BooleanField(default=False)

# class release_inspection(models.Model):
#     prop = models.ForeignKey
#     user = models.ForeignKey(User)
#     staff_user = models.ForeignKey(User, related_name='staff_user')
#     created = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)
#     staff_notes = models.CharField(max_length=5000)
#     user_notes = models.CharField(max_length=5000)
