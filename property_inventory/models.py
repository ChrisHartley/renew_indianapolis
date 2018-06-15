from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.models import User
import datetime # used for price_change summary view
from django.apps import apps
from django.utils.text import slugify

### This is the parent model inherited by various overlay models, collections of geometries
### such as zip codes, census tracts, CDC focus areas, etc that a Property (below) could fall within.
### These are calculated when the Property is first created. I believe I tried not having a ForeignKey in the
### Property definition but it was crazy slow to compute st_within for all the properties 3-4 times. It would be
### more elegant though.
class Overlay(models.Model):
    name = models.CharField(max_length=255)
    geometry = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    @property
    def area(self):
        return GEOSGeometry(self.geometry).area

    def __unicode__(self):
        return u'%s' % (self.name)

    def natural_key(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['name']


class Zipcode(Overlay):
    pass


class CDC(Overlay):
    CDCtype = models.CharField(max_length=50)


class Zoning(Overlay):
    pass

class Neighborhood(Overlay):
    pass

class ContextArea(Overlay):
    disposition_strategy = models.CharField(max_length=50)

class MVAClassifcation(Overlay):
    mva_cat = models.CharField(max_length=10)

### The Property model is the heart of blight_fight. A Property is a parcel of land with a unique identifier, the
### parcel number. It has various attributes, including geometry, and can fall within a Overlay geometry (above).
###
###
class Property(models.Model):

    PROPERTY_TYPES = (('lb', 'Landbank'), ('sp', 'County Owned Surplus'))

    geometry = models.MultiPolygonField(srid=4326)

    centroid_geometry = models.PointField(srid=4326, default='POINT(39.7684 86.1581)')

    objects = models.GeoManager()
    propertyType = models.CharField(
        choices=PROPERTY_TYPES, max_length=2, verbose_name='property type')

    parcel = models.CharField(
        max_length=7, unique=True, help_text="The 7 digit local parcel number for a property, ex 1052714", verbose_name='parcel number')
    streetAddress = models.CharField(
        max_length=255, help_text="Supports partial matching, so you can enter either the full street address (eg 1425 E 11TH ST) to find one property or just the street name (eg 11th st) to find all the properties on that street.", verbose_name='Street Address')
    nsp = models.BooleanField(
        default=False, help_text="If a property comes with requirements related to the Neighborhood Stabilization Program.", verbose_name='NSP')
    quiet_title_complete = models.BooleanField(
        default=False, help_text="If quiet title process has been completed.", verbose_name='Quiet Title Complete')
    # should restrict this with choices using valid strings as options to catch mis-spellings.
    structureType = models.CharField(max_length=255, null=True, blank=True,
                                     help_text="As classified by the Assessor", verbose_name='Structure Type')

    cdc = models.ForeignKey(CDC, blank=True, null=True,
                            help_text="The Community Development Corporation boundries the property falls within.", verbose_name='CDC')
    zone = models.ForeignKey(
        Zoning, blank=True, null=True, help_text="The zoning of the property")
    neighborhood = models.ForeignKey(
        Neighborhood, blank=True, null=True, help_text="The neighborhood the property is in")
    zipcode = models.ForeignKey(
        Zipcode, blank=True, null=True, help_text="The zipcode of the property")
    urban_garden = models.BooleanField(
        default=False, help_text="If the property is currently licensed as an urban garden through the Office of Sustainability")
    status = models.CharField(max_length=255, null=True, blank=True,
                              help_text="The property's status with Renew Indianapolis")
    sidelot_eligible = models.BooleanField(
        default=False, help_text="If the property is currently elgibile for the side-lot program")
    price = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="The price of the property", null=True)
    area = models.FloatField(help_text="The parcel area in square feet")
    # change to foreign key when ready
    applicant = models.CharField(
        max_length=255, blank=True, null=True, help_text="Name of current applicant for status page")
    homestead_only = models.BooleanField(
        default=False, help_text="Only available for homestead applications")
    bep_demolition = models.BooleanField(
        default=False, help_text="Slated for demolition under the Blight Elimination Program", verbose_name="Slated for BEP demolition")
    project_agreement_released = models.BooleanField(
        default=False, help_text="Has the project agreement on a sold property been released?")
    is_active = models.BooleanField(
        default=True, help_text="Is this property listing active?")
    price_obo = models.BooleanField(
        default=False, help_text="Price is Or Best Offer", verbose_name="Price is 'Or Best Offer'")
    renew_owned = models.BooleanField(
        default=False, help_text="Property is owned directly by Renew Indianapolis or a wholly owned subsidiary.", verbose_name="Owned by Renew Indianapolis directly")
    hhf_demolition = models.BooleanField(default=False, help_text="Property was demolished through Hardest Hit Funds/Blight Elimination Program, and may have restrictions on end use.",
        verbose_name="Property was demolished through Hardest Hit Funds/Blight Elimination Program")
    vacant_lot_eligible = models.BooleanField(default=False, help_text="Property is eligible for sale through the vacant lot program.")
    short_legal_description = models.CharField(max_length=2048, blank=True)
    #slug = AutoSlugField(always_update=True, unique=True, populate_from=lambda instance: instance.streetAddress + instance.parcel)

    acquisition_date =  models.DateField(null=True, blank=True, help_text='Date property was acquired')
    buyer_application = models.ForeignKey('applications.Application', null=True, blank=True, help_text='The final buyer application.')

    property_inspection_group = models.CharField(blank=True, max_length=10)

    class Meta:
        verbose_name_plural = "properties"
        ordering = ['streetAddress', 'parcel']
    def natural_key(self):
        return u'%s - %s' % (self.streetAddress, self.parcel)

    def __unicode__(self):
        return u'%s - %s' % (self.streetAddress, self.parcel)

    ## added this function to calculate centroid of the geometry on saving, as it not otherwise available.
    def save(self, *args, **kwargs):
        self.centroid_geometry = self.geometry.centroid
        super(Property, self).save(*args, **kwargs)
"""
Add notes to properties, for staff use.
Added 20170630.
"""
class note(models.Model):
    Property = models.ForeignKey(Property)
#    user = models.ForeignKey(User)
    text = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'{0}...'.format(self.text[0:12],)

def price_change_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'price_change/{0}/{1}/{2}'.format(slugify(instance.Property), instance.datestamp, filename)


class price_change(models.Model):
    Property = models.ForeignKey(Property)
    proposed_price = models.DecimalField(max_digits=8, decimal_places=2,
        help_text="The proposed new price for the property", null=False)
    notes = models.CharField(max_length=1024, blank=True)
    # meeting is the PriceChangeMeetingLink accessor
    datestamp = models.DateField(auto_now_add=True)
    approved = models.NullBooleanField()
    acquisition_date = models.DateField(null=True)
    assessed_land_value = models.IntegerField(null=True)
    assessed_improvement_value = models.IntegerField(null=True)
    cma = models.FileField(upload_to=price_change_directory_path, null=True, blank=True)

    @property
    def inquiries_previous_30_days(self):
        end_day = datetime.date.today()
        start_day = end_day - datetime.timedelta(30)
        return apps.get_model('property_inquiry', 'propertyInquiry').objects.filter(Property=self.Property).filter(timestamp__range=(start_day, end_day)).count()

    @property
    def inquiries_previous_60_days(self):
        end_day = datetime.date.today()
        start_day = end_day - datetime.timedelta(60)
        return apps.get_model('property_inquiry', 'propertyInquiry').objects.filter(Property=self.Property).filter(timestamp__range=(start_day, end_day)).count()

    @property
    def inquiries_previous_90_days(self):
        end_day = datetime.date.today()
        start_day = end_day - datetime.timedelta(90)
        return apps.get_model('property_inquiry', 'propertyInquiry').objects.filter(Property=self.Property).filter(timestamp__range=(start_day, end_day)).count()

    @property
    def inquiries_previous_180_days(self):
        end_day = datetime.date.today()
        start_day = end_day - datetime.timedelta(180)
        return apps.get_model('property_inquiry', 'propertyInquiry').objects.filter(Property=self.Property).filter(timestamp__range=(start_day, end_day)).count()


    def __unicode__(self):
        return '{0} - {1} - {2}'.format(self.Property, self.datestamp, self.proposed_price)

    class Meta:
        verbose_name = 'price change'
        verbose_name_plural = 'price changes'

class featured_property(models.Model):
    Property = models.ForeignKey(Property, related_name='featured_property')
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.CharField(max_length=1024, blank=True)

    class Meta:
        verbose_name = 'featured property'
        verbose_name_plural = 'featured properties'

    def __unicode__(self):
        return u'{0}, {1} - {2} - {3}'.format(self.Property, self.start_date, self.end_date, self.note[:15])

class blc_listing(models.Model):
        Property = models.ForeignKey(Property, related_name='blc_listing')
        blc_id = models.CharField(max_length=50, blank=False)
        blc_url = models.URLField(max_length=255, blank=True)
        date_time = models.DateTimeField(auto_now_add=True)
        note = models.CharField(max_length=1024, blank=True)
        active = models.BooleanField(default=True)
        def __unicode__(self):
            return u'{0} - {1} - {2}'.format(self.Property, self.blc_id, self.date_time)

class yard_sign(models.Model):
    Property = models.ForeignKey(Property, related_name='yard_sign')
    date_time = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=1024, blank=True)
    removed_date_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'yard sign'
        verbose_name_plural = 'yard signs'

    def __unicode__(self):
        return u'{0} - {1} - {2}'.format(self.Property, self.date_time, self.note[:20])

class take_back(models.Model):
    Property = models.ForeignKey(Property, related_name='take_back')
    take_back_date = models.DateField(blank=False)
    original_sale_date = models.DateField(blank=False)
    original_sale_price = models.DecimalField(max_digits=8, decimal_places=2)
    note = models.TextField(max_length=1024, blank=True)
    owner = models.CharField(max_length=1024, blank=True)
    application = models.ForeignKey('applications.Application', null=True, blank=True)

    class Meta:
        verbose_name = 'take back'
        verbose_name_plural = 'take back'

    def __unicode__(self):
        return u'{0} - {1}'.format(self.Property, self.owner)

    def save(self, *args, **kwargs):
        if self.application is not None:
            self.owner = self.application.applicant
        if self.application is None and self.owner == '':
            return
        super(take_back, self).save(*args, **kwargs)  # Call the "real" save() method.
