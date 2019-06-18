from django.shortcuts import render, get_object_or_404, Http404
from django.shortcuts import render_to_response, redirect, reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import os
from wsgiref.util import FileWrapper
import mimetypes
from django.http import HttpResponse, HttpResponseNotFound

from property_inquiry.models import propertyInquiry
from property_inventory.models import Property
from property_condition.models import ConditionReport, ConditionReportProxy
from property_condition.forms import ConditionReportForm
from property_condition.filters import ConditionReportFilters




# Displays form template for property condition submissions, and saves
# those submissions

@user_passes_test(lambda u: u.groups.filter(name='City Staff').exists() or u.is_staff)
def submitConditionReport(request):
    success = False
    if request.method == 'POST':
        form = ConditionReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            success = True
    form = ConditionReportForm()
    return render(request, 'condition_report.html', {
        'form': form,
        'title': 'condition report',
        'success': success
    })


def view_or_create_condition_report(request, parcel):
    if parcel and Property.objects.filter(parcel=parcel).exists():
        if ConditionReport.objects.filter(Property__parcel=parcel).exists():
            return redirect('{0}?_popup=1'.format(
                reverse('admin:property_condition_conditionreportproxy_change', args=[ConditionReportProxy.objects.filter(Property__parcel=parcel).order_by('timestamp').first().pk])
                ),
            )
        else:
            cr = ConditionReport(Property=Property.objects.get(parcel=parcel))
            cr.save()
            return redirect('{0}?_popup=1'.format(reverse('admin:property_condition_conditionreportproxy_change', args=[cr.pk])),)
    return HttpResponseNotFound('<h1>Parcel not found. BEP Property?</h1>')
