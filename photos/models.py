from django.db import models
from property_inventory.models import Property
from django.utils.text import slugify
from os.path import basename
from django.utils.safestring import mark_safe
from PIL import Image, ExifTags
from django.conf import settings

def save_location(instance, filename):
    return 'property_photos/{0}/{1}'.format(instance.prop, filename)


class photo(models.Model):
    prop = models.ForeignKey(Property, null=False)
    main_photo = models.BooleanField(null=False, default=False)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=save_location, max_length=512, blank=False, null=False)

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.image))

    image_tag.short_description = 'Image'

    def __unicode__(self):
        if self.image:
            return '%s - %s' % (self.prop, basename(self.image.path))
        return '%s' % (self.prop, )

    def save(self, *args, **kwargs):
        super(photo, self).save(*args, **kwargs) # have to save object first to get the file in the right place
        im = Image.open(self.image.path)
        # image rotation code from http://stackoverflow.com/a/11543365/2731298
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
        im.thumbnail((1024,1024))
        im.save(self.image.path)
