# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from arcgis import ArcGIS
from .models import registered_organization, blacklisted_emails
from property_inventory.models import Property
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal.error import GDALException
from django.db import IntegrityError
from django.views.generic.base import TemplateView



# Pull updated list of registered organizations from the city's public list
def update_registered_organizations(request):
    URL = 'http://xmaps.indy.gov/arcgis/rest/services/RegisteredOrganizations/RegisteredOrganizations/MapServer'
    LAYER = 0

    # clear out the db of previous registered organizations
    number_deleted = registered_organization.objects.all().delete()

    service = ArcGIS(URL)
    geojson = service.get(LAYER, fields='*')
    records = geojson['features']
    number_created = 0
    number_errors = 0
    for record in records:
        try:
            geometry = GEOSGeometry(str(record['geometry']))
            if not geometry.valid:
                geometry = geometry.buffer(0)
        except GDALException, ValueError:
            number_errors = number_errors + 1
            #print "Error on", record['properties']['ORG_NAME']
        try:
            x = registered_organization(
                name=record['properties']['ORG_NAME'],
                first_name=record['properties']['FIRSTNAME'],
                last_name=record['properties']['LASTNAME'],
                email=record['properties']['EMAIL'],
                geometry=geometry,
                )
            x.save()
            if registered_organization.objects.filter(geometry__isvalid=True).filter(id=x.id).count() == 0:
                #print "Error, invalid geometry", record['properties']['ORG_NAME']
                pass
            else:
                number_created = number_created + 1
        except IntegrityError:
            number_errors = number_errors + 1
            #print "IntegrityError on ", record['properties']['ORG_NAME']
    return HttpResponse('<html><body><ul><li>Number deleted: {0}</li><li>Number created: {1}</li><li>Number errors: {2}</li></ul></body></html>'.format(number_deleted[0], number_created, number_errors))


class RelevantOrganizationsView(TemplateView):
    template_name = "relevant_organizations.html"
    def get_context_data(self, **kwargs):
        context = super(RelevantOrganizationsView, self).get_context_data(**kwargs)
        parcel = self.kwargs['parcel']
        prop = Property.objects.get(parcel=parcel)
        orgs = registered_organization.objects.filter(geometry__contains=prop.geometry).exclude(email='n/a').order_by('-geometry')

        recipient = []
        org_names = []
        for o in orgs:
            if o.email and blacklisted_emails.objects.filter(email=o.email).count() == 0: # check if email exists in blacklist (bounces, opt-out, etc)
                recipient.append(o.email)
                org_names.append(o.name)
            else:
                pass
        context['recipients'] =  recipient
        context['organizations'] = org_names

        return context
