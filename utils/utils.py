# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.files import FileField
import inspect
def batch_update_view(model_admin, request, queryset, field_names=None, exclude_field_names=None):

        # removes fields not included in field_names
    def remove_fields(form, field_names):
        for field in list(form.base_fields.keys()):
            if not field in field_names:
                del form.base_fields[field]
        return form

        # the return value is the form class, not the form class instance
    f = model_admin.get_form(request)
    # If no field names are given, do them all
    if field_names is None:
        field_names = f.base_fields.keys()
    if exclude_field_names is not None:
        # should do this with list comprehension
        temp_names = []
        for n in field_names:
            if n not in exclude_field_names:
                temp_names.append(n)
        field_names = temp_names
    form_class = remove_fields(f, field_names)
    if request.method == 'POST':
        form = form_class()
        # for this there is a hidden field 'form-post' in the html template the edit is confirmed
        if 'form-post' in request.POST:
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                for item in queryset.all():
                    changed_list = []
                    for field_name in field_names:
                        if request.POST.get('{}_use'.format(field_name,)) == 'on':
                            if item._meta.get_field(field_name).__class__ is FileField:
                                setattr(item, field_name, request.FILES[field_name])
                            else:
                                setattr(item, field_name, form.cleaned_data[field_name])
                            changed_list.append(field_name)
                    if len(changed_list) > 0:
                        l = LogEntry(
                                    user=request.user,
                                    content_type=ContentType.objects.get_for_model(model_admin.model, for_concrete_model=False),
                                    object_id=item.pk,
                                    object_repr=unicode(item),
                                    action_flag=CHANGE,
                                    change_message = 'Changed {}'.format(', '.join(changed_list),),
                                    )
                        l.save()
                    item.save()
                model_admin.message_user(request, "Bulk updated {} records".format(queryset.count()))
                return HttpResponseRedirect(request.get_full_path())
        return render(
            request,
            'admin/batch_editing_intermediary.html',
            context={
                'form': form,
                'items': queryset,
                'fieldnames': field_names,
                'media': model_admin.media,
            }
        )

import pyclamd
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
def virus_scan(input_file):
    try:
        cd = pyclamd.ClamdUnixSocket()
        # test if server is reachable
        cd.ping()
    except pyclamd.ConnectionError:
        # if failed, test for network socket
        cd = pyclamd.ClamdNetworkSocket()
    try:
        cd.ping()
    except pyclamd.ConnectionError:
        raise ValueError('could not connect to clamd server either by unix or network socket')

    scan_results = cd.scan_stream(input_file.read())
    if scan_results is not None:
        #print 'Virus found:', scan_results
        send_mail('Django Virus Scanner Results', 'Virus scanner returned - {0}'.format(scan_results,), 'info@renewindianapolis.org',
    ['chris.hartley@renewindianapolis.org'], fail_silently=False)
        raise ValidationError(
            'Virus scanner returned %(value)s',
            params={'value': scan_results},
        )


import requests
import json
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, LinearRing, Polygon
import logging
def pull_property_info_from_arcgis(parcel, request_type='json'):
    if request_type == 'geojson':
        city_arcgis_url = 'http://xmaps.indy.gov/arcgis/rest/services/MapIndy/MapIndyProperty/MapServer/10/query?where=PARCEL_C%3D%27{0}%27&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentsOnly=false&datumTransformation=&parameterValues=&rangeValues=&f=geojson'.format(parcel,)

        logger = logging.getLogger(__name__)

        r = requests.get(city_arcgis_url)
        try:
            r.raise_for_status()
            response_json = r.json()
            if response_json.get('error', None) != None:
                raise requests.exceptions.HTTPError
        except ValueError:
            #print('ValueError, no valid json in response?')
            logger.error('Error parsing response from ArcGIS server - ValueError')
            return False
        except requests.exceptions.HTTPError as e:
            #print('Response error')
            logger.error('Error getting response from ArcGIS server or server returned error - HTTPError, {}'.format(e,))
            return False

        data = {}
        stname, stnumber, pre_dir, zipcode, geometry = '', '', '', '', ''

        try:
            stname = response_json['features'][0]['properties']['FULL_STNAME'] or ''
            stnumber = response_json['features'][0]['properties']['STNUMBER'] or ''
            pre_dir = response_json['features'][0]['properties']['PRE_DIR'] or ''
            zipcode = response_json['features'][0]['properties']['ZIPCODE'] or ''
            geometry = MultiPolygon(GEOSGeometry(json.dumps(response_json['features'][0]['geometry'])))
            state_parcel = response_json['features'][0]['properties']['STATEPARCELNUMBER'] or ''
            assessed_land_value = response_json['features'][0]['properties']['ASSESSORYEAR_LANDTOTAL'] or ''
            assessed_improvement_value = response_json['features'][0]['properties']['ASSESSORYEAR_IMPTOTAL'] or ''
            estsqft = response_json['features'][0]['properties']['ESTSQFT'] or ''

        except IndexError as e:
            #print('Data not found in response: {}'.format(e,))
            logger.error('Error parsing response from ArcGIS server - IndexError')
        except KeyError as e:
            #print('Data not found in response: {}'.format(e,))
            #print(response_json)
            logger.error('Error parsing response from ArcGIS server - KeyError: {}'.format(e,))


        else:
            data['street_address'] = '{} {} {}'.format(stnumber, pre_dir, stname)
            data['zipcode'] = zipcode
            data['geometry'] = geometry
            data['state_parcel'] = state_parcel
            data['assessed_land_value'] = assessed_land_value
            data['assessed_improvement_value'] = assessed_improvement_value
            data['estsqft'] = estsqft

        return data

    if request_type == 'json':
        city_arcgis_url = 'http://xmaps.indy.gov/arcgis/rest/services/MapIndy/MapIndyProperty/MapServer/10/query?where=PARCEL_C%3D%27{0}%27&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentsOnly=false&datumTransformation=&parameterValues=&rangeValues=&f=json'.format(parcel,)

        logger = logging.getLogger(__name__)

        r = requests.get(city_arcgis_url)
        try:
            r.raise_for_status()
            response_json = r.json()
            if response_json.get('error', None) != None:
                raise requests.exceptions.HTTPError
        except ValueError:
            #print('ValueError, no valid json in response?')
            logger.error('Error parsing response from ArcGIS server - ValueError')
            return False
        except requests.exceptions.HTTPError as e:
            #print('Response error')
            logger.error('Error getting response from ArcGIS server or server returned error - HTTPError, {}'.format(e,))
            return False

        data = {}
        stname, stnumber, pre_dir, zipcode, geometry = '', '', '', '', ''

        try:
            stname = response_json['features'][0]['attributes']['FULL_STNAME'] or ''
            stnumber = response_json['features'][0]['attributes']['STNUMBER'] or ''
            pre_dir = response_json['features'][0]['attributes']['PRE_DIR'] or ''
            zipcode = response_json['features'][0]['attributes']['ZIPCODE'] or ''
            geometry = MultiPolygon(Polygon(LinearRing(response_json['features'][0]['geometry']['rings'][0], srid=2965), srid=2965), srid=2965)
            state_parcel = response_json['features'][0]['attributes']['STATEPARCELNUMBER'] or ''
            assessed_land_value = response_json['features'][0]['attributes']['ASSESSORYEAR_LANDTOTAL'] or ''
            assessed_improvement_value = response_json['features'][0]['attributes']['ASSESSORYEAR_IMPTOTAL'] or ''
            estsqft = response_json['features'][0]['attributes']['ESTSQFT'] or ''

        except IndexError as e:
            logger.error('Error parsing response from ArcGIS server - IndexError')
        except KeyError as e:

            logger.error('Error parsing response from ArcGIS server - KeyError: {}'.format(e,))


        else:
            data['street_address'] = '{} {} {}'.format(stnumber, pre_dir, stname)
            data['zipcode'] = zipcode
            data['geometry'] = geometry
            data['state_parcel'] = state_parcel
            data['assessed_land_value'] = assessed_land_value
            data['assessed_improvement_value'] = assessed_improvement_value
            data['estsqft'] = estsqft

        return data
