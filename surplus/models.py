from django.contrib.gis.db import models
from property_inventory.models import Property
from property_condition.models import ConditionReport
from photos.models import photo

"""
## The absurd query to populate this model from existing data:
insert into surplus_parcel (parcel_number, street_address, township, zipcode,
has_building, improved_value, land_value, assessor_classification,
classification, demolition_order, repair_order, interesting, notes, geometry,
centroid_geometry, area, zoning, previously_held_gateway_area,
commissioners_resolution_number, commissioners_response_note, intended_end_use,
 mdc_acquire_resolution_number, mdc_dispose_resolution_number,
  requested_from_commissioners, vetted, vetting_notes) select p.parcel_c as "parcel_number",
p."streetAddress" as street_address, case when p.township = 'PIKE' then 1 when
p.township = 'WAYNE' then 2 when p.township = 'DECATUR' then 3 when
p.township = 'WASHINGTON' then 4 when p.township = 'CENTER' then 5
when p.township = 'PERRY' then 6 when p.township = 'LAWRENCE' then 7
when p.township = 'WARREN' then 8 when p.township = 'FRANKLIN' then 9
 end as "township", p.zipcode, case when has_building = True then True else
 False end as has_building, c."Improv_Value" as "improved_value",
 c."Land_Value" as "land_value", case when c."Property_Class" = 'RESIDENTIAL' and
 c."Homestead_Value" != '0' then 1  when c."Property_Class" = 'RESIDENTIAL' and
 c."Homestead_Value" = '0' then 2 else 3 end as assessor_classification, 2 as
 classification, False as demolition_order, False as repair_order, False as
 interesting, ''::character varying as notes, p.geom as geometry,
 st_centroid(p.geom) as centroid_geometry, st_area(p.geom)::int as area,
 z.label as zoning, False as "previously_held_gateway_area",
 '' as "commissioners_resolution_number",
 '' as "commissioners_response_note",
 '' as "intended_end_use",
 '' as mdc_acquire_resolution_number,
 '' as mdc_dispose_resolution_number,
 False as requested_from_commissioners,
 False as vetted,
 '' as vetting_notes
 FROM parcels p left join counter_book_2018 c on
 c."Parcel_Number" = p.parcel_c left join zoning z on
 st_within(st_centroid(p.geom), st_setsrid(z.geom, 2965)) where p.parcel_c in()

"""

class Parcel(models.Model):
    #parcel_number = models.CharField(max_length=7, primary_key=True)
    parcel_number = models.CharField(max_length=7)
    street_address = models.CharField(max_length=254)

    PIKE_TOWNSHIP = 1
    WAYNE_TOWNSHIP = 2
    DECATUR_TOWNSHIP = 3
    WASHINGTON_TOWNSHIP = 4
    CENTER_TOWNSHIP = 5
    PERRY_TOWNSHIP = 6
    LAWRENCE_TOWNSHIP = 7
    WARREN_TOWNSHIP = 8
    FRANKLIN_TOWNSHIP = 9
    TOWNSHIP_CHOICES = (
        (PIKE_TOWNSHIP, 'Pike Township'),
        (WAYNE_TOWNSHIP, 'Wayne Township'),
        (DECATUR_TOWNSHIP, 'Decatur Township'),
        (WASHINGTON_TOWNSHIP, 'Washington Township'),
        (CENTER_TOWNSHIP, 'Center Township'),
        (PERRY_TOWNSHIP, 'Perry Township'),
        (LAWRENCE_TOWNSHIP, 'Lawrence Township'),
        (WARREN_TOWNSHIP, 'Warren Township'),
        (FRANKLIN_TOWNSHIP, 'Franklin Township'),
    )
    township = models.IntegerField(choices=TOWNSHIP_CHOICES, null=True)
    zipcode = models.CharField(max_length=5, null=True)
    zoning = models.CharField(max_length=5, null=True)
    has_building = models.BooleanField()
    improved_value = models.IntegerField(null=True)
    land_value = models.IntegerField(null=True)
    area = models.IntegerField() # compuated from geometry on save

    RESIDENTIAL_1PCT = 1
    RESIDENTIAL_2PCT = 2
    OTHER_3PCT = 3

    ASSESSOR_CLASSIFICATION_CHOICES = (
        (RESIDENTIAL_1PCT, 'Residential - homestead'),
        (RESIDENTIAL_2PCT, 'Residential - non-homestead'),
        (OTHER_3PCT, 'Non-residential'),
    )

    assessor_classification = models.IntegerField(choices=ASSESSOR_CLASSIFICATION_CHOICES)


    TAX_SALE_UNSOLD = 1
    SURPLUS = 2
    FORMER_SURPLUS = 3
    CLASSIFICATION_CHOICES = ( (TAX_SALE_UNSOLD,'Tax Sale Unsold'),(SURPLUS, 'County Surplus'), (FORMER_SURPLUS, 'Former Surplus'))
    classification = models.IntegerField(choices=CLASSIFICATION_CHOICES, default=SURPLUS)

    demolition_order = models.BooleanField(default=False)
    repair_order = models.BooleanField(default=False)

    demolition_order_count = models.IntegerField(default=0)
    repair_order_count = models.IntegerField(default=0)
    vbo_count = models.IntegerField(default=0)

    interesting = models.NullBooleanField(default=None)
    notes = models.CharField(max_length=2048, blank=True)

    vetted = models.BooleanField(default=False)
    vetting_notes = models.CharField(max_length=2048, blank=True, default='')

    requested_from_commissioners_date = models.DateField(blank=True, null=True)
    requested_from_commissioners = models.BooleanField(default=False)

    END_USE_BEP = 'BEP'
    END_USE_INVENTORY = 'Inventory'
    INTENDED_END_USE = (
        (END_USE_BEP, 'Blight Elimination Program - Demolition'),
        (END_USE_INVENTORY, 'Inventory for re-sale'),
    )
    intended_end_use = models.CharField(choices=INTENDED_END_USE, blank=True, max_length=30)

    COMMISSIONERS_DENY = False
    COMMISSIONERS_ACCEPT = True
    COMMISSIONERS_UNKNOWN = None

    COMMISSIONERS_RESPONSE_CHOICES = (
        (COMMISSIONERS_DENY, 'Denied'),
        (COMMISSIONERS_ACCEPT, 'Accepted'),
        (COMMISSIONERS_UNKNOWN, 'None'),
    )

    commissioners_response = models.NullBooleanField(choices=COMMISSIONERS_RESPONSE_CHOICES)

    commissioners_response_note = models.CharField(blank=True, max_length=1024)

    commissioners_resolution_number = models.CharField(blank=True, max_length=100)
    commissioners_resolution_date = models.DateField(blank=True, null=True)

    mdc_acquire_resolution_number = models.CharField(blank=True, max_length=100)
    mdc_acquire_resolution_date = models.DateField(blank=True, null=True)
    mdc_dispose_resolution_number = models.CharField(blank=True, max_length=100)
    mdc_dispose_resolution_date = models.DateField(blank=True, null=True)
    city_deed_recorded = models.DateField(blank=True, null=True)

    previously_held_gateway_area = models.BooleanField(default=False)

    geometry = models.MultiPolygonField(srid=2965)
    centroid_geometry = models.PointField(srid=2965) # compuated from geometry on save

    @property
    def parcel_in_inventory(self):
        return Property.objects.filter(parcel=self.parcel_number).exists()

    @property
    def condition_report_exists(self):
        prop = Property.objects.get(parcel=self.parcel_number)
        return ConditionReport.objects.filter(Property=prop).exists()

    @property
    def number_of_pictures(self):
        return photo.objects.filter(prop__parcel=self.parcel_number).count()


    ## added this function to calculate centroid of the geometry on saving, as it not otherwise available.
    def save(self, *args, **kwargs):
        self.centroid_geometry = self.geometry.centroid
        self.area = self.geometry.area
        super(Parcel, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{0} - {1}'.format(self.street_address, self.parcel_number)

    def natural_key(self):
        return '{0} - {1}'.format(self.street_address, self.parcel_number)
