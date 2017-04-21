from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test


from django_tables2_reports.config import RequestConfigReport as RequestConfig

from django.core.urlresolvers import reverse

from django.core.mail import send_mail

from ipware.ip import get_real_ip

from property_inquiry.models import propertyInquiry
from property_inventory.models import Property
from property_inquiry.filters import PropertyInquiryFilters
from property_inquiry.tables import PropertyInquiryTable
from property_inquiry.forms import PropertyInquiryForm

import datetime


# Displays form template for property inquiry submissions, and saves those
# submissions
@login_required
def submitPropertyInquiry(request):
    form = PropertyInquiryForm()
    if request.method == 'POST':
        previousPIcount = propertyInquiry.objects.filter(user=request.user).filter(timestamp__gt=datetime.datetime.now()-datetime.timedelta(hours=48)).count()
        #print "Previous PI count:", previousPIcount
        form = PropertyInquiryForm(request.POST)
        if previousPIcount >= 3: # limit number of requests per time period
            #print "adding error message"
            form.add_error(None, "You can not submit more than 3 property inquiries every 48 hours. Please try again later.")
        if form.is_valid():
            form_saved = form.save(commit=False)
            form_saved.applicant_ip_address = get_real_ip(request)
            form_saved.user = request.user
            form_saved.save()
            message_body = 'Applicant: ' + form_saved.user.first_name + ' ' + form_saved.user.last_name + '\n' + 'Parcel: ' + \
                form_saved.Property.parcel + '\nAddress: ' + \
                form_saved.Property.streetAddress + '\nStatus: ' + form_saved.Property.status
            send_mail('New Property Inquiry', message_body, 'chris.hartley@renewindianapolis.org',
                      ['chris.hartley@renewindianapolis.org',], fail_silently=False)
            return HttpResponseRedirect(reverse('property_inquiry_confirmation', args=(form_saved.id,)))
    return render(request, 'property_inquiry.html', {
        'form': form,
        'title': 'property visit'
    })


@login_required
def property_inquiry_confirmation(request, id):
    inquiry = get_object_or_404(propertyInquiry, id=id, user=request.user)
    return render(request, 'property_inquiry_confirmation.html', {
        'title': 'thank you',
        'Property': inquiry.Property,
    })

# Displays submitted property inquiries


@user_passes_test(lambda u: u.is_staff, login_url='/map/accounts/login/')
@login_required
def inquiry_list(request):
    config = RequestConfig(request)
    f = PropertyInquiryFilters(
        request.GET, queryset=propertyInquiry.objects.all().order_by('-timestamp'))
    table = PropertyInquiryTable(f)
    config.configure(table)
    return render(request, 'admin-with-filter-table.html', {
        'filter': f,
        'title': 'Property Inquiry Admin',
        'table': table
    })


@user_passes_test(lambda u: u.is_staff, login_url='/map/accounts/login/')
@login_required
def inquiriesAsJSON(request):
    object_list = propertyInquiry.objects.all()
    json = serializers.serialize(
        'json', object_list, use_natural_foreign_keys=True)
    return HttpResponse(json, content_type='application/json')
