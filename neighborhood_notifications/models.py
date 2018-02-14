# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.gis.db import models as gis_models

from applications.models import Application
# Create your models here.
# message
## application
## datetime
## recepient emails
## recipient orgs
## body
## subject
## files
def default_body():

    return


class message(models.Model):
    body = models.TextField(blank=False)
    subject = models.CharField(max_length=50, blank=False)
    recipient_emails = models.TextField(blank=True)
    recipient_names = models.TextField(blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    modified_timestamp = models.DateTimeField(auto_now=True)
    sent_timestamp = models.DateTimeField()
    sent = models.BooleanField(default=False)
    application = models.ForeignKey(Application, null=False, blank=False)
    #files


class registered_organization(gis_models.Model):
    name = models.CharField(blank=True, max_length=555)
    first_name = models.CharField(blank=True, max_length=555)
    last_name = models.CharField(blank=True, max_length=555)
    email = models.EmailField(blank=True, null=True)
    geometry = gis_models.PolygonField(srid=4326)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.name, self.email)


class blacklisted_emails(models.Model):
    name = models.CharField(blank=True, max_length=255)
    email = models.CharField(blank=True, max_length=255)
    reason = models.TextField(blank=True)
