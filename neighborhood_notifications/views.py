# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from arcgis import ArcGIS
from .models import registered_organization
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal.error import GDALException
from django.db import IntegrityError

# Create your views here.
def update_registered_organizations(request):
    URL = 'http://imaps.indy.gov/arcgis/rest/services/RegisteredOrganizations/MapServer/'
    LAYER = 0

    # clear out the db of previous registered organizations
    number_deleted = registered_organization.objects.all().delete()

    service = ArcGIS(URL)
    geojson = service.get(LAYER)

    number_created = 0
    number_errors = 0
    for record in geojson['features']:
        try:
            geometry = GEOSGeometry(str(record['geometry']))
            if not geometry.valid:
                #raise ValueError('The geometry was invalid')
                geometry=None
        except GDALException, ValueError:
            number_errors = number_errors + 1
            break
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
                print "Error, invalid geometry"
            number_created = number_created + 1
        except IntegrityError:
            number_errors = number_errors + 1
    return HttpResponse('<html><body><ul><li>Number deleted: {0}</li><li>Number created: {1}</li><li>Number errors: {2}</li></ul></body></html>'.format(number_deleted[0], number_created, number_errors))
