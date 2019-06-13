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
    qs = parcel.objects.all().values('parcel_number','street_address', 'bid_group', 'mortgage_decision', 'mva_category', 'ilp_within_quarter_mile', 'adjacent_homesteads_non_surplus').order_by('street_address')
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
          context['filter'].qs,
          geometry_field='geometry',
          srid=2965,
          fields=('id', 'parcel_number', 'street_address', 'bid_group',
            'mva_category', 'mortgage_decision', 'ilp_within_quarter_mile',
            'adjacent_homesteads_non_surplus'),
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
        prop.mortgage_decision = decision
    try:
        prop.save()
        return JsonResponse({'status': 'OK'})
    except:
        return JsonResponse({'status':'Not OK'})
