# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#from django.contrib import admin
from django.contrib.gis import admin

from .models import registered_organization, blacklisted_emails
# Register your models here.
class registered_organization_admin(admin.OSMGeoAdmin):
    pass
admin.site.register(registered_organization, registered_organization_admin)
admin.site.register(blacklisted_emails)
