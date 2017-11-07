import django_filters
from django.contrib.gis.db import models
from .models import market_value_analysis, parcel
from .forms import UniSearchForm

class UniSearchFilter(django_filters.FilterSet):
    parcel_or_street_address = django_filters.CharFilter(method='filter_parcel_or_street_address', label="Street address or parcel number")

    BOOL_CHOICES = ((False, 'No'), (True, 'Yes'))
    has_building_filter = django_filters.MultipleChoiceFilter(
        choices=BOOL_CHOICES, name='has_building', label='Parcel has improvements')

    mva_area = django_filters.ModelChoiceFilter(
         label='MVA Classification', name='mva__geometry', lookup_expr="within",
        queryset=market_value_analysis.objects.all()
    )


    status = django_filters.MultipleChoiceFilter(
        choices=parcel.STATUS_CHOICES,
        lookup_expr="exact",
        label="Status"
    )



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
