from django.db import models
from PIL import Image
import numpy as np
from django.conf import settings
from django.db.models import Q
#from property_inventory.models import Property


def content_file_name(instance, filename):
    return '/'.join(['condition_report', instance.Property.streetAddress, filename])


class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('ATCFN','Attic, Finished'),
        ('ENBAL','Balcony, Enclosed'),
        ('MSTBD','MasterBedroom'),
        ('2BDRM','Bedroom 2nd'),
        ('3BDRM','Bedroom 3rd'),
        ('4BDRM','Bedroom 4th'),
        ('5BDRM','Bedroom 5th'),
        ('6BDRM','Bedroom 6th'),
        ('BONUS','BonusRoom'),
        ('BKFST','BreakfastRoom'),
        ('DENLB','DenLibrary'),
        ('DIN','DiningRoom'),
        ('EXRCS','ExerciseRm'),
        ('FAMLY','FamilyRoom'),
        ('GREAT','GreatRoom'),
        ('GUEST','GuestRoom'),
        ('HERTH','HearthRoom'),
        ('HMTHR','HomeTheatr'),
        ('KITCH','Kitchen'),
        ('LNDRY','LaundryRm'),
        ('LIVNG','LivingRoom'),
        ('LOFT','Loft'),
        ('MUDRM','MudRoom'),
        ('OFFIC','Office'),
        ('RECRM','Rec\/PlayRm'),
        ('SITRM','SittingRoom'),
        ('SUNRM','SunRoom'),
        ('UTILITY','Utility Room'),
        ('WINEC','WineCellar'),
        ('WRKSH','Workshop'),
    )
    room_type = models.CharField(choices=ROOM_TYPE_CHOICES, blank=False, null=False, max_length=254)

    LEVEL_CHOICES = (
        ('BASEMENT', 'Basement'),
        ('LOWER', 'Lower'),
        ('UPPER', 'Upper'),
    )

    room_level = models.CharField(choices=LEVEL_CHOICES, blank=False, null=False, max_length=254)

    FLOORING_TYPE = (
        ('B','Brick'),
        ('C','Carpeting'),
        ('H','Hardwood'),
        ('L','Laminate'),
        ('LH','Laminated Hardwood'),
        ('M','Marble'),
        ('P','Parquet'),
        ('T','Tile-Ceramic'),
        ('V','Vinyl'),
        ('VinylHardwood','Vinyl Hardwood'),
        ('O','Other')
    )

    flooring_type = models.CharField(choices=FLOORING_TYPE, blank=False, null=False, max_length=254)
    dimensions = models.CharField(max_length=7, blank=True, null=False)
    conditionreport = models.ForeignKey('property_condition.ConditionReport')

    def __unicode__(self):
        return u'{0} - {1}'.format(self.conditionreport, self.get_room_type_display())

class ConditionReport(models.Model):
    GOOD_STATUS = 3
    FAIR_STATUS = 2
    POOR_STATUS = 1
    MISSING_STATUS = 0
    NA_STATUS = None

    STATUS_CHOICES = (
        (GOOD_STATUS, 'Good / Satisfactory'),
        (FAIR_STATUS, 'Fair / Repair'),
        (POOR_STATUS, 'Poor / Replace'),
        (MISSING_STATUS, 'Missing'),
        (NA_STATUS, 'N/A'))

    def limit_property_choices():
        return Q( (Q(structureType__exact='Residential Dwelling') | Q(structureType__exact='Mixed Use Commercial')), ~Q(status__contains='Sold'))

    Property = models.ForeignKey('property_inventory.Property', limit_choices_to=limit_property_choices())
    picture = models.ImageField(upload_to=content_file_name, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    general_property_notes = models.CharField(
        max_length=512, blank=True, verbose_name='General Property Notes')


    roof_shingles = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Shingles')
    roof_shingles_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    roof_framing = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Framing')
    roof_framing_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    roof_gutters = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Gutters')
    roof_gutters_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')

    foundation_slab = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Slab')
    foundation_slab_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    foundation_crawl = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Crawlspace')
    foundation_crawl_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')

    exterior_siding_brick = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Brick')
    exterior_siding_brick_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    exterior_siding_vinyl = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Vinyl')
    exterior_siding_vinyl_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    exterior_siding_wood = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Wood')
    exterior_siding_wood_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    exterior_siding_other = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Other')
    exterior_siding_other_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')

    windows = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Windows')
    windows_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    garage = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Garage')
    garage_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    fencing = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Fencing')
    fencing_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    landscaping = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Landscaping')
    landscaping_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    doors = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Doors')
    doors_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    kitchen_cabinets = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Kitchen Cabinets')
    kitchen_cabinets_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')

    flooring_subflooring = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Subflooring')
    flooring_subflooring_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    flooring_covering = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Covering')
    flooring_covering_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')

    electrical_knob_tube_cloth = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Knob, tube and cloth')
    electrical_knob_tube_cloth_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    electrical_standard = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Standard')
    electrical_standard_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')

    plumbing_metal = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Copper / metal')
    plumbing_metal_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    plumbing_plastic = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='PVC / PEX')
    plumbing_plastic_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')

    walls_drywall = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Drywall')
    walls_drywall_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    walls_lathe_plaster = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Plaster and lathe')
    walls_lathe_plaster_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')

    hvac_furance = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Furnace')
    hvac_furance_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    hvac_duct_work = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Duct work')
    hvac_duct_work_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')
    hvac_air_conditioner = models.IntegerField(
        choices=STATUS_CHOICES, null=True, blank=True, verbose_name='AC')
    hvac_air_conditioner_notes = models.CharField(
        max_length=512, blank=True, verbose_name='Notes')

    @property
    def condition_avg(self):
        condition_array = [self.roof_shingles, self.roof_framing, self.roof_gutters, self.foundation_slab, self.foundation_crawl, self.exterior_siding_brick, self.exterior_siding_vinyl, self.exterior_siding_wood, self.exterior_siding_other, self.windows, self.garage, self.fencing, self.landscaping,
                           self.doors, self.kitchen_cabinets, self.flooring_subflooring, self.electrical_knob_tube_cloth, self.electrical_standard, self.plumbing_metal, self.plumbing_plastic, self.walls_drywall, self.walls_lathe_plaster, self.hvac_furance, self.hvac_duct_work, self.hvac_air_conditioner]
        clean = [x for x in condition_array if x is not None]
        return np.round(np.mean(clean), 1)

    def save(self, size=(400, 300)):
        """
        Save Photo after ensuring it is not blank.  Resize as needed.
        """
        #print "Does the object already exist?", self.id
        if not self.id:
            super(ConditionReport, self).save()

            if self.picture:
                filename = self.picture.path
                image = Image.open(filename)

                image.thumbnail(size, Image.ANTIALIAS)
                image.save(filename)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.Property, self.timestamp)
