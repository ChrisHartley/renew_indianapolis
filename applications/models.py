from django.db import models
from django.contrib.auth.models import User
from django.apps import apps
from property_inventory.models import Property
from applicants.models import Organization
from django.utils.deconstruct import deconstructible
from django.conf import settings

from datetime import datetime, timedelta
from dateutil.rrule import *
from django.utils import timezone # use this for timezone aware times
from django.core.mail import send_mail
#from datetime import timedelta, date, datetime
from django.utils.timezone import now
from django.utils.encoding import python_2_unicode_compatible


@deconstructible
class UploadToApplicationDir(object):
    path = "applicants/{0}/{1}{2}"

    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        return 'applicants/{0}/{1}{2}'.format(instance.user.email, self.sub_path, filename)

@python_2_unicode_compatible
class Application(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Property = models.ForeignKey(Property, null=True, blank=True, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.CASCADE,
                                     help_text="Other parties (eg organizations, spouses, siblings, etc). This, or the name on your account, are the only names that can be shown on the deed")

    created = models.DateTimeField(auto_now_add=True)
    submitted_timestamp = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)

    HOMESTEAD = 1
    STANDARD = 2
    SIDELOT = 3
    VACANT_LOT = 4
    FDL = 5

    APPLICATION_TYPES = (
        (HOMESTEAD, 'Homestead - Applicants will use this property as their primary residence.'),
        (STANDARD, 'Standard - Applicants intend to rent or sell the property after completing the proposed project.'),
        (SIDELOT, 'Sidelot - lot is adjacent to owner occupied property'),
        (VACANT_LOT, 'Vacant Lot - Properties that have been in city inventory for an extended period of time; no requirement to build.'),
        (FDL, 'Future Development Lot - Vacant lots with no requirement for immediate development.')
    )


    # Application types to show to the user as active choices
    ACTIVE_APPLICATION_TYPES = (HOMESTEAD, STANDARD, FDL)

    WITHDRAWN_STATUS = 1
    HOLD_STATUS = 2
    ACTIVE_STATUS = 3
    COMPLETE_STATUS = 4
    INITIAL_STATUS = 5

    STATUS_TYPES = (
        (WITHDRAWN_STATUS, 'Withdrawn'),
        (HOLD_STATUS, 'On Hold'),
        (ACTIVE_STATUS, 'Active / In Progress'),
        (COMPLETE_STATUS, 'Complete / Submitted'),
        (INITIAL_STATUS, 'Initial state'),
    )

    YES_CHOICE = True
    NO_CHOICE = False
    YESNO_TYPES = (
        (YES_CHOICE, 'Yes'),
        (NO_CHOICE, 'No')
    )

    YES_YNNA_CHOICE = 1
    NO_YNNA_CHOICE = 2
    NA_YNNA_CHOICE = 3
    YESNONA_TYPES = (
        (YES_YNNA_CHOICE, 'Yes'),
        (NO_YNNA_CHOICE, 'No'),
        (NA_YNNA_CHOICE, 'Not applicable'),
    )


    CURRENT_STATUS = 3
    DELINQUENT_STATUS = 2
    UNKNOWN_STATUS = 1
    NA_STATUS = 0

    TAX_STATUS_CHOICES = (
        (CURRENT_STATUS, 'Current'),
        (DELINQUENT_STATUS, 'Delinquent'),
        (UNKNOWN_STATUS, 'Unknown'),
        (NA_STATUS, 'N/A - No property owned')
    )

    application_type = models.IntegerField(
        choices=APPLICATION_TYPES,
        verbose_name='Application Type',
        null=True,
        blank=True,
        help_text="""If you will live in this property as your primary
            residence chose Homestead, if you will rent or sell chose Standard.
            Some, but not all, of our vacant lots are available through the
            Future Development Lot sales program, which does not require
            immediate development. The sidelot and vacant lot sales programs are
            no longer available."""
    )

    status = models.IntegerField(
        choices=STATUS_TYPES,
        help_text="What is the internal status of this application?",
        null=False,
        default=INITIAL_STATUS,
        verbose_name='Status'
    )

    is_rental = models.NullBooleanField(
        choices=YESNO_TYPES,
        verbose_name='Rental Property',
        help_text="Will this property be a rental?"
    )

    planned_improvements = models.TextField(
        max_length=5120,
        help_text="Tell us about your plans for this property and who will do what work.",
        blank=True
    )

    SELF_PERFORMED = 'Self'
    FRIENDS_FAMILY_PERFORMED = 'Friends and family'
    CONTRACTOR_PERFORMED = 'Contractor'
    OTHER_PERFORMED = 'Other'


    WORK_PERFORMER_CHOICES = (
        (SELF_PERFORMED,SELF_PERFORMED),
        (FRIENDS_FAMILY_PERFORMED,FRIENDS_FAMILY_PERFORMED),
        (CONTRACTOR_PERFORMED,CONTRACTOR_PERFORMED),
        (OTHER_PERFORMED,OTHER_PERFORMED),
    )

    who_will_perform_work = models.CharField(
        max_length=254,
        help_text="Who will perform most of the work?",
        blank=True,
        choices=WORK_PERFORMER_CHOICES,
        default='',
    )

    long_term_ownership = models.CharField(
        max_length=255,
        help_text="Who will own the property long-term? (e.g. self, LLC, end-buyer, etc.)",
        blank=True
    )

    estimated_cost = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="How much do you estimate your project will cost?"
    )

    source_of_financing = models.TextField(
        max_length=5120,
        help_text="""
			Tell us how you plan to pay for the proposed improvements, including any donated materials or
			labor from friends and family.  Also include any grants you plan to apply for, including the
			name of the grant and whether it is awarded, pending, or not yet submitted.
		""",
        blank=True
    )

    timeline = models.TextField(
        max_length=5120,
        help_text="Tell us your anticipated timeline for this project. You can take up to 24 months from closing to complete the work in your scope of work.",
        blank=True
    )

    staff_recommendation = models.NullBooleanField(
        help_text="Staff recommendation to Review Comittee",
        null=True
    )

    staff_recommendation_notes = models.CharField(
        max_length=255,
        help_text="Explanation of staff recommendation to Review Comittee",
        blank=True
    )

    staff_summary = models.TextField(
        max_length=5120,
        help_text="Staff summary of application for Review Committee",
        blank=True
    )

    staff_sow_total = models.DecimalField(max_digits=10, decimal_places=2,
        help_text="Total scope of work, as verified by staff.",
        verbose_name='Staff determined scope of work total',
        null=True,
        blank=True
    )

    staff_pof_total = models.DecimalField(max_digits=10, decimal_places=2,
        help_text="Total funds demonstrated",
        verbose_name='Staff determined PoF',
        null=True,
        blank=True
    )

    staff_pof_description = models.CharField(max_length=1024, blank=True, verbose_name="Staff description of proof of funds provided")

    staff_points_to_consider = models.CharField(
        verbose_name="Staff's suggested points to consider",
        max_length=255,
        blank=True
    )

    # neighborhood notification - boolean or file? boolean and then collection
    # of files

    conflict_board_rc = models.NullBooleanField(
        choices=YESNO_TYPES,
        verbose_name="Do you, any family members or partner/member of your entity, or any of your entity's board members or employees work for Renew Indianapolis or serve on the Renew Indianapolis Board of Directors or Committees and thus pose a potential conflict of interest?",
        blank=True
    )

    conflict_board_rc_name = models.CharField(
        verbose_name="If yes, what is their name?",
        blank=True,
        max_length=255
    )

    conflict_city = models.NullBooleanField(
        choices=YESNO_TYPES,
        verbose_name="Do you, any family members or partner/member of your entity, or any of your entity's board members or employees serve on the Metropolitan Development Commission or are employed by the City of Indianapolis Department of Metropolitan Development and thus pose a potential conflict of interest?",
        blank=True
    )

    conflict_city_name = models.CharField(
        verbose_name="If yes, what is their name?",
        blank=True,
        max_length=255
    )


    active_citations = models.NullBooleanField(
        choices=YESNO_TYPES,
        verbose_name="Do you own any property that is subject to any un-remediated citation of violation of the state and local codes and ordinances?",
        help_text="The unsafe building code and building code history of properties owned by the prospective buyer, or by individuals or entities related to the prospective buyer, will be a factor in determining eligibility.  Repeat violations, unmitigated violations, and unpaid civil penalties may cause a buyer to be ineligible",
        blank=True
    )

    landlord_in_marion_county = models.NullBooleanField(
        choices=YESNO_TYPES,
        verbose_name="Do you own any rental properties in Marion County?",
        help_text="For the purposes of this question, refer to definitions in <a href='https://www.municode.com/library/in/indianapolis_-_marion_county/codes/code_of_ordinances?nodeId=TITIVBUCORELI_CH851INLAREPR_S851-103DE&showChanges=true' target='_blank'>Chapter 851-103</a> of the Marion County Code of Ordinances",
        blank=True
    )

    landlord_registry = models.IntegerField(
        choices=YESNONA_TYPES,
        verbose_name="Are your rental properties registered in the Landlord Registry?",
        help_text="<a href='https://www.municode.com/library/in/indianapolis_-_marion_county/codes/code_of_ordinances?nodeId=TITIVBUCORELI_CH851INLAREPR&showChanges=true' target='_blank'>Chapter 851</a> of the Marion County Code of Ordinances requires that landlords register rental properties in the <a href='https://www.indy.gov/activity/landlord-registration-program' target='_blank'>Landlord Registry</a>",
        blank=True,
        null=True,
    )

    tax_status_of_properties_owned = models.IntegerField(
        choices=TAX_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name='Tax status of property currently owned in Marion County',
        help_text="If you do not own any property (real estate) in Marion County chose N/A. If you chose 'Unknown' we will contact you for an explanation.",
    )

    other_properties_names_owned = models.CharField(
        max_length=255,
        verbose_name="If you own properties under other names or are a partner/member of an entity that owns properties, please list the names of those entities here",
        blank=True
    )

    prior_tax_foreclosure = models.NullBooleanField(
        choices=YESNO_TYPES,
        verbose_name="Were you the prior owner of any property in Marion County that was transferred to the Treasurer or to a local government as a result of tax foreclosure proceedings?",
        blank=True
    )

    sidelot_eligible = models.NullBooleanField(
        choices=YESNO_TYPES,
        verbose_name='Do you qualify for our side lot program?',
        help_text='To be eligible for our side lot program you must claim a homestead deduction on an adjacent property that shares at least a 75% property line with the vacant lot you are applying for. If you are not eligible you may still apply but you will be required to complete a sidelot policy waiver form, which we will email to you.'
    )

    vacant_lot_end_use = models.CharField(
        max_length=1024,
        verbose_name='What is your intended end-use for this property? Why are you buying it?',
        help_text='',
        blank=True,
    )

    finished_square_footage = models.CharField(
        max_length=1024,
        verbose_name='Finished or conditioned square footage',
        help_text='What is the final finished square footage of the structure(s) (for new construction and rehabs involving add-ons)',
        blank=True,
    )



    SINGLE_MULTI_CHOICES = (
        ('Single family', 'Single Family'),
        ('Multi-family', 'Multi-family (duplex, etc)'),

    )

    single_or_multi_family = models.CharField(
        max_length=254,
        verbose_name='Single or multi-family?',
        help_text='Will this home, when completed, be a single or multi-family (duplex, etc) home?',
        blank=True,
        choices=SINGLE_MULTI_CHOICES,
    )


    nsp_income_qualifier = models.CharField(
        max_length=255,
        verbose_name="Which entity will conduct the income qualification process for new tenants for this property?",
        help_text="Federal policies require that during the affordability period (5 years from your purchase), tenants must be at or below 120% of the Area Median Income. Verifying tenant income is a complicated process that must be completed by a qualified entity with experience in this field.  If your organization will do this itself, enter 'self'.",
        blank=True
    )

    why_this_house = models.CharField(
        max_length=5120,
        verbose_name="Why are you interseted in this specific property?",
        help_text="""
			Tell us why you want to buy this property in particular. What makes it desirable to you? What features do you especially like?
		""",
        blank=True
    )


    frozen = models.BooleanField(
        default=False,
        verbose_name='Freeze Application for Review',
        help_text="Frozen applications are ready for review and can not be edited by the applicant"
    )

    staff_notes = models.CharField(blank=True, max_length=1024)
    staff_sidelot_waiver_required = models.NullBooleanField(
        default=None,
        verbose_name='Staff field, if a waiver is required with the sidelot application',
    )
    staff_intent_neighborhood_notification = models.CharField(blank=True, max_length=10240)
    neighborhood_notification_details = models.CharField(blank=True, max_length=10240)
    neighborhood_notification_feedback = models.CharField(blank=True, max_length=10240)

    price_at_time_of_submission = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="The price of the property at time of submission", null=True, blank=True)

    #meeting is MeetingLink accessor

    def save(self, *args, **kwargs):
        if self.status == self.COMPLETE_STATUS and self.Property is not None and self.price_at_time_of_submission is None:
            if self.application_type == self.SIDELOT:
                self.price_at_time_of_submission = settings.COMPANY_SETTINGS['SIDELOT_PRICE']
            else:
                self.price_at_time_of_submission = self.Property.price
        if self.status == self.COMPLETE_STATUS and self.submitted_timestamp is None:
            self.submitted_timestamp = timezone.now()
        super(Application, self).save(*args, **kwargs)

    def __str__(self):
        if self.organization:
            return '%s - %s - %s' % (self.organization.name, self.user.email, self.Property)
        return '%s %s - %s - %s' % (self.user.first_name, self.user.last_name, self.user.email, self.Property)

class TransferApplication(Application):
    pass

@python_2_unicode_compatible
class Meeting(models.Model):
    REVIEW_COMMITTEE = 1
    BOARD_OF_DIRECTORS = 2
    MDC = 3
    RFP_COMMITTEE = 4
    PROCESSING = 5

    MEETING_TYPE_CHOICES = (
        (REVIEW_COMMITTEE, 'Review Committee'),
        (BOARD_OF_DIRECTORS, 'Board of Directors'),
        (MDC, 'Metropolitan Development Commission'),
        (RFP_COMMITTEE, 'RFP Committee'),
        (PROCESSING, '**Vetted**'),
    )

    meeting_date = models.DateField()
    meeting_type = models.IntegerField(choices=MEETING_TYPE_CHOICES)
    resolution_number = models.CharField(max_length=254, blank=True)

    def __str__(self):
        return '%s - %s' % (self.get_meeting_type_display(), self.meeting_date)

    class Meta:
        ordering = ['meeting_date']

@python_2_unicode_compatible
class MeetingLink(models.Model):

    APPROVED_STATUS = 1
    NOT_APPROVED_STATUS = 2
    TABLED_STATUS = 3
    SCHEDULED_STATUS = 4
    BACKUP_APPROVED_STATUS = 5

    STATUS_CHOICES = (
        (APPROVED_STATUS, 'Approved'),
        (NOT_APPROVED_STATUS, 'Not Approved'),
        (TABLED_STATUS, 'Tabled'),
        (SCHEDULED_STATUS, 'Scheduled'),
        (BACKUP_APPROVED_STATUS, 'Approved - Backup'),
    )

    NO_CONDITION = 1
    CONDITION = 2
    CONDITION_SATISFIED = 3

    CONDITIONAL_CHOICES = (
        (NO_CONDITION,'None'),
        (CONDITION,'Approved with conditions'),
        (CONDITION_SATISFIED,'Condition Satisfied'),
    )

    meeting = models.ForeignKey(Meeting, related_name='meeting_link', on_delete=models.CASCADE)
    meeting_outcome = models.IntegerField(choices=STATUS_CHOICES, null=False, default=SCHEDULED_STATUS)
    application = models.ForeignKey(Application, related_name='meeting', on_delete=models.CASCADE)
    notes = models.CharField(max_length=1024, blank=True, null=False)
    schedule_weight = models.IntegerField(default=0, null=False, blank=True)

    conditional_approval = models.IntegerField(choices=CONDITIONAL_CHOICES, null=False, default=NO_CONDITION)

    @property
    def meeting_date(self):
        return self.meeting.meeting_date

    def __str__(self):
        return '%s - %s' % (self.meeting, self.get_meeting_outcome_display())

    def save(self, *args, **kwargs):
        if self.application.status != Application.WITHDRAWN_STATUS: # If an application is withdrawn then don't update meetings, etc even if it was approved.

            schedule_next_meeting = True # We want to put the app on the agenda of the next appropriate meeting unless it receives final approval.

            if self.meeting_outcome == self.APPROVED_STATUS or self.meeting_outcome == self.BACKUP_APPROVED_STATUS:
                if (self.application.Property.renew_owned == False and self.meeting.meeting_type == Meeting.MDC) or (self.application.Property.renew_owned == True and self.meeting.meeting_type == Meeting.BOARD_OF_DIRECTORS):
                    # Final approval received
                    schedule_next_meeting = False
                    if self.meeting_outcome == self.APPROVED_STATUS:
                        closing = apps.get_model('closings', 'closing')
                        # No closing created yet
                        if closing.objects.filter(application=self.application).count()==0:
                            new_closing = closing(application=self.application)
                            new_closing.save()
                            # email applicant with congratulatory email and URL to pay processing fee
                        else:
                            old_closing = closing.objects.filter(application=self.application).order_by('date_time').first()
                            pf = old_closing.processing_fee.first()
                            pf.due_date = now()+timedelta(days=9)
                            pf.save()



            if self.meeting_outcome == self.APPROVED_STATUS:
                prop = self.application.Property
                body = self.meeting.get_meeting_type_display()
                if body == 'Metropolitan Development Commission':
                    body = 'MDC'
                date = self.meeting.meeting_date
                prop.status = 'Sale approved by {0} {1}'.format(body, date.strftime('%m/%d/%Y'))
                prop.buyer_application = self.application
                if self.application.organization:
                    prop.applicant = '{0} {1} - {2}'.format(self.application.user.first_name, self.application.user.last_name, self.application.organization)
                else:
                    prop.applicant = '{0} {1}'.format(self.application.user.first_name, self.application.user.last_name)
                prop.save()




                # If a property is listed in BLC, notify BLC manager if necessary to mark sale pending.
                if prop.blc_listing.count() > 0 and self.meeting.meeting_type == Meeting.REVIEW_COMMITTEE and settings.SEND_BLC_ACTIVITY_NOTIFICATION_EMAIL:
                        send_mail('BLC listed property pending - {}'.format(prop,), 'Property {} is BLC listed and was approved at the Review Committee. Update BLC as necessary.'.format(prop,), 'info@renewindianapolis.org',
                    [settings.BLC_MANAGER_EMAIL], fail_silently=False)

            # If application is rejected at the Board or MDC level then change the status to Available.
            # If we were to use this logic at the Review Committee level where there could be competing applications
            # then it will do bad things.
            if self.meeting_outcome == self.NOT_APPROVED_STATUS and (self.meeting.meeting_type == Meeting.BOARD_OF_DIRECTORS or self.meeting.meeting_type == Meeting.MDC):
                prop = self.application.Property
                prop.status = 'Available'
                prop.save()
                schedule_next_meeting = False

            if self.meeting.meeting_type == Meeting.PROCESSING:
                schedule_next_meeting = False


            if schedule_next_meeting == True and (self.meeting_outcome == self.TABLED_STATUS or self.meeting_outcome == self.APPROVED_STATUS or self.meeting_outcome == self.BACKUP_APPROVED_STATUS):
                notes = 'made by robot'
                # Tabled status means it goes back on the agenda for the next occurance of the same meeting
                if self.meeting_outcome == self.TABLED_STATUS:
                    meeting_type = self.meeting.meeting_type
                    notes = 'Tabled from {0}'.format(self.meeting.meeting_date,)
                # Approved means it goes on the agenda of the next occurance of the next level meeting
                if self.meeting_outcome == self.APPROVED_STATUS or self.meeting_outcome == self.BACKUP_APPROVED_STATUS:
                    if self.meeting_outcome == self.APPROVED_STATUS:
                        notes = 'Promoted from {0}'.format(self.meeting.meeting_date,)
                    if self.meeting_outcome == self.BACKUP_APPROVED_STATUS:
                        notes = 'Backup - Promoted from {0}'.format(self.meeting.meeting_date,)

                    if self.meeting.meeting_type == Meeting.REVIEW_COMMITTEE:
                        meeting_type = Meeting.BOARD_OF_DIRECTORS
                    if self.meeting.meeting_type == Meeting.BOARD_OF_DIRECTORS:
                        meeting_type = Meeting.MDC
                    if self.meeting.meeting_type == Meeting.PROCESSING:
                        meeting_type = Meeting.PROCESSING # users shouldn't use any status except scheduled for this fake meeting type.
                    if self.meeting.meeting_type == Meeting.MDC:
                        # We should never get here since approval stops at MDC
                        # if a renew owned property goes to MDC we will get an error, need to catch that
                        pass


                next_meeting = Meeting.objects.filter(meeting_type__exact=meeting_type).filter(meeting_date__gt=self.meeting.meeting_date).order_by('meeting_date').first()
                if next_meeting is None:
                    if meeting_type == Meeting.REVIEW_COMMITTEE:
                        meeting_date = rrule(MONTHLY, count=1, byweekday=TH(4), dtstart=self.meeting.meeting_date+timedelta(days=1))[0].date()
                    if meeting_type == Meeting.BOARD_OF_DIRECTORS:
                        meeting_date = rrule(MONTHLY, count=1, byweekday=TH(1), dtstart=self.meeting.meeting_date)[0].date()
                    if meeting_type == Meeting.MDC:
                        meeting_date = rrule(MONTHLY, count=1, byweekday=WE(3), dtstart=self.meeting.meeting_date)[0].date()
                    next_meeting = Meeting(meeting_type=meeting_type, meeting_date=meeting_date)
                    next_meeting.save()
                next_meeting_link = MeetingLink(
                    application=self.application,
                    meeting=next_meeting,
                    notes=notes,
                    schedule_weight=self.schedule_weight,
                    conditional_approval=self.conditional_approval,
                )
                next_meeting_link.save()
        super(MeetingLink, self).save(*args, **kwargs)

    class Meta:
        get_latest_by = 'meeting_date'

class ApplicationMeetingSummary(MeetingLink):
    class Meta:
        proxy = True
        verbose_name = 'Application Meeting Summary'
        verbose_name_plural = 'Application Meeting Summaries'


"""
Sure would be nice to just inherient from MeetingLink and override application but not allowed except on abstract models so we have a lot of code duplication.
"""
@python_2_unicode_compatible
class PriceChangeMeetingLink(models.Model):
    APPROVED_STATUS = 1
    NOT_APPROVED_STATUS = 2
    TABLED_STATUS = 3
    SCHEDULED_STATUS = 4

    STATUS_CHOICES = (
        (APPROVED_STATUS, 'Approved'),
        (NOT_APPROVED_STATUS, 'Not Approved'),
        (TABLED_STATUS, 'Tabled'),
        (SCHEDULED_STATUS, 'Scheduled'),
    )
    meeting = models.ForeignKey(Meeting, related_name='price_change_meeting_link', on_delete=models.CASCADE)
    meeting_outcome = models.IntegerField(choices=STATUS_CHOICES, null=False, default=SCHEDULED_STATUS)
    price_change = models.ForeignKey('property_inventory.price_change', related_name='meeting', on_delete=models.CASCADE)
    notes = models.CharField(max_length=1024, blank=True, null=False)

    @property
    def meeting_date(self):
        return self.meeting.meeting_date

    def __str__(self):
        return '%s - %s' % (self.meeting, self.get_meeting_outcome_display())

    # When saving this intermediary linkage object we save it and update the price_change and property_object to reflect approval, if given.
    def save(self, *args, **kwargs):
        super(PriceChangeMeetingLink, self).save(*args, **kwargs)

        chng = self.price_change
        if chng.approved != True and self.meeting_outcome == self.APPROVED_STATUS:
            chng.approved = True
            chng.save()

            prop = self.price_change.Property
            prop.price = self.price_change.proposed_price
            if chng.make_fdl_eligible == True:
                prop.future_development_program_eligible = True
            prop.save()

    class Meta:
        get_latest_by = 'meeting_date'
