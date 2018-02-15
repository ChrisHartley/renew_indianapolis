# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis import admin
from .models import registered_organization, blacklisted_emails

class registered_organization_admin(admin.OSMGeoAdmin):
    search_fields = ( 'name', 'first_name', 'last_name', 'email', )

class blacklisted_emails_admin(admin.OSMGeoAdmin):
    search_fields = ('name', 'email')

admin.site.register(registered_organization, registered_organization_admin)
admin.site.register(blacklisted_emails, blacklisted_emails_admin)
