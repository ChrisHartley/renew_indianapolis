from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext
import json  # not used anymore, right?
from django.core import serializers
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django.views.generic import View  # for class based views
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

# used for geojson display of search results
from vectorformats.Formats import Django, GeoJSON
from django.core.serializers import serialize  # new in 1.8 supports geojson
from django.http import JsonResponse
from django.core.serializers.json import Serializer
from django.contrib.gis.serializers.geojson import Serializer as GeoJSONSerializer
from django.utils.encoding import is_protected_type

# these used for search() function, can be removed when that is removed
# used for geojson display of search results
from vectorformats.Formats import Django, GeoJSON
import csv  # used for csv return of search results
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import operator
from django.contrib.gis.geos import GEOSGeometry  # used for centroid calculation
from djqscsv import render_to_csv_response

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie


from property_inventory.models import Property, Zipcode, CDC, Zoning, ContextArea, price_change
from property_inventory.filters import ApplicationStatusFilters
from property_inventory.tables import PropertySearchTable, PropertyStatusTable, reviewPendingStatusTable
from property_inventory.forms import PropertySearchForm, PropertySearchSlimForm
from property_inventory.filters import PropertySearchFilter, PropertySearchSlimFilter
from property_inquiry.models import propertyInquiry
from photos.models import photo

from django.db import connection

import datetime # used for price_change summary view, getting next RC meeting
from decimal import * # used for price_change summary view
from applications.models import Meeting


def get_inventory_csv(request):
    #qs = Property.objects.filter(is_active=True).values('parcel', 'streetAddress', 'zipcode__name', 'structureType','quiet_title_complete','nsp','zone__name','cdc__name', 'neighborhood__name','urban_garden', 'bep_demolition','homestead_only','applicant', 'status','area', 'price', 'price_obo', 'renew_owned')
    qs = Property.objects.filter(is_active=True).values('parcel', 'streetAddress', 'zipcode__name', 'structureType','quiet_title_complete','zone__name','cdc__name', 'neighborhood__name','sidelot_eligible','vacant_lot_eligible','urban_garden', 'bep_demolition','homestead_only','applicant', 'status','area', 'price', 'price_obo', 'renew_owned').order_by('zipcode', 'status', 'streetAddress')
    return render_to_csv_response(qs)

def get_featured_properties_csv(request):
    from datetime import date
    today = date.today()
    qs = Property.objects.filter(is_active=True).filter(featured_property__start_date__lte=today).filter(featured_property__end_date__gte=today).values('parcel', 'streetAddress', 'zipcode__name', 'structureType','quiet_title_complete','zone__name','cdc__name', 'neighborhood__name','sidelot_eligible','vacant_lot_eligible','urban_garden', 'bep_demolition','homestead_only','applicant', 'status','area', 'price', 'price_obo', 'renew_owned', 'featured_property__note')
    return render_to_csv_response(qs)

# given a parcel number return a json with a number of fields
def getAddressFromParcel(request):
    if 'parcel' in request.GET and request.GET['parcel']:
        parcelNumber = request.GET.__getitem__('parcel')
        SearchResult = Property.objects.filter(parcel__exact=parcelNumber)
        response_data = serializers.serialize('json', SearchResult,
                                              fields=('streetAddress', 'zipcode', 'neighborhood','status', 'structureType',
                                                      'sidelot_eligible', 'homestead_only', 'price','hhf_demolition', 'vacant_lot_eligible')
                                              )
        return HttpResponse(response_data, content_type="application/json")
    # when is this used? who knows. I broke it, when I find out where it is used I'll fix it.
    # if 'streetAddress' in request.GET and request.GET['streetAddress']:
    # 	streetAddress = request.GET.__getitem__('streetAddress')
    # 	try:
    # 		SearchResult = Property.objects.get(streetAddress__iexact=streetAddress)
    # 		return HttpResponse(SearchResult.parcel)
    # 	except Property.DoesNotExist:
    return HttpResponse("Please submit a search term")

# Show a table with property statuses broken down by sold, sale-approved and in-progress.

def showApplications(request):
    config = RequestConfig(request)

    soldProperties = Property.objects.all().filter(
        status__istartswith='Sold').order_by('status', 'applicant')
    approvedProperties = Property.objects.all().filter(
        status__istartswith='Sale').order_by('status', 'applicant')

    next_rc_meeting = Meeting.objects.filter(Q(meeting_type=Meeting.REVIEW_COMMITTEE)&Q(meeting_date__gte=datetime.date.today())).order_by('meeting_date').first()
    if next_rc_meeting is not None:
        meeting_date = next_rc_meeting.meeting_date
        reviewPendingProperties = Property.objects.filter(application__meeting__meeting=next_rc_meeting).distinct().order_by('zipcode__name', 'streetAddress')
    else:
        meeting_date = 'future'
        reviewPendingProperties = Property.objects.none().order_by('zipcode__name', 'streetAddress')


    soldFilter = ApplicationStatusFilters(
        request.GET, queryset=soldProperties, prefix="sold-")
    approvedFilter = ApplicationStatusFilters(
        request.GET, queryset=approvedProperties, prefix="approved-")
    reviewPendingFilter = ApplicationStatusFilters(
        request.GET, queryset=reviewPendingProperties, prefix="review_pending-")

    soldTable = PropertyStatusTable(soldFilter.qs, prefix="sold-")
    approvedTable = PropertyStatusTable(approvedFilter.qs, prefix="approved-")
    reviewPendingTable = reviewPendingStatusTable(reviewPendingFilter.qs, prefix="review_pending-")

    config.configure(reviewPendingTable)
    config.configure(soldTable)
    config.configure(approvedTable)
    return render(request, 'app_status_template.html', {
        'meeting': meeting_date,
        'reviewPendingTable': reviewPendingTable,
        'soldTable': soldTable,
        'approvedTable': approvedTable,
        'title': 'applications & sale activity',
        'soldFilter': soldFilter,
        'approvedFilter': approvedFilter,
        'reviewPendingFilter': reviewPendingFilter,
        })


class DisplayNameJsonSerializer(GeoJSONSerializer):

    def handle_field(self, obj, field):
        value = field._get_val_from_obj(obj)

        display_method = "get_%s_display" % field.name
        if hasattr(obj, display_method):
            self._current[field.name] = getattr(obj, display_method)()
        elif is_protected_type(value):
            self._current[field.name] = value
        else:
            if field == "price":
                self._current[field.name] = "$".join(
                    field.value_to_string(obj))
            else:
                self._current[field.name] = field.value_to_string(obj)



# search property inventory - new version
def searchProperties(request):
    #	config = RequestConfig(request)
    f = PropertySearchFilter(request.GET, queryset=Property.objects.filter(
        propertyType__exact='lb', is_active__exact=True).prefetch_related('cdc', 'zone', 'zipcode'))

    if 'returnType' in request.GET and request.GET['returnType']:
        if request.GET['returnType'] == "geojson":
            json_serializer = DisplayNameJsonSerializer()
            if 'centroids' in request.GET and request.GET['centroids']:
                if request.GET['centroids'] == "true":
                    print "using centroid_geometry"
                    geom = 'centroid_geometry'
                else:
                    geom = 'geometry'
            else:
                geom = 'geometry'
            s = serializers.serialize('geojson',
                                      f.qs,
                                      geometry_field=geom,
                                      fields=('id', 'parcel', 'streetAddress', 'zipcode', 'zone', 'status', 'structureType',
                                              'sidelot_eligible', 'vacant_lot_eligible','neighborhood', 'homestead_only', 'bep_demolition', 'quiet_title_complete',
                                              'urban_garden','price', 'renew_owned', 'area','price_obo', 'cdc', 'hhf_demolition', geom),
                                      use_natural_foreign_keys=True
                                      )
            return HttpResponse(s, content_type='application/json')

    return render(
        request,
        'property_search.html',
        {
            'form_filter': f.form,
            'title': 'Property Search'
        })


# populate property popup on map via ajax
def propertyPopup(request):
    object_list = Property.objects.get(parcel__exact=request.GET['parcel'])
#	json = serializers.serialize('json', object_list)
    content = "<div style='font-size:.8em'>Parcel: " + str(object_list.parcel) + "<br/>Address: " + str(object_list.streetAddress) + "<br/>Status: " + str(object_list.status) + "<br/>Structure Type: " + str(
        object_list.structureType) + "<br/>Side lot Eligible: " + str(object_list.sidelot_eligible) + "<br/>Homestead only: " + str(object_list.homestead_only) + "<br/><a href='http://maps.indy.gov/AssessorPropertyCards.Reports.Service/ReportPage.aspx?ParcelNumber="+str(object_list.parcel)+"' target='_blank'>Assessor's Property Report Card</a></br><a target='_blank' href='https://www.renewindianapolis.org/map/property/"+str(object_list.parcel)+"/photos/'>View Photos</a></div>"
    return HttpResponse(content, content_type='text/plain; charset=utf8')
#	return HttpResponse(json, content_type='application/json')

class PropertyDetailView(DetailView):
    model = Property
    template = 'property_detail.html'
    slug_field = 'parcel'
    slug_url_kwarg = 'parcel'
    context_object_name = 'property'

    def get_context_data(self, **kwargs):
        context = super(PropertyDetailView, self).get_context_data(**kwargs)
        context['photos'] = photo.objects.filter(prop__exact=self.object).order_by('-main_photo')
        context['title'] = '{0} - {1}'.format(self.object.streetAddress, self.object.parcel)
        return context

class InventoryMapTemplateView(TemplateView):
    template_name = "inventory_map.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(InventoryMapTemplateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InventoryMapTemplateView, self).get_context_data(**kwargs)
        context['filter'] = PropertySearchSlimFilter
        return context

class PropertyDetailJSONView(DetailView):
    model = Property
    slug_field = 'parcel'
    slug_url_kwarg = 'parcel'
    def render_to_response(self, context, **response_kwargs):
        s = serializers.serialize('geojson',
                              [context.get('property'),],
                              geometry_field='geometry',
                              use_natural_foreign_keys=True
                              )
        return HttpResponse(s, content_type='application/json')

# New property search for new map
class SlimPropertySearchView(ListView):
    model = Property
    def get_context_data(self, **kwargs):
        context = super(SlimPropertySearchView, self).get_context_data(**kwargs)
        context['filter'] = PropertySearchSlimFilter(self.request.GET, queryset=Property.objects.filter(
            propertyType__exact='lb', is_active__exact=True).prefetch_related('cdc', 'zone', 'zipcode'))
        return context

    def render_to_response(self, context, **response_kwargs):
        s = serializers.serialize('geojson',
                                  context['filter'].qs,
                                  geometry_field='geometry',
                                  srid=2965,
                                  fields=('id', 'parcel', 'streetAddress', 'zipcode', 'zone', 'status', 'structureType',
                                          'sidelot_eligible', 'vacant_lot_eligible','neighborhood', 'homestead_only', 'bep_demolition', 'quiet_title_complete',
                                          'urban_garden','price', 'renew_owned', 'area','price_obo', 'hhf_demolition', 'geometry'),
                                  use_natural_foreign_keys=True
                                  )
        return HttpResponse(s, content_type='application/json')

class ContextAreaListJSONView(ListView):
    model = ContextArea
    def render_to_response(self, context, **response_kwargs):
        s = serializers.serialize('geojson',
                              ContextArea.objects.all(),
                              geometry_field='geometry',
                              use_natural_foreign_keys=True
                              )
        return HttpResponse(s, content_type='application/json')

class PriceChangeSummaryView(DetailView):
    model = price_change
    template_name = 'price_change_summary_view.html'
    context_object_name = 'price_change'
    def get_context_data(self, **kwargs):
        context = super(PriceChangeSummaryView, self).get_context_data(**kwargs)
        for duration in (30,60,90,180):
            end_day = datetime.date.today()
            start_day = end_day - datetime.timedelta(duration)
            context['{0}dayinquiries'.format(duration,)] = propertyInquiry.objects.filter(Property=self.object.Property).filter(timestamp__range=(start_day, end_day)).count()
        context['current_lot_price_per_square_foot'] = round(self.object.Property.price / Decimal(self.object.Property.area), 2)
        context['proposed_lot_price_per_square_foot'] = round(self.object.proposed_price / Decimal(self.object.Property.area), 2)
        return context
