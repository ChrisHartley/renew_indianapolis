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

from icalendar import Calendar, Event, vCalAddress, vText
from datetime import timedelta
from django.utils.timezone import now
from django.utils.text import slugify
from django.contrib.auth.models import User
@method_decorator(staff_member_required, name='dispatch')
class CreateIcsFromShowing(View):
    def get(self, request, pk):
        obj = propertyShowing.objects.get(pk=pk)
        c = Calendar()
        e = Event()
        c.add('prodid', '-//Renew Indianapolis//Property Showings//EN')
        c.add('version', '2.0')
        e.add('summary', '{} - Proposed Property Showing'.format(obj.Property.streetAddress,).title() )
        e.add('uid', obj.id)
        e.add('dtstart', obj.datetime)
        e.add('dtend', obj.datetime+timedelta(minutes=30))
        e.add('dtstamp', now())
        e.add('location', '{0}, Indianapolis, IN {1}'.format(obj.Property.streetAddress, obj.Property.zipcode))
        people = []
        organizer = vCalAddress('MAILTO:{}'.format(request.user.email,))
        organizer.params['cn'] = vText(u'{} {}'.format(request.user.first_name, request.user.last_name))
        e.add('organizer', organizer, encode=0)
        for showing in obj.inquiries.all():
            u = showing.user
            try:
                people.append(u'{} {} - {} {}'.format(u.first_name, u.last_name, u.email, u.profile.phone_number))
            except ApplicantProfile.DoesNotExist:
                people.append(u'{} {} - {}'.format(u.first_name, u.last_name, u.email))
            attendee = vCalAddress('MAILTO:{}'.format(u.email,))
            attendee.params['cn'] = vText(u'{} {}'.format(u.first_name, u.last_name))
    #        e.add('attendee', attendee, encode=0)

        for staff in settings.COMPANY_SETTINGS['city_staff']:
        #for staff in User.objects.filter(group__exact='City Staff'):
        #   a = vCalAddress('MAILTO:{}'.format(staff.email,))
        #   a.params['cn'] = vText('{} {}'.format(staff.first_name, staff.last_name) )
            a = vCalAddress('MAILTO:{}'.format(staff['email'],))
            a.params['cn'] = vText(staff['name'])
            e.add('attendee', a, encode=0)
        description = render_to_string('property_inquiry/property_showing_ics_description.txt', {'showing': self, 'property': obj.Property, 'inquiries': obj.inquiries.all()})
        e.add('description', description )
        e.add('status', 'TENTATIVE')
        c.add_component(e)
        print(c.to_ical())
        response = HttpResponse(c.to_ical(), content_type="text/calendar")
        response['Content-Disposition'] = 'attachment; filename={0}.ics'.format(slugify(obj),)
        return response

from django.views.generic import DetailView
@method_decorator(staff_member_required, name='dispatch')
class propertyShowingEmailTemplateView(DetailView):
    template_name = "property_inquiry/property_showing_schedule_email.txt"
    model = propertyShowing

from django.views.generic import ListView
@method_decorator(staff_member_required, name='dispatch')
class propertyShowingListEmailTemplateView(ListView):
    template_name = "property_inquiry/property_showing_schedule_email_list.txt"
    model = propertyShowing
