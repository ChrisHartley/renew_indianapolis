from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator

from django_tables2_reports.config import RequestConfigReport as RequestConfig

from django.core.urlresolvers import reverse

from django.core.mail import send_mail
from django.template.loader import render_to_string
from ipware import get_client_ip

from property_inquiry.models import propertyInquiry, propertyShowing
from property_inventory.models import Property
from property_inquiry.filters import PropertyInquiryFilters
from property_inquiry.tables import PropertyInquiryTable
from property_inquiry.forms import PropertyInquiryForm
from applicants.models import ApplicantProfile

from django.views import View

from django.conf import settings
from django.contrib import messages
import datetime
from django.utils import timezone # timezone aware now()

# Displays form template for property inquiry submissions, and saves those
# submissions
@login_required
def submitPropertyInquiry(request):
    parcel = request.GET.get('parcel', None)
    if parcel:
        try:
            prop = Property.objects.filter(status__contains='Available').exclude(
                structureType__contains='Vacant Lot').exclude(structureType__contains='Detached Garage/Boat House').exclude(is_active__exact=False).filter(parcel__exact=parcel).first()
        except Property.DoesNotExist:
            raise Http404("Property does not exist or is not eligible for property inquiry")
        #print prop
        form = PropertyInquiryForm(initial = {'Property': prop})
    else:
        form = PropertyInquiryForm()

    if request.method == 'POST':
        previousPIcount = propertyInquiry.objects.filter(user=request.user).filter(timestamp__gt=timezone.now()-datetime.timedelta(hours=48)).count()

        #print "Previous PI count:", previousPIcount
        form = PropertyInquiryForm(request.POST)
        duplicate_pi = propertyInquiry.objects.filter(user=request.user).filter(timestamp__gt=timezone.now()-datetime.timedelta(hours=72)).filter(Property=request.POST['Property']).count()
        if duplicate_pi > 0:
            form.add_error(None, "You submitted a request for this property within the past 72 hours. Due to volume it may take 5+ business days to schedule your inquiry, there is no need to re-submit.")
        if previousPIcount >= 3: # limit number of requests per time period
            form.add_error(None, "You can not submit more than 3 property inquiries every 48 hours. Please try again later.")
        if form.is_valid():
            form_saved = form.save(commit=False)
            form_saved.applicant_ip_address = get_client_ip(request)[0]
            form_saved.user = request.user
            form_saved.save()
            message_body = render_to_string('email/property_inquiry_confirmation.txt', {'Property': form_saved.Property })
            message_subject = 'Inquiry Received - {0}'.format(form_saved.Property)
            send_mail(message_subject, message_body, 'info@renewindianapolis.org', [form_saved.user.email,], fail_silently=False)
            return HttpResponseRedirect(reverse('property_inquiry_confirmation', args=(form_saved.id,)))
    return render(request, 'property_inquiry.html', {
        'form': form,
        'title': 'property visit',
        'form_enabled': settings.PROPERTY_INQUIRIES_ENABLED
    })


@login_required
def property_inquiry_confirmation(request, id):
    inquiry = get_object_or_404(propertyInquiry, id=id, user=request.user)
    return render(request, 'property_inquiry_confirmation.html', {
        'title': 'thank you',
        'Property': inquiry.Property,
    })


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client import file, client, tools
import logging
def publish_to_public_calendar(event, pk):
    calendar_id = 'renewindianapolis.org_pmmt30l2g1lm606tl88gt6sc04@group.calendar.google.com'
    e = {
        'summary': event['summary'],
        'location': event['location'],
#        'description': event['description'], # not published because it includes contact information
        'start': {
            'dateTime': event['dtstart'].dt.isoformat(),
            'timeZone': '',
        },
        'end': {
            'dateTime': event['dtend'].dt.isoformat(),
            'timeZone': '',
        }

    }
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('blight_fight/token.json')
    creds = store.get()
    logger = logging.getLogger(__name__)

    if not creds or creds.invalid:
        # this obviously won't work since there is no browser to open. Need
        # to log as an error
#        flow = client.flow_from_clientsecrets('blight_fight/google_api_credentials.json', SCOPES)
#        creds = tools.run_flow(flow, store)
        logger.error('Error with Google API token.json - creds not found or invalid')
    for i in range(5):
        try:
            service = build('calendar', 'v3', http=creds.authorize(Http()))
            e = service.events().insert(calendarId=calendar_id, body=e).execute()
        except HttpError as e:
            time.sleep(2)
            logger.warning('HttpError calling Google Calendar API')
            continue
        else:
            ps = propertyShowing.objects.get(id=pk)
            ps.google_calendar_event_id = e.get('id')
            ps.save()
        break




from icalendar import Calendar, Event, vCalAddress, vText
from datetime import timedelta
from operator import itemgetter, attrgetter
from itertools import groupby
from django.utils.timezone import now
from django.utils.text import slugify
from django.contrib.auth.models import User
@method_decorator(staff_member_required, name='dispatch')
class CreateIcsFromShowing(View):
    def get(self, request, pk):

        obj = propertyShowing.objects.get(pk=pk)
        data = sorted(obj.inquiries.all(), key=attrgetter('user'))
        props = []
        props_addresses = []
        for k,g in groupby(data, attrgetter('Property')):
            props.append(k)
            props_addresses.append(k.streetAddress)
        data = sorted(obj.inquiries.all(), key=attrgetter('user'))
        users = []
        for k,g in groupby(data, attrgetter('user')):
            users.append(k)

        c = Calendar()
        e = Event()
        c.add('prodid', '-//Renew Indianapolis//Property Showings//EN')
        c.add('version', '2.0')
        e.add('summary', '{} - Property Showing'.format(','.join(props_addresses),).title() )
        e.add('uid', obj.id)
        e.add('dtstart', obj.datetime)
        e.add('dtend', obj.datetime+timedelta(minutes=30))
        e.add('dtstamp', now())
        e.add('location', '{0}, Indianapolis, IN'.format(','.join(props_addresses),))
        people = []
        organizer = vCalAddress('MAILTO:{}'.format(request.user.email,))
        organizer.params['cn'] = vText(u'{} {}'.format(request.user.first_name, request.user.last_name))
        e.add('organizer', organizer, encode=0)


        for u in users:
            try:
                people.append(u'{} {} - {} {}'.format(u.first_name, u.last_name, u.email, u.profile.phone_number))
            except ApplicantProfile.DoesNotExist:
                people.append(u'{} {} - {}'.format(u.first_name, u.last_name, u.email))
            attendee = vCalAddress('MAILTO:{}'.format(u.email,))
            attendee.params['cn'] = vText(u'{} {}'.format(u.first_name, u.last_name))
    #        e.add('attendee', attendee, encode=0)

        for staff in settings.COMPANY_SETTINGS['city_staff']:
            a = vCalAddress('MAILTO:{}'.format(staff['email'],))
            a.params['cn'] = vText(staff['name'])
            e.add('attendee', a, encode=0)
        description = render_to_string('property_inquiry/property_showing_ics_description.txt', {'showing': self, 'properties': props, 'users': users})
        e.add('description', description )
        e.add('status', 'TENTATIVE')

        c.add_component(e)
        #print(c.to_ical())
        if obj.google_calendar_event_id == '' or obj.google_calendar_event_id is None:
            publish_to_public_calendar(e, pk)
        response = HttpResponse(c.to_ical(), content_type="text/calendar")
        response['Content-Disposition'] = 'attachment; filename={0}.ics'.format(slugify(obj),)
        return response



from django.views.generic import ListView
@method_decorator(staff_member_required, name='dispatch')
class propertyShowingListEmailTemplateView(ListView):
    template_name = "property_inquiry/property_showing_schedule_email_list.txt"
    model = propertyShowing
    def get_queryset(self):
        pks = self.kwargs['pks'].split(',')
        return propertyShowing.objects.filter(pk__in=pks).order_by('datetime')

    def get_context_data(self, **kwargs):
        context = super(propertyShowingListEmailTemplateView, self).get_context_data(**kwargs)
        context['title'] = 'Showing Email'
        return context



from django.views.generic import DetailView
@method_decorator(staff_member_required, name='dispatch')
class propertyShowingReleaseView(DetailView):
    template_name = "property_inquiry/release.html"
    model = propertyShowing
    context_object_name = 'showing'
    def get_context_data(self, **kwargs):
        context = super(propertyShowingReleaseView, self).get_context_data(**kwargs)
        context['title'] = 'Showing Release'
        return context
