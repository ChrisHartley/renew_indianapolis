import django_filters
from django_filters.widgets import RangeWidget
from .models import Parcel
from .forms import SurplusSearchForm

class SurplusParcelFilter(django_filters.FilterSet):
    #street_address = django_filters.CharFilter(lookup_type='icontains')
    notes = django_filters.CharFilter(lookup_type='icontains')
    street_address = django_filters.CharFilter(lookup_type='icontains')
    area = django_filters.RangeFilter(widget=RangeWidget(attrs={'placeholder': 'sqft'}))
    #area = django_filters.RangeFilter(name='area')
    has_building = django_filters.BooleanFilter(label='Has a structure')
    township = django_filters.MultipleChoiceFilter(choices=Parcel.TOWNSHIP_CHOICES)
    land_value = django_filters.RangeFilter(widget=RangeWidget(attrs={'placeholder': '$'}))
    improved_value = django_filters.RangeFilter(widget=RangeWidget(attrs={'placeholder': '$'}))
    interesting = django_filters.BooleanFilter()
    parcel_number = django_filters.CharFilter(lookup_type='startswith')

    class Meta:
        model = Parcel
        form = SurplusSearchForm
#        fields = {
            #'parcel_number': ['contains'],
            #'street_address': ['icontains'],
            #'township': ['AllValuesMultipleFilter'],
            #'zipcode': ['contains'],
            #'has_building': ['exact'],
            #'land_value': ['RangeFilter'],
            #'improved_value': ['RangeFilter'],
            #'area': ['RangeFilter'],
            #'classification': ['exact'],
            #'assessor_classification': ['exact'],
            #'interesting': ['exact'],
            #'notes': ['icontains'],
#        }
