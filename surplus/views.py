from django.shortcuts import render
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.gis.serializers.geojson import Serializer as GeoJSONSerializer
from django.core.serializers import serialize, register_serializer  # new in 1.8 supports geojson
from django.forms.models import model_to_dict
from djqscsv import render_to_csv_response
from django.db.models import Q

from .models import Parcel
from .filters import SurplusParcelFilter
from property_condition.models import ConditionReport
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.core import serializers

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


#register_serializer('geojson_display_name','DisplayNameJsonSerializer')

class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    https://docs.djangoproject.com/en/1.8/topics/class-based-views/generic-editing/
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return model_to_dict(context)

class ParcelDetailView(JSONResponseMixin, DetailView):
    model = Parcel
    slug_field = 'parcel_number'
    slug_url_kwarg = 'parcel'
    def render_to_response(self, context, **response_kwargs):
        s = serializers.serialize('geojson',
                              [context.get('parcel'),],
                              geometry_field='geometry',
                              fields = ('parcel_number','street_address', 'zipcode', 'zoning',
                                  'township', 'has_building', 'land_value', 'improved_value',
                                  'area', 'assessor_classification', 'classification',
                                  'demolition_order', 'repair_order', 'vbo_count',
                                  'repair_order_count', 'demolition_order_count', 'interesting',
                                  'notes', 'requested_from_commissioners', 'vetted', 'vetting_notes',
                                  'intended_end_use', 'condition_report_exists', 'request_tranche'),
                              use_natural_foreign_keys=True,
                              )
        return HttpResponse(s, content_type='application/json')

class ParcelListView(ListView):
    model = Parcel

class ParcelUpdateView(AjaxableResponseMixin, UpdateView):
    model = Parcel
    fields = ['interesting','notes']

class SurplusMapTemplateView(TemplateView):
    template_name = "surplus_map_fancy_three.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(SurplusMapTemplateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SurplusMapTemplateView, self).get_context_data(**kwargs)
        context['filter'] = SurplusParcelFilter
        context['classification'] = self.request.GET.get('classification', 1)
        return context

from django.db import connection
import pprint
@ensure_csrf_cookie
def searchSurplusProperties(request):
    #properties_with_reports = ConditionReport.objects.filter(quick_condition__isnull=False).values_list('Property__parcel', flat=True)
#    if request.GET.get('report') == 'false':
#        qs = Parcel.objects.filter(Q(requested_from_commissioners_date__exact='2018-08-16') & Q(requested_from_commissioners__exact=True) &Q(commissioners_response__exact=True)).exclude(parcel_number__in=properties_with_reports).exclude(intended_end_use='BEP')
#    elif request.GET.get('report') == 'true':
#        qs = Parcel.objects.filter(Q(requested_from_commissioners_date__exact='2018-08-16') & Q(requested_from_commissioners__exact=True) &Q(commissioners_response__exact=True)).filter(parcel_number__in=properties_with_reports).exclude(intended_end_use='BEP')
#    else:
#        qs = Parcel.objects.filter(Q(requested_from_commissioners_date__exact='2018-08-16') & Q(requested_from_commissioners__exact=True) &Q(commissioners_response__exact=True)).exclude(intended_end_use='BEP')
    classification_requested = request.GET.get('classification', 1)
    qs = Parcel.objects.filter(classification=classification_requested)
    f = SurplusParcelFilter(request.GET, queryset=qs)

    if request.GET.get("geometry_type", None) == "centroid":
        geom = 'centroid_geometry'
        fields = ('parcel_number','street_address', 'zipcode', 'zoning',
            'township', 'has_building', 'land_value', 'improved_value',
            'area', 'assessor_classification', 'classification',
            'demolition_order_count', 'repair_order_count', 'vbo_count',
            'interesting', 'notes', 'requested_from_commissioners',
            'vetted', 'vetting_notes', 'request_tranche', geom)
    else:
        geom = 'geometry'
        fields = ('parcel_number', 'has_building', geom)

    s = serializers.serialize('geojson',
        f.qs,
        geometry_field=geom,
        srid=2965,
        fields=fields,
        use_natural_foreign_keys=True
    )
    return HttpResponse(s, content_type='application/json')

@csrf_exempt
def surplusUpdateFieldsFromMap(request):
    prop = Parcel.objects.get(parcel_number=request.POST.get('parcel_number', None))
    if request.POST.get('notes', None):
        prop.notes = request.POST.get('notes')
    if request.POST.get('interesting', None) == 'on':
        prop.interesting = True
    else:
        prop.interesting = False
    if request.POST.get('vetted', None) == 'on':
        prop.vetted = True
    else:
        prop.vetted = False
    prop.request_tranche = request.POST.get('request_tranche', None)
    try:
        prop.save()
        return JsonResponse({'status': 'OK'})
    except:
        return JsonResponse({'status':'Not OK'})


def get_surplus_inventory_csv(request):
    qs = Parcel.objects.filter(classification=1).values('parcel_number','street_address','township','zipcode','zoning','has_building','improved_value','land_value','area','assessor_classification','classification','demolition_order','repair_order','interesting','requested_from_commissioners','notes', 'vetted', 'vetting_notes', 'request_tranche') #.values('parcel', 'street_address')
    #qs = Property.objects.all().prefetch_related('cdc', 'zone', 'zipcode')
    return render_to_csv_response(qs)
