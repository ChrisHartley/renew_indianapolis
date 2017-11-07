# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from django.core.serializers import serialize, register_serializer  # new in 1.8 supports geojson

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .models import parcel
from .filters import UniSearchFilter

from djqscsv import render_to_csv_response
def get_uniinventory_csv(request):
    #qs = Property.objects.filter(is_active=True).values('parcel', 'streetAddress', 'zipcode__name', 'structureType','quiet_title_complete','nsp','zone__name','cdc__name', 'neighborhood__name','urban_garden', 'bep_demolition','homestead_only','applicant', 'status','area', 'price', 'price_obo', 'renew_owned')
    qs = parcel.objects.all().order_by('street_address')
    return render_to_csv_response(qs)

class UniParcelDetailJSONView(DetailView):
    model = parcel
    slug_field = 'parcel_number'
    slug_url_kwarg = 'parcel'
    def render_to_response(self, context, **response_kwargs):
        s = serialize('geojson',
                              [context.get('parcel'),],
                              geometry_field='geometry',
                              srid=2965,
                              use_natural_foreign_keys=True
                              )
        return HttpResponse(s, content_type='application/json')

class UniPropertySearchView(ListView):
    model = parcel
    def get_context_data(self, **kwargs):
        context = super(UniPropertySearchView, self).get_context_data(**kwargs)
        context['filter'] = UniSearchFilter(self.request.GET, queryset=parcel.objects.all())
        return context

    def render_to_response(self, context, **response_kwargs):
        s = serialize('geojson',
                                  parcel.objects.all(), #context['filter'].qs,
                                  geometry_field='geometry',
                                  srid=2965,
                                  fields=('id', 'parcel_number', 'street_address', 'has_building', 'property_type', 'status', 'bid_group', 'mva_category'),
                                #          'sidelot_eligible', 'vacant_lot_eligible','neighborhood', 'homestead_only', 'bep_demolition', 'quiet_title_complete',
                                #          'urban_garden','price', 'renew_owned', 'area','price_obo', 'hhf_demolition', 'geometry'),
                                  use_natural_foreign_keys=True
                                  )
        return HttpResponse(s, content_type='application/json')


class UniMapTemplateView(TemplateView):
    template_name = "inventory_map_uni.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(UniMapTemplateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UniMapTemplateView, self).get_context_data(**kwargs)
        context['filter'] = UniSearchFilter
        return context

@method_decorator(csrf_exempt, name='dispatch')
class UniParcelUpdateView(UpdateView):
    model = parcel
    slug_field = 'parcel_number'
    slug_url_kwarg = 'parcel'
    fields = ['mortgage_decision']

@csrf_exempt
def bepUpdateFieldsFromMap(request):
    prop = parcel.objects.get(parcel_number=request.GET.get('parcel_number', None))
    decision = request.GET.get('mortgage_decision', None)
    if decision != None:
        print 'Got it', decision
        prop.mortgage_decision = decision
    try:
        prop.save()
        return JsonResponse({'status': 'OK'})
    except:
        return JsonResponse({'status':'Not OK'})
