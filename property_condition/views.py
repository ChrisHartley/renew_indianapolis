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
from django.db.models import Q
from property_inquiry.models import propertyInquiry
from property_inventory.models import Property
from surplus.models import Parcel as SurplusProperty
from property_condition.models import ConditionReport, ConditionReportProxy
from property_condition.forms import ConditionReportForm
from property_condition.filters import ConditionReportFilters
from datetime import timedelta
from django.utils import timezone



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
    if parcel and (Property.objects.filter(parcel=parcel).exists() or SurplusProperty.objects.filter(parcel_number=parcel).exists()):
        threshold = timezone.now() - timedelta(days=180)
        if ConditionReport.objects.filter(Q(Property__parcel=parcel) | Q(Property_surplus__parcel_number=parcel)).exclude(timestamp__lte=threshold).exists():
            if ConditionReport.objects.filter(Property__parcel=parcel).exclude(timestamp__lte=threshold).count()==1:
                return redirect('{0}?_popup=1'.format(
                    reverse('admin:property_condition_conditionreportproxy_change', args=[ConditionReport.objects.filter(Property__parcel=parcel).exclude(timestamp__lte=threshold).first().pk])
                    ),
                )
            elif ConditionReport.objects.filter(Property_surplus__parcel_number=parcel).exclude(timestamp__lte=threshold).count()==1:
                    return redirect('{0}?_popup=1'.format(
                        reverse('admin:property_condition_conditionreportproxy_change', args=[ConditionReport.objects.filter(Property_surplus__parcel_number=parcel).exclude(timestamp__lte=threshold).first().pk])
                        ),
                    )
            else:
                return redirect('{0}/?_popup=1&q={1}'.format(
                    reverse('admin:property_condition_conditionreportproxy_list'),
                    parcel,
                    ),
                )

        else:
            if Property.objects.filter(parcel=parcel).exists():
                cr = ConditionReport(Property=Property.objects.get(parcel=parcel))
            elif SurplusProperty.objects.filter(parcel_number=parcel).exists():
                cr = ConditionReport(Property_surplus=SurplusProperty.objects.get(parcel_number=parcel))
            cr.save()
            return redirect('{0}?_popup=1'.format(reverse('admin:property_condition_conditionreportproxy_change', args=[cr.pk])),)
    return HttpResponseNotFound('<h1>Parcel not found. BEP Property?</h1>')
