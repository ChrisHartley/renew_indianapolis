from django.db import models
#from property_inventory.models import Property as Property_inventory
#from ncst.models import Property as Property_ncst
from django.utils.text import slugify
from os.path import basename
from django.utils.safestring import mark_safe
from django.urls import reverse
from PIL import Image, ExifTags
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

def save_location(instance, filename):
    return 'property_photos/{0}/{1}'.format(instance.prop or instance.prop_ncst or instance.prop_surplus or 'no_property', filename)

@python_2_unicode_compatible
class photo(models.Model):
    prop = models.ForeignKey('property_inventory.Property', null=True, blank=True, on_delete=models.CASCADE)
    prop_ncst = models.ForeignKey('ncst.Property', null=True, blank=True, on_delete=models.CASCADE)
    prop_surplus = models.ForeignKey('surplus.parcel', null=True, blank=True, on_delete=models.CASCADE)
    main_photo = models.BooleanField(null=False, default=False)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=save_location, max_length=512, blank=False, null=False)

    def image_tag(self, width=150, height=150):
        if self.id is not None:
            return mark_safe('<a href="{0}"><img src="/media/{1}" width="{2}" height="{3}" /></a>'.format(
                reverse("send_class_file", kwargs={'app_name': 'photos', 'class_name': 'photo', 'pk':self.id, 'field_name':'image'}),
                self.image,
                width,
                height)
            )

    image_tag.short_description = 'Image'

    def __str__(self):
        if self.image:
            return '{} - {}'.format(instance.prop or instance.prop_ncst or instance.prop_surplus or 'no_property', basename(self.image.path) )
            #return '%s - %s' % (self.prop, basename(self.image.path))
        return '{}'.format(instance.prop or instance.prop_ncst or instance.prop_surplus or 'no_property')

    def save(self, *args, **kwargs):
        super(photo, self).save(*args, **kwargs) # have to save object first to get the file in the right place
        im = Image.open(self.image.path)
        # image rotation code from http://stackoverflow.com/a/11543365/2731298
        e = None
        if hasattr(im, '_getexif'): # only present in JPEGs
            for orientation in list(ExifTags.TAGS.keys()):
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            e = im._getexif()       # returns None if no EXIF data
        if e is not None:
            exif=dict(list(e.items()))
            orientation = exif.get(orientation, None)

            if orientation == 3:   im = im.transpose(Image.ROTATE_180)
            elif orientation == 6: im = im.transpose(Image.ROTATE_270)
            elif orientation == 8: im = im.transpose(Image.ROTATE_90)
        #im.thumbnail((1024,1024)) # don't resize images any more.
        im.save(self.image.path)
