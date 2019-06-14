# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class registered_organization(gis_models.Model):
    name = models.CharField(blank=True, max_length=555)
    first_name = models.CharField(blank=True, max_length=555)
    last_name = models.CharField(blank=True, max_length=555)
    email = models.EmailField(blank=True, null=True)
    geometry = gis_models.PolygonField(srid=4326)

    def __str__(self):
        return '{0} - {1}'.format(self.name, self.email)

@python_2_unicode_compatible
class blacklisted_emails(models.Model):
    name = models.CharField(blank=True, max_length=255)
    email = models.CharField(blank=True, max_length=255)
    reason = models.TextField(blank=True)

    def __str__(self):
        return '{0} - {1}'.format(self.email, self.reason[:15])
