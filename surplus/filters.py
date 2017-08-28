import django_filters
from django_filters.widgets import RangeWidget
from django.forms.widgets import SelectMultiple, Select
from .models import Parcel
from django.db.models import Q
from django.contrib.gis.db import models

from .models import Parcel
from .forms import SurplusSearchForm

from datetime import date
class SurplusParcelFilter(django_filters.FilterSet):
    notes = django_filters.CharFilter(lookup_expr='icontains')
    general_search = django_filters.CharFilter(method='general_search_filter')
    area = django_filters.RangeFilter(widget=RangeWidget(attrs={'placeholder': 'sqft'}))
    has_building = django_filters.BooleanFilter(label='Has a structure')
    township = django_filters.MultipleChoiceFilter(choices=Parcel.TOWNSHIP_CHOICES)
    land_value = django_filters.RangeFilter(widget=RangeWidget(attrs={'placeholder': '$'}))
    improved_value = django_filters.RangeFilter(widget=RangeWidget(attrs={'placeholder': '$'}))
    interesting = django_filters.BooleanFilter()
    classification = django_filters.ChoiceFilter(choices=Parcel.CLASSIFICATION_CHOICES)
    demolition_order = django_filters.BooleanFilter()
    repair_order = django_filters.BooleanFilter()
    rc = Parcel.objects.order_by('requested_from_commissioners').distinct(
        'requested_from_commissioners').values_list('requested_from_commissioners', flat=True)

    #rc_formatted = []
    #for rc_value in rc:
    #    try:
    #        rc_formatted.append(datetime.strftime(rc_value, '%Y-%m-%d'))
    #        rc_formatted.append(datetime.strftime(rc_value, '%B %d, %Y'))
    #    except TypeError:
    #        rc_formatted.append('None')
    #rc_dates = zip(rc_formatted, rc)
    #rc_dates = zip(rc, rc)
    rc_dates = (
        ("2017-08-02","2017-08-02"),
        ("2017-05-18","2017-05-18"),
        ("2017-05-30","2017-05-30"),
        (None, 'None')
    )


    # The problem might be the choice filter rather than a date filter. Can we
    # use a date filter with multi select widget
    requested_from_commissioners = django_filters.DateFilter(widget=Select(choices=rc_dates), lookup_expr='exact')
    #requested_from_commissioners = django_filters.ChoiceFilter(
    #    choices=rc_dates, label='Date requested from commissioners', lookup_expr='exact')
    #requested_from_commissioners = django_filters.DateFilter()

    def general_search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(street_address__icontains=value) |
            Q(zipcode__exact=value) |
            Q(parcel_number__exact=value)
        )

    class Meta:
        model = Parcel
        form = SurplusSearchForm
        exclude = ['centroid_geometry', 'geometry']

        filter_overrides = {
            models.MultiPolygonField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                }
            },
        }
