from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator

from django_tables2_reports.config import RequestConfigReport as RequestConfig

from django.core.urlresolvers import reverse

from django.core.mail import send_mail
from django.template.loader import render_to_string
from ipware.ip import get_real_ip

from property_inquiry.models import propertyInquiry
from property_inventory.models import Property
from property_inquiry.filters import PropertyInquiryFilters
from property_inquiry.tables import PropertyInquiryTable
from property_inquiry.forms import PropertyInquiryForm

from django.views import View

from django.conf import settings
from django.contrib import messages
import datetime


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
        previousPIcount = propertyInquiry.objects.filter(user=request.user).filter(timestamp__gt=datetime.datetime.now()-datetime.timedelta(hours=48)).count()

        #print "Previous PI count:", previousPIcount
        form = PropertyInquiryForm(request.POST)
        duplicate_pi = propertyInquiry.objects.filter(user=request.user).filter(timestamp__gt=datetime.datetime.now()-datetime.timedelta(hours=72)).filter(Property=request.POST['Property']).count()
        if duplicate_pi > 0:
            form.add_error(None, "You submitted a request for this property within the past 72 hours. Due to volume it may take 5+ business days to schedule your inquiry, there is no need to re-submit.")
        if previousPIcount >= 3: # limit number of requests per time period
            form.add_error(None, "You can not submit more than 3 property inquiries every 48 hours. Please try again later.")
        if form.is_valid():
            form_saved = form.save(commit=False)
            form_saved.applicant_ip_address = get_real_ip(request)
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

@method_decorator(staff_member_required, name='dispatch')
class IdentifyClusters(View):
    template_name = 'property_inquiry/clusters.html'
    def get(self, request):
        params = {
            'distance': int(request.GET.get('distance', 2640)),
            'age': int(request.GET.get('age', 90)),
            'min_points': int(request.GET.get('min_points', 1)),
        }
        p_clusters = propertyInquiry.objects.raw("""
            select pi.*, st_clusterdbscan(st_transform(geometry,2965), eps:=%(distance)s, minPoints :=%(min_points)s) over () as cid
            from property_inventory_property p
            left join property_inquiry_propertyinquiry pi on pi."Property_id" = p.id
            where pi.status is null and timestamp >= now() - interval '%(age)s days' order by cid""",
            params)

        return render(request, self.template_name, {'clusters':p_clusters, 'params': params})

    def post(self, request):
        ids = request.POST.get('pi_ids').split()
        date = request.POST.get('date')
        time = request.POST.get('time')
        for id in ids:
            pi = propertyInquiry.objects.get(id=id)
            pi.status = propertyInquiry.USER_CONTACTED_STATUS
            pi.showing_scheduled = datetime.datetime.strptime('{} {}'.format(date,time), "%Y-%m-%d %H:%M")
            pi.save()
            messages.info(request, '{} updated'.format(pi,))
        return HttpResponseRedirect(reverse('identify_pi_clusters'))
