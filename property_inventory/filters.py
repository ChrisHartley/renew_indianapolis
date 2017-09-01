import django_filters
#from django_filters import MethodFilter
from django.db.models import Count, Q
from django import forms
from django.contrib.gis.db import models


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django.contrib.gis.geos import GEOSGeometry  # used for centroid calculation

from property_inventory.models import Property, Zoning, Zipcode, Neighborhood
from property_inventory.forms import PropertySearchForm, PropertySearchSlimForm

# this allows a None option with the AllValues dropdown.


class AllValuesNoneFilter(django_filters.ChoiceFilter):

    @property
    def field(self):
        qs = self.model._default_manager.distinct()
        qs = qs.order_by(self.name).values_list(self.name, flat=True)
        self.extra['choices'] = [(o, o) for o in qs]
        self.extra['choices'].insert(0, ('', u'------',))
        return super(AllValuesNoneFilter, self).field


class ApplicationStatusFilters(django_filters.FilterSet):
    streetAddress = django_filters.CharFilter()
    all_applicants = AllValuesNoneFilter(name='applicant', label="Applicant")

    def __init__(self, *args, **kwargs):
        super(ApplicationStatusFilters, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.add_input(Submit('Filter', 'Filter'))

    class Meta:
        model = Property
        fields = ['all_applicants', 'streetAddress']

class PropertySearchSlimFilter(django_filters.FilterSet):
    parcel_or_street_address = django_filters.CharFilter(method='filter_parcel_or_street_address', label="Street address or parcel number")
    st = Property.objects.order_by('structureType').distinct(
        'structureType').values_list('structureType', flat=True).order_by('structureType')
    structure_types = zip(st, st)
    structureType = django_filters.MultipleChoiceFilter(
        choices=structure_types, name='structureType', label='Structure Type')
    zipcode = django_filters.ModelChoiceFilter(
         label='Zipcode', name='zipcode__name', lookup_expr="icontains",
        queryset=Zipcode.objects.all()
    )
    neighborhood = django_filters.ModelChoiceFilter(
        label='Neighborhood', name='neighborhood__name', lookup_expr="icontains",
        queryset=Neighborhood.objects.all()
    )

    AVAILABLE_CHOICE = 'A'
    SOLD_CHOICE = 'S'

    STATUS_CHOICES = (
        (AVAILABLE_CHOICE,'Available'),
        (SOLD_CHOICE,'Sold or Approved For Sale'),
    )

    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
    #status = django_filters.ChoiceFilter(method='filter_status', label='Limit search to...', widget=forms.RadioSelect(attrs={'class': 'radio'}), empty_label=None)
    status =  django_filters.ChoiceFilter(widget=forms.RadioSelect(attrs={'class': 'radio'}), empty_label=None)
    #available_only = django_filters.BooleanFilter(method='filter_available_only', label='Show only available properties')

    ZONING_CHOICES = (
        ('D', 'Dwelling'),
        ('C', 'Commercial'),
        ('I', 'Industrial'),
        ('O', 'Other'),
    )
    zoning = django_filters.ChoiceFilter(
        choices=ZONING_CHOICES,
        method='filter_zoning',
        label='Property Zoning',
    )


# new vs old inventory
# duplex vs sfr vs other

    class Meta:
        model = Property
        exclude = []
        #fields = ['neighborhood__name', 'cdc__name']
        #fields = ['parcel', 'streetAddress', 'nsp', 'structureType', 'cdc', 'zone', 'sidelot_eligible', 'homestead_only', 'bep_demolition']
        form = PropertySearchSlimForm

        filter_overrides = {
            models.MultiPolygonField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                }
            },
            models.PointField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                }
            },
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                }

            },
        }

    def filter_zoning(self, queryset, field, value):
        print value
        if value == 'O':
            return queryset.exclude(zone__name__startswith='C').exclude(zone__name__startswith='I').exclude(zone__name__startswith='D')
        else:
            return queryset.filter(zone__name__startswith=value)

    def filter_parcel_or_street_address(self, queryset, field, value):
        return queryset.filter(
            Q(streetAddress__icontains=value) |
            Q(parcel__icontains=value)
        )

    def filter_status(self, queryset, field, value):
        if value == self.AVAILABLE_CHOICE:
            return queryset.filter(status__contains='Available')
        if value == self.SOLD_CHOICE:
            return queryset


    def filter_searchArea(self, queryset, field, value):
        try:
            searchGeometry = GEOSGeometry(value, srid=900913)
        except Exception:
            return queryset

        return queryset.filter(
            geometry__within=searchGeometry
        )




class PropertySearchFilter(django_filters.FilterSet):
    #streetAddress = django_filters.CharFilter(label="Street address", lookup_expr='icontains')
    #parcel = django_filters.CharFilter(label="Parcel number")

    parcel_or_street_address = django_filters.CharFilter(method='filter_parcel_or_street_address', label="Address or parcel number")

    # lord I don't remember how this works but it takes calculates all the structureTypes in the database and makes a list.
    st = Property.objects.order_by('structureType').distinct(
        'structureType').values_list('structureType', flat=True).order_by('structureType')
    structure_types = zip(st, st)
    structureType = django_filters.MultipleChoiceFilter(
        choices=structure_types, name='structureType', label='Structure Type')

    status_choices = [('available', 'Available'), ('review', 'Application under review'),
                      ('approved', 'Approved for Sale'), ('sold', 'Sold'), ('bep', 'BEP Demolition Slated')]
    status = django_filters.CharFilter(
        label='Status', widget=forms.Select(choices=status_choices), method='filter_status')

    searchArea = django_filters.CharFilter(method="filter_searchArea")

    yesno_choices = [('true', 'Yes'), ('false', 'No')]
    #featured_properties_only = django_filters.BooleanFilter(method="filter_featured_properties", label='Search only featured properties')#, widget=forms.widgets.CheckboxInput())
    featured_properties_only = django_filters.MultipleChoiceFilter(choices=yesno_choices, label='Search Featured Properties Only', method="filter_featured_properties")

    class Meta:
        model = Property
        exclude = []
        #fields = ['parcel', 'streetAddress', 'nsp', 'structureType', 'cdc', 'zone', 'sidelot_eligible', 'homestead_only', 'bep_demolition']
        form = PropertySearchForm

        filter_overrides = {
            models.MultiPolygonField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                }
            },
            models.PointField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                }
            },
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                }

            },
        }

    def filter_featured_properties(self, queryset, field, value):
        #print "!!!! value: {0}".format(value,)
        if value[0] == 'true':
            from datetime import date
            today = date.today()
            return queryset.filter(featured_property__start_date__lte=today).filter(featured_property__end_date__gte=today)
        else:
            return queryset

    def filter_parcel_or_street_address(self, queryset, field, value):
        return queryset.filter(
            Q(streetAddress__icontains=value) |
            Q(parcel__icontains=value)
        )

    def filter_status(self, queryset, field, value):
        if value == 'available':
            return queryset.filter(status__icontains='Available')
        if value == 'review':
            return queryset.filter(
                (Q(renew_owned__exact=False) & Q(
                    status__icontains='Sale approved by Board of Directors'))
                | Q(status__icontains='Sale approved by Review Committee')
            )
        if value == 'approved':
            return queryset.filter(
                (Q(renew_owned__exact=True) & Q(
                    status__icontains='Sale approved by Board of Directors'))
                | Q(status__icontains='Sale approved by MDC')
            )
        if value == 'sold':
            return queryset.filter(status__contains='Sold')

        if value == 'bep':
            return queryset.filter(status__contains='BEP')

        return queryset

    def filter_searchArea(self, queryset, field, value):
        try:
            searchGeometry = GEOSGeometry(value, srid=900913)
        except Exception:
            return queryset

        return queryset.filter(
            geometry__within=searchGeometry
        )
