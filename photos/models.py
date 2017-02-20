from django.db import models
from property_inventory.models import Property
from django.utils.text import slugify
from os.path import basename
from django.utils.safestring import mark_safe
from PIL import Image
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
        super(photo, self).save(*args, **kwargs)
        print self.image.path
        im = Image.open(self.image.path)
        im.thumbnail((1024,1024))
        im.save(self.image.path)
        print "in save"
