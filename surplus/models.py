from django.contrib.gis.db import models


## The absurd query to populate this model from existing data:
# select s.parcel_c as "parcel", s."streetAddress" as "street_address", case when s.township = 'PIKE' then 1 when s.township = 'WAYNE' then 2 when s.township = 'DECATUR' then 3 when s.township = 'WASHINGTON' then 4 when s.township = 'CENTER' then 5 when s.township = 'PERRY' then 6 when s.township = 'LAWRENCE' then 7 when s.township = 'WARREN' then 8 when s.township = 'FRANKLIN' then 9 end as "township", s.zipcode, case when has_building = True then True else False end as "has_building", t."CURRENT_AV_TOTAL_IMPROVEMENTS" as improved_value, t."CURRENT_AV_TOTAL_LAND" as land_value, case when t."AV_LAND_1PCT_CB_CAP" > 0 then 1 when t."AV_N_HOME_RES_LAND_2PCT_CB_CAP" > 0 then 2 when t."AV_COMM_APT_LAND_2PCT_CB_CAP" > 0 then 2 when t."AV_LTC_FAC_LAND_2PCT_CB_CAP" > 0 then 2 when t."AV_LAND_3PCT_CB_CAP" > 0 then 3 else 3 end as assessor_classification, 2 as classification, False as interesting, ''::character varying as notes, s.geom as geometry, st_centroid(s.geom) as centroid_geometry, st_area(s.geom) as area, z.label as zoning INTO tmp_20170411 FROM "TAXDATA" t
#     RIGHT JOIN state_parcels_marion_county p ON p."PARCELID"::text = t."PARCEL_NUMBER"::text
#     RIGHT JOIN parcels_with_state_id ps ON ps.stateparce::text = p."IDPARCEL"::text
#     RIGHT JOIN surplus s ON ps.parcel_c::text = s.parcel_c::text
#     LEFT JOIN zoning z on st_within(st_centroid(s.geom), st_setsrid(z.geom, 2965));

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
    CLASSIFICATION_CHOICES = ( (TAX_SALE_UNSOLD,'Tax Sale Unsold'),(SURPLUS, 'County Surplus'))
    classification = models.IntegerField(choices=CLASSIFICATION_CHOICES, default=SURPLUS)

    demolition_order = models.BooleanField(default=False)
    repair_order = models.BooleanField(default=False)

    interesting = models.NullBooleanField(default=None)
    notes = models.CharField(max_length=2048, blank=True)

    requested_from_commissioners = models.DateField(blank=True, null=True)

    geometry = models.MultiPolygonField(srid=2965)
    centroid_geometry = models.PointField(srid=2965) # compuated from geometry on save

    ## added this function to calculate centroid of the geometry on saving, as it not otherwise available.
    def save(self, *args, **kwargs):
        self.centroid_geometry = self.geometry.centroid
        self.area = self.geometry.area
        super(Parcel, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s - %s' % (self.street_address, self.parcel_number)

    def natural_key(self):
        return '%s - %s' % (self.street_address, self.parcel_number)
