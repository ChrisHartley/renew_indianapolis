import django_filters
from django.apps import apps
from django.contrib.gis.db import models
from django.db.models import Q

from .models import market_value_analysis, parcel
from .forms import UniSearchForm

class UniSearchFilter(django_filters.FilterSet):


    parcel_or_street_address = django_filters.CharFilter(method='general_search_filter', label="Street address or parcel number")


    mortgage_decision_filter = django_filters.MultipleChoiceFilter(choices=parcel.MORTGAGE_CHOICES, lookup_expr="mortgage_decision__exact", label='Mortgage Decision')

    EARLY_BID_GROUPS = 'Early Bid Groups'
    LATE_BID_GROUPS = 'Late Bid Groups'
    BID_GROUP_CHOICES = (
        (EARLY_BID_GROUPS, 'Early Bid Groups (1-4)'),
        (LATE_BID_GROUPS, 'Late Bid Groups (5-8)'),

    )

    bid_group_filter = django_filters.MultipleChoiceFilter(choices=BID_GROUP_CHOICES, method="bid_group_choice_filter", label='Bid Group')

    MVA_VALUES = apps.get_model(app_lable='univiewer', model_name='parcel').objects.order_by('mva_category').distinct(
        'mva_category').values_list('mva_category', flat=True)
    MVA_CHOICES = zip(MVA_VALUES, MVA_VALUES)

    mva_category_filter = django_filters.MultipleChoiceFilter(choices=MVA_CHOICES, method="mva_category_choice_filter", label='MVA Categories')

    adjacent_homesteads_non_surplus_filter = django_filters.RangeFilter(widget=django_filters.widgets.RangeWidget(), name='adjacent_homesteads_non_surplus', label='# adjacent homesteads')
    ilp_within_quarter_mile_filter = django_filters.RangeFilter(widget=django_filters.widgets.RangeWidget(), name='ilp_within_quarter_mile', label='# ILPs within a quarter mile')

    #adjacent_homesteads_non_surplus_filter__gt = django_filters.NumberFilter(name='price', lookup_expr='gt')
    #adjacent_homesteads_non_surplus_filter__lt = django_filters.NumberFilter(name='price', lookup_expr='lt')

    def mva_category_choice_filter(self, queryset, name, value):
        return queryset.filter(mva_category__in=value)

    def general_search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(street_address__icontains=value) |
            Q(parcel_number__exact=value)
        )

    def bid_group_choice_filter(self, queryset, name, value):
        if value[0] == self.EARLY_BID_GROUPS:
            return queryset.filter(bid_group__regex=r'^[1-4]{1}\.')
        if value[0] == self.LATE_BID_GROUPS:
            return queryset.filter(bid_group__regex=r'^[5-9]{1}\.')
        return queryset

    class Meta:
        model = parcel
        exclude = []
        form = UniSearchForm

        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                }

            },
            models.MultiPolygonField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                }
            },

        }
