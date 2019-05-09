from django.db import models
#from property_inventory.models import Property as Property_inventory
#from ncst.models import Property as Property_ncst
from django.utils.text import slugify
from os.path import basename
from django.utils.safestring import mark_safe
from PIL import Image, ExifTags
from django.conf import settings

def save_location(instance, filename):
    return 'property_photos/{0}/{1}'.format(instance.prop, filename)


class photo(models.Model):
    prop = models.ForeignKey('property_inventory.Property', null=True, blank=True)
    prop_ncst = models.ForeignKey('ncst.Property', null=True, blank=True)
    main_photo = models.BooleanField(null=False, default=False)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=save_location, max_length=512, blank=False, null=False)

    def image_tag(self, width=150, height=150):
        return mark_safe('<img src="/media/{0}" width="{1}" height="{2}" />'.format(self.image, width, height))

    image_tag.short_description = 'Image'

    def __unicode__(self):
        if self.image:
            return u'%s - %s' % (self.prop, basename(self.image.path))
        return u'%s' % (self.prop, )

    def save(self, *args, **kwargs):
        super(photo, self).save(*args, **kwargs) # have to save object first to get the file in the right place
        im = Image.open(self.image.path)
        # image rotation code from http://stackoverflow.com/a/11543365/2731298
        e = None
        if hasattr(im, '_getexif'): # only present in JPEGs
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            e = im._getexif()       # returns None if no EXIF data
        if e is not None:
            exif=dict(e.items())
            orientation = exif.get(orientation, None)

            if orientation == 3:   im = im.transpose(Image.ROTATE_180)
            elif orientation == 6: im = im.transpose(Image.ROTATE_270)
            elif orientation == 8: im = im.transpose(Image.ROTATE_90)
        #im.thumbnail((1024,1024)) # don't resize images any more.
        im.save(self.image.path)
