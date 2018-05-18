from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotAllowed, JsonResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import serializers
from django.core.serializers.json import Serializer
#from django.core.serializers.json import DjangoJSONEncoder
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.utils.encoding import is_protected_type
import os
from django.forms import inlineformset_factory


from .forms import ApplicationForm
#from user_files.forms import UploadedFileForm
from .models import Application, Meeting, MeetingLink
from property_inventory.models import Property
from applicants.models import ApplicantProfile
from user_files.models import UploadedFile
from closings.models import processing_fee

from django.contrib.auth.models import User


# used to send confirmation email
from django.core.mail import send_mail
from django.template.loader import render_to_string

from pprint import pprint
import zipfile
import tempfile
from django.utils.text import slugify

from django.views.generic import DetailView, View, UpdateView

import datetime
from dateutil.rrule import *
from dateutil.relativedelta import *

def determine_next_deadline_date():
    next_deadline = datetime.date(2017, 1, 1)
    next_meeting = datetime.date(2017, 1, 1)
    i = 0
    while (next_deadline <= datetime.date.today()):
        start = datetime.date.today()+relativedelta(days=i)
        next_meeting = rrule(MONTHLY, count=1, byweekday=TH(4), dtstart=start)[0].date()
        next_deadline = next_meeting-relativedelta(weekday=FR(-3))
        i=i+1
    return [next_meeting, next_deadline]


def determine_next_meeting_date():
    next_deadline = datetime.date(2007, 1, 1)
    next_meeting = datetime.date(2017, 1, 1)
    i = 0
    while (next_meeting <= datetime.date.today()):
        start = datetime.date.today()+relativedelta(days=i)
        next_meeting = rrule(MONTHLY, count=1, byweekday=TH(4), dtstart=start)[0].date()
        next_deadline = next_meeting-relativedelta(weekday=FR(-3))
        i=i+1
    return [next_meeting, next_deadline]


@login_required
def process_application(request, action, id=None):
    if action == 'edit':
        app = get_object_or_404(Application, id=id, user=request.user)
        if app.frozen == True:
            return HttpResponse("This application has been submitted and can not be editted. To unfreeze this application email {0} at {1}.".format(settings.COMPANY_SETTINGS['APPLICATION_CONTACT_NAME'], settings.COMPANY_SETTINGS['APPLICATION_CONTACT_EMAIL']), status=403)
        form = ApplicationForm(instance=app, user=request.user, id=app.pk)
    if action == 'new':
        # see if they already have an application with initial status, if so use that one again, if not create one.
        # Problem - multiple browser windows, or multiple browsers (eg start app on phone, continue on computer, then save phone app before computer app,
        # they share an ID and will overwrite each other. So not doing this for now. We'll see if it is a problem having a blank app saved for each app start
        # try:
        # 	app = Application.objects.get(user.request=user, status=Application.INITIAL_STATUS).first()
        # except model.DoesNotExist:
        # 	app = Application(user=request.user, status=Application.INITIAL_STATUS)
        # 	app.save()
        parcel = request.GET.get('parcel', None)
        if parcel:
            try:
                prop = Property.objects.filter(parcel=parcel).exclude(
                    status__contains='Sale approved by MDC').exclude(
                    is_active__exact=False).exclude(
                    status__contains='Sold').exclude(
                    status__contains='BEP').exclude(
                    status__contains='Sale approved by Board of Directors', renew_owned=True).first()
            except Property.DoesNotExist:
                raise Http404("Property does not exist or is not eligible for application")
            app = Application(user=request.user, status=Application.INITIAL_STATUS, Property=prop)
        else:
            app = Application(user=request.user, status=Application.INITIAL_STATUS)
        app.save()
        form = ApplicationForm(instance=app, user=request.user, id=app.pk)
    if action == 'save':
        if request.method != 'POST':
            return HttpResponseNotAllowed('Error - POST required to save')
        app = get_object_or_404(Application, id=id, user=request.user)
        if app.frozen == True:
            return HttpResponse("This application has been submitted and can not be editted. To unfreeze this application email {0} at {1}.".format(settings.COMPANY_SETTINGS['APPLICATION_CONTACT_NAME'], settings.COMPANY_SETTINGS['APPLICATION_CONTACT_EMAIL']), status=403)
        form = ApplicationForm(request.POST, request.FILES,
                               user=request.user, instance=app, id=app.pk)
        if form.is_valid():
            application = form.save(commit=False)
            if application.status == Application.INITIAL_STATUS:
                application.status = Application.ACTIVE_STATUS
            save_for_later = request.POST.get('save_for_later')
            if not save_for_later:  # they want to submit the application
                if form.validate_for_submission(id=application.id):
                    #application.frozen = True
                    application.status = Application.COMPLETE_STATUS
                    application.save()
                    applicant_email = request.user.email
                    property_address = app.Property
                    msg_plain = render_to_string('email/application_submitted.txt', {
                        'user': request.user,
                        'Property': property_address,
                        'application': application,
                        'COMPANY_SETTINGS': settings.COMPANY_SETTINGS,
                    }
                    )
                    send_mail(
                        'Application received: {0}'.format(property_address),
                        msg_plain,
                        'info@renewindianapolis.org',
                        [applicant_email],
                    )
                    return HttpResponseRedirect(reverse('application_confirmation', args=(id,)))
                else:
                    "*!*!* validate_for_submission() returned false"

            application.frozen = False
            application.save()

    uploaded_files_sow = UploadedFile.objects.filter(
        user=request.user, application=app.id, file_purpose=UploadedFile.PURPOSE_SOW)
    uploaded_files_pof = UploadedFile.objects.filter(
        user=request.user, application=app.id, file_purpose=UploadedFile.PURPOSE_POF)
    uploaded_files_all = UploadedFile.objects.filter(
        user=request.user, application=app.id)

    return render(request, 'application.html', {
        'form': form,
        'app_id': app.id,
        'uploaded_files_sow': uploaded_files_sow,
        'uploaded_files_pof': uploaded_files_pof,
        'uploaded_files_all': uploaded_files_all,
        'title': 'application',
        'COMPANY_SETTINGS': settings.COMPANY_SETTINGS,
        'next_deadline': determine_next_deadline_date()[1],
        'next_meeting': determine_next_deadline_date()[0],
    })


# no longer needed since switching to admin app instead of home rolled dataTables
class DisplayNameJsonSerializer(Serializer):

    def handle_field(self, obj, field):
        value = field._get_val_from_obj(obj)
        display_method = "get_%s_display" % field.name
        if hasattr(obj, display_method):
            self._current[field.name] = getattr(obj, display_method)()
        elif is_protected_type(value):
            self._current[field.name] = value
        else:
            self._current[field.name] = field.value_to_string(obj)

@login_required
def application_confirmation(request, id):
    app = get_object_or_404(Application, id=id, user=request.user)
    return render(request, 'confirmation.html', {
        'title': 'thank you',
        'Property': app.Property,
        'COMPANY_SETTINGS': settings.COMPANY_SETTINGS,
    })

class ApplicationDetail(DetailView):
    model = Application
    context_object_name = 'application'
    template_name = 'application_display.html'

class ApplicationDisplay(DetailView):
    model = Application
    context_object_name = 'application'
    template_name = 'application_detail.html'

class ApplicationNeighborhoodNotification(DetailView):
    model = Application
    context_object_name = 'application'
    template_name = 'neighborhood_notification.html'

class ApplicationPurchaseAgreement(DetailView):
    model = Application
    context_object_name = 'application'
    template_name = 'purchase_agreement.html'

class ReviewCommitteeAgenda(DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'rc_agenda.html'

class ReviewCommitteeStaffSummary(DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'application_display_all.html'

class ReviewCommitteeApplications(DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'application_detail_all.html'


class CreateMeetingSupportArchive(View):
    def get(self, request, *args, **kwargs):
        meeting_id = self.kwargs['pk']
        meeting = get_object_or_404(Meeting, id=meeting_id)
        with tempfile.SpooledTemporaryFile() as tmp:
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as myzip:
                for meeting_link in meeting.meeting_link.all():
                    application = meeting_link.application
                    uploaded_files = UploadedFile.objects.filter(application=application).exclude(file_purpose=UploadedFile.PURPOSE_POF)
                    for uploaded_file in uploaded_files:
                        filename = str(uploaded_file.supporting_document.name)
                        if filename.startswith('/') != True:
                            filename = settings.MEDIA_ROOT+filename
                        archive_filename = '{0}_{1}/{2}'.format(slugify(application.Property), slugify(application.user.first_name+' '+application.user.last_name), os.path.basename(filename))
                        myzip.write(filename, archive_filename)
            tmp.seek(0)
            response = HttpResponse(tmp.read(), content_type='application/x-zip-compressed')
            response['Content-Disposition'] = 'attachment; filename="{0}.zip"'.format(meeting,)
            return response


import csv
class PriceChangeCSVResponseMixin(object):
    """
    A mixin that constructs a CSV response from the context data if
    the CSV export option was provided in the request.
    """
    def render_to_response(self, context, **response_kwargs):
        """
        Creates a CSV response if requested, otherwise returns the default
        template response.
        """
        # Sniff if we need to return a CSV export
        if 'csv' in self.request.GET.get('export', ''):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}"'.format(slugify(context['meeting']), 'price-changes.csv')
            writer = csv.writer(response)

            header = ['Property', 'Structure Type', 'Current Price', 'Proposed Price', 'Price Difference']
            writer.writerow(header)
            price_change_total = 0
            # Write the data from the context somehow
            for price_change_link in context['meeting'].price_change_meeting_link.all():
                price_change = price_change_link.price_change.proposed_price - price_change_link.price_change.Property.price
                price_change_total = price_change_total + price_change
                row = [price_change_link.price_change.Property, price_change_link.price_change.Property.structureType, price_change_link.price_change.Property.price, price_change_link.price_change.proposed_price, price_change]
                writer.writerow(row)
            writer.writerow(['Total Change', price_change_total])
            return response
        # Business as usual otherwise
        else:
            return super(PriceChangeCSVResponseMixin, self).render_to_response(context, **response_kwargs)

class PriceChangeSummaryAll(PriceChangeCSVResponseMixin, DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'price_change_summary_view_all.html'

class CreateMeetingPriceChangeCMAArchive(View):
    def get(self, request, *args, **kwargs):
        meeting_id = self.kwargs['pk']
        meeting = get_object_or_404(Meeting, id=meeting_id)
        with tempfile.SpooledTemporaryFile() as tmp:
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as myzip:
                for price_change_link in meeting.price_change_meeting_link.all():
                    filename = str(price_change_link.price_change.cma.name)
                    #print price_change_link.price_change.cma
                    if price_change_link.price_change.cma.name == 'None':
                        pass
                    if filename.startswith('/') != True:
                        filename = settings.MEDIA_ROOT+filename
                    #print price_change_link.price_change
                    #print filename
                    archive_filename = '{0}.pdf'.format(slugify(price_change_link.price_change),)
                    try:
                        myzip.write(filename, archive_filename)
                    # if the file can't be opened or doesn't exist, eg in testing environment, then skip it.
                    except OSError:
                        pass
            tmp.seek(0)
            response = HttpResponse(tmp.read(), content_type='application/x-zip-compressed')
            response['Content-Disposition'] = 'attachment; filename="{0}-CMAs.zip"'.format(meeting,)
            return response


import csv
from decimal import *
class MDCCSVResponseMixin(object):
    """
    A mixin that constructs a CSV response from the context data if
    the CSV export option was provided in the request. In this case to create the
    MDC spreadsheet.
    """
    def render_to_response(self, context, **response_kwargs):
        """
        Creates a CSV response if requested, otherwise returns the default
        template response.
        """
        # Sniff if we need to return a CSV export
        if 'csv' in self.request.GET.get('export', ''):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}"'.format(slugify(context['meeting']), 'MDC-for-resolution.csv')
            writer = csv.writer(response)

            header = ['Parcel','Street Address','Application Type','Structure Type','City\'s Sale Price','Renew\'s Sale Price','Total','Buyer Name']
            writer.writerow(header)
            # Write the data from the context somehow
            #from applications.models import MeetingLink.APPROVED_STATUS
            for meeting_link in context['meeting'].meeting_link.all().order_by('application__application_type').filter(application__Property__renew_owned__exact=False).filter(meeting_outcome=MeetingLink.SCHEDULED_STATUS):
                application = meeting_link.application

                # Price is locked at time of submission, but older apps might
                # not have a price, so use the property price then.
                if application.price_at_time_of_submission is None:
                    property_price = application.Property.price
                else:
                    property_price = application.price_at_time_of_submission

                if property_price >= 3500:
                    price = property_price
                    city_split = round(price*Decimal('.55'))
                    renew_split = Decimal(price)-Decimal(city_split)
                # elif property_price == 3500.0:
                #     price = property_price
                #     city_split = 1000.00
                #     renew_split = 2500.00
                elif property_price == 750.0:
                    price = property_price
                    city_split = 250.00
                    renew_split = 500.00
                else: # Error case, should catch people's attention to fix manually
                    city_split = 0
                    renew_split = 0
                total = Decimal(city_split)+Decimal(renew_split)
                if application.organization:
                    buyer = '{0} {1}, {2}'.format(application.user.first_name, application.user.last_name, application.organization.name)
                else:
                    buyer = '{0} {1}'.format(application.user.first_name, application.user.last_name)
                row = [application.Property.parcel, application.Property.streetAddress, application.get_application_type_display(), application.Property.structureType, city_split, renew_split, total, buyer]
                writer.writerow(row)
            return response
        # Business as usual otherwise
        else:
            return super(MDCCSVResponseMixin, self).render_to_response(context, **response_kwargs)


class MDCSpreadsheet(MDCCSVResponseMixin, DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'price_change_summary_view_all.html'

# Meeting Outcome Notification CSV Response Mixin
class MONCSVResponseMixin(object):
    """
    A mixin that constructs a CSV response from the context data if
    the CSV export option was provided in the request.
    """
    def render_to_response(self, context, **response_kwargs):
        """
        Creates a CSV response if requested, otherwise returns the default
        template response.
        """
        # Sniff if we need to return a CSV export
        if 'csv' in self.request.GET.get('export', ''):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}"'.format(slugify(context['meeting']), 'notification-merge-template.csv')
            writer = csv.writer(response)

            header = ['First Name', 'Email Address', 'Property', 'Renew Owned', 'Status', 'Reason', 'Sidelot', 'Link']
            #header = ['Parcel','Street Address','Application Type','Structure Type','City\'s Sale Price','Renew\'s Sale Price','Total','Buyer Name']
            writer.writerow(header)
            # Write the data from the context somehow
            #from applications.models import MeetingLink.APPROVED_STATUS
            for meeting_link in context['meeting'].meeting_link.all().order_by('application__application_type'):
                application = meeting_link.application
                user_name = '{0} {1}'.format(application.user.first_name, application.user.last_name)
                sidelot_text = ''
                if application.application_type in(Application.SIDELOT, Application.VACANT_LOT):
                    sidelot_text = 'Since this is a sidelot or vacant lot program application you have the option of closing directly with Renew Indianapolis, rather than with a title company.'
                try:
                    pf = processing_fee.objects.get(closing__application__exact=application)
                    pf_link = 'https://www.renewindianapolis.org{0}'.format(
                        reverse("application_pay_processing_fee", args=(slugify(pf.slug), pf.id,)),)
                except processing_fee.DoesNotExist:
                    pf_link = ''
                row = [user_name, application.user.email, application.Property, application.Property.renew_owned, meeting_link.get_meeting_outcome_display(), '', sidelot_text, pf_link]
                #row = [application.Property.parcel, application.Property.streetAddress, application.get_application_type_display(), application.Property.structureType, city_split, renew_split, total, buyer]
                writer.writerow(row)
            return response
        # Business as usual otherwise
        else:
            return super(MONCSVResponseMixin, self).render_to_response(context, **response_kwargs)


class MeetingOutcomeNotificationSpreadsheet(MONCSVResponseMixin, DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'price_change_summary_view_all.html'

import xlsxwriter
from io import BytesIO
class ePPPropertyUpdate(DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'price_change_summary_view_all.html'

    def render_to_response(self, context, **response_kwargs):
        header = ['Parcel Number', 'Property Status', 'Property Class', 'Owner Party Number', 'Owner Party External System Id', 'Property Address.Address1', 'Property Address.Address2', 'Property Address.City', 'Property Address.County', 'Property Address.State', 'Property Address.Postal Code', 'Status Date', 'Property Manager Party Number', 'Property Manager Party External System Id', 'Update', 'Available', 'Foreclosure Year', 'Inventory Type', 'Legal Description', 'Listing Comments', 'Maintenance Manager Party External System Id', 'Maintenance Manager Party Number', 'Parcel Square Footage', 'Parcel Length', 'Parcel Width', 'Published', 'Tags', 'Latitude', 'Longitude', 'Parcel Boundary', 'Census Tract', 'Congressional District', 'Legislative District', 'Local District', 'Neighborhood', 'School District', 'Voting Precinct', 'Zoned As', 'Acquisition Amount', 'Acquisition Date', 'Acquisition Method', 'Sold Amount', 'Sold Date', 'Actual Disposition', 'Asking Price', 'Assessment Year', 'Current Assessment', 'Minimum Bid Amount', 'Block Condition', 'Brush Removal', 'Cleanup Assessment', 'Demolition Needed', 'Environmental Cleanup Needed', 'Market Condition', 'Potential Use', 'Property Condition', 'Property of Interest', 'Quiet Title', 'Rehab Candidate', 'Target Disposition', 'Trash Removal ', 'Custom.BEP Mortgage Expiration Date', 'Custom.BLC Number', 'Custom.CDC', 'Custom.Grant Program', 'Custom.Sales Program'
        ]

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('PropertyDescription')
        text_format = workbook.add_format({'num_format': '@'})

        for i in range(len(header)):
            worksheet.write(0, i, header[i])

        max_index = 0
        for index,price_change_link in enumerate(context['meeting'].price_change_meeting_link.all().filter(meeting_outcome=1), 1):
            price_change = price_change_link.price_change
            worksheet.write(index, header.index('Parcel Number'), price_change.Property.parcel, text_format)
            worksheet.write(index, header.index('Update'), 'Y')
            worksheet.write(index, header.index('Asking Price'), price_change.proposed_price)
            max_index = index

            ## This changes the property status if approved to Sale Pending. This works at all stages b/c
        for index,meeting_link in enumerate(context['meeting'].meeting_link.all().order_by('-meeting_outcome').exclude(meeting_outcome=4), max_index+1):
            application = meeting_link.application
            if meeting_link.meeting_outcome == MeetingLink.APPROVED_STATUS:
                status = 'Sale Pending'

            # If this is the first stage of review then status should already be available but it doesn't hurt to re-set it
            if meeting_link.meeting_outcome == MeetingLink.NOT_APPROVED_STATUS:
                status = 'Available'

            worksheet.write(index, header.index('Parcel Number'), application.Property.parcel, text_format)
            worksheet.write(index, header.index('Update'), 'Y')
            worksheet.write(index, header.index('Property Status'), status, text_format)


        workbook.close()
        response = HttpResponse(output.getvalue(), content_type='application/application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="price_change.xlsx"'
        return response



class ePPPartyUpdate(DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'price_change_summary_view_all.html'

    def render_to_response(self, context, **response_kwargs):
        person_header = ['First Name', 'Last Name', 'Party Number', 'External System Id', 'Organization External System Id', 'Organization Party Number', 'Update', 'Address.Address 1', 'Address.City', 'Address.State', 'Address.Postal Code', 'Address.Address 2', 'Address.Country', 'Address.County', 'Address.Latitude', 'Address.Longitude', 'Email', 'Function', 'Middle', 'Prefix', 'Suffix', 'Telephone', 'TIN', 'Title']
        organization_header = ['Class', 'Legal Name', 'Contact.First Name', 'Contact.Last Name', 'Party Number', 'External System Id', 'Contact.External System Id', 'Update', 'Address.Address 1', 'Address.City', 'Address.State', 'Address.Postal Code', 'Address.Address 2', 'Address.Country', 'Address.County', 'Address.Latitude', 'Address.Longitude', 'Business Type', 'DBA Name', 'DUNS', 'EIN', 'Email', 'Function', 'Industry', 'Telephone']


        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        person_worksheet = workbook.add_worksheet('Person')
        organization_worksheet = workbook.add_worksheet('Organization')
        text_format = workbook.add_format({'num_format': '@'})

        for i in range(len(person_header)):
            person_worksheet.write(0, i, person_header[i])

        for i in range(len(organization_header)):
            organization_worksheet.write(0, i, organization_header[i])


            ## This gets all the applications at the meeting and creates one row in the appropriate sheet for each application.
            ## This does create duplication and blank rows but that doesn't matter because ePP skips them both.
        organization_index = 1
        person_index = 1
        for index,meeting_link in enumerate(context['meeting'].meeting_link.all().order_by('application__application_type'), 1):
            application = meeting_link.application
            if application.organization is None:
                person_worksheet.write(person_index, person_header.index('First Name'), application.user.first_name, text_format)
                person_worksheet.write(person_index, person_header.index('Last Name'), application.user.last_name, text_format)
                person_worksheet.write(person_index, person_header.index('External System Id'), application.user.profile.external_system_id, text_format)
                person_worksheet.write(person_index, person_header.index('Address.Address 1'), application.user.profile.mailing_address_line1, text_format)
                person_worksheet.write(person_index, person_header.index('Address.City'), application.user.profile.mailing_address_city, text_format)
                person_worksheet.write(person_index, person_header.index('Address.State'), application.user.profile.mailing_address_state, text_format)
                person_worksheet.write(person_index, person_header.index('Address.Postal Code'), application.user.profile.mailing_address_zip, text_format)
                person_worksheet.write(person_index, person_header.index('Address.Address 2'), application.user.profile.mailing_address_line2, text_format)
                person_worksheet.write(person_index, person_header.index('Email'), application.user.email, text_format)
                person_worksheet.write(person_index, person_header.index('Function'), 'Owner|Buyer', text_format)
                person_worksheet.write(person_index, person_header.index('Telephone'), application.user.profile.phone_number, text_format)
                person_index = person_index + 1
            else:
                organization_worksheet.write(organization_index,organization_header.index('Class'), 'External', text_format)
                organization_worksheet.write(organization_index,organization_header.index('Legal Name'), application.organization.name, text_format)
                organization_worksheet.write(organization_index,organization_header.index('Contact.First Name'), application.user.first_name, text_format)
                organization_worksheet.write(organization_index,organization_header.index('Contact.Last Name'), application.user.last_name, text_format)
                organization_worksheet.write(organization_index,organization_header.index('External System Id'), application.organization.external_system_id, text_format)
                person_worksheet.write(organization_index, person_header.index('Address.Address 1'), application.organization.mailing_address_line1, text_format)
                person_worksheet.write(organization_index, person_header.index('Address.City'), application.organization.mailing_address_city, text_format)
                person_worksheet.write(organization_index, person_header.index('Address.State'), application.organization.mailing_address_state, text_format)
                person_worksheet.write(organization_index, person_header.index('Address.Postal Code'), application.organization.mailing_address_zip, text_format)
                person_worksheet.write(organization_index, person_header.index('Address.Address 2'), application.organization.mailing_address_line2, text_format)
                person_worksheet.write(organization_index, person_header.index('Email'), application.organization.email, text_format)
                person_worksheet.write(organization_index, person_header.index('Function'), 'Owner|Buyer', text_format)
                person_worksheet.write(organization_index, person_header.index('Telephone'), application.organization.phone_number, text_format)
                organization_index = organization_index + 1


        workbook.close()
        response = HttpResponse(output.getvalue(), content_type='application/application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="party-import.xlsx"'
        return response

from neighborhood_notifications.models import registered_organization, blacklisted_emails
from user_files.models import UploadedFile
from django.db.models import Q
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib import messages
class GenerateNeighborhoodNotifications(DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'price_change_summary_view_all.html'
    #form = None
    #fields = []

    #def post()

    #def get_success_url(self):
    #    messages.add_message(self.request, messages.INFO, 'Neighborhood notifications sent.')
    #    return reverse("generate_neighborhood_notifications", kwargs={'pk': self.kwargs['pk']})

    def render_to_response(self, context, **response_kwargs):
        applications = []
        for index,meeting_link in enumerate(context['meeting'].meeting_link.all().order_by('application__application_type'), 1):
            application = meeting_link.application
            if application.neighborhood_notification_details != '':
                continue
            applications.append(application)
            orgs = registered_organization.objects.filter(geometry__contains=application.Property.geometry).exclude(email='n/a').order_by('-geometry')

            recipient = []
            org_names = []
            for o in orgs:
                if o.email and blacklisted_emails.objects.filter(email=o.email).count() == 0: # check if email exists in blacklist (bounces, opt-out, etc)
                    recipient.append(o.email)
                    org_names.append(o.name)
                else:
                    pass

            subject = 'Neighborhood Notification - {0}'.format(application.Property,)
            from_email = 'info@renewindianapolis.org'
            message = render_to_string('email/neighborhood_notification_email.txt', {'application': application})

            email = EmailMessage(
                subject,
                message,
                from_email,
                recipient,
                reply_to=[settings.COMPANY_SETTINGS['APPLICATION_CONTACT_EMAIL']]
            )

            files = UploadedFile.objects.filter(application=application).filter(send_with_neighborhood_notification=True)
            for f in files:
                if settings.DEBUG: # application media files don't exist in testing environment, so attach dummy file.
                    email.attach_file('/tmp/blank.txt')
                else:
                    email.attach_file(f.supporting_document.path)
            #print "Send?", self.request.GET.get('send')
            if self.request.GET.get('send') == 'True':
                email.send()
            #    print 'Sent email'
                new_notifications = ', '.join(org_names)
                application.neighborhood_notification_details = application.neighborhood_notification_details + new_notifications
                application.save()

        context['applications'] = applications
        return render(self.request, 'neighborhood_notification_preview.html', context)

class GenerateNeighborhoodNotificationsVersion2(DetailView):
    model = Meeting
    context_object_name = 'meeting'
    template_name = 'price_change_summary_view_all.html'
    #form = None
    #fields = []

    #def post()

    #def get_success_url(self):
    #    messages.add_message(self.request, messages.INFO, 'Neighborhood notifications sent.')
    #    return reverse("generate_neighborhood_notifications", kwargs={'pk': self.kwargs['pk']})

    def render_to_response(self, context, **response_kwargs):
        applications = []
        for index,meeting_link in enumerate(context['meeting'].meeting_link.all().order_by('application__application_type'), 1):
            application = meeting_link.application
            applications.append(application)

        orgs = []
        for org in registered_organization.objects.all():

            if blacklisted_emails.objects.filter(email=org.email).count() != 0: # check if email exists in blacklist (bounces, opt-out, etc)
                break

            apps_in_area = []
            for app in applications:
                if registered_organization.objects.filter(geometry__contains=app.Property.geometry).filter(id=org.id):
                    apps_in_area.append(app)
            if len(apps_in_area) == 0:
                print "No apps in", org.name
                break
            orgs.append( (org, apps_in_area) )
            subject = 'Neighborhood Notifications - Renew Indianapolis'
            from_email = 'info@renewindianapolis.org'
            message = render_to_string('email/neighborhood_notification_email_single_org.txt', {'applications': apps_in_area})

            email = EmailMessage(
                subject,
                message,
                from_email,
                [org.email,],
                reply_to=[settings.COMPANY_SETTINGS['APPLICATION_CONTACT_EMAIL']]
            )

            files = UploadedFile.objects.filter(application=application).filter(send_with_neighborhood_notification=True)
            for f in files:
                if settings.DEBUG: # application media files don't exist in testing environment, so attach dummy file.
                    email.attach_file('/tmp/blank.txt')
                else:
                    email.attach_file(f.supporting_document.path)
            #print "Send?", self.request.GET.get('send')
            if self.request.GET.get('send') == 'True':
                email.send()
            #    print 'Sent email'
                for app in apps_in_area:
                    app.neighborhood_notification_details = '{} {}'.format(app.neighborhood_notification_details,o.name)
                    app.save()

        #context['applications'] = applications
        context['organizations'] = orgs
        return render(self.request, 'neighborhood_notification_preview_single_org.html', context)
