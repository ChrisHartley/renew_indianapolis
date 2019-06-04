# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
import mimetypes
import os
from django.http import HttpResponse
from wsgiref.util import FileWrapper

import xlsxwriter
from os.path import getmtime
import datetime
from ePP_simple_api import ePPHelper
from property_inventory.models import Property, MVAClassifcation, blc_listing
from django.views import View
from django.utils import timezone

def fetch_epp_inventory(request):
    ### This is a utility to create an Excel spreadsheet of properties from the
    ### ePropertyPlus API. One use case could be to have an always up-to-date
    ### inventory spreadsheet available for users to download.
    ### GPL v3 license, by Chris Hartley, Renew Indianapolis.
    ### chris.hartley@renewindianapolis.org

    FILENAME = '/tmp/inventory.xlsx'
    REFRESH_SECONDS = 300
    # Define the fields to write to the spreadsheet.
    # Column name, field name from response json.
    fields = (
        ('Parcel', 'parcelNumber'),
        ('Street Address', 'propertyAddress1'),
        ('ZIP Code','postalCode'),
        ('Property Class','propertyClass'),
        ('Neighborhood', 'neighborhood'),
        ('Price', 'askingPrice'),
        ('Zoning','zonedAs'),
        ('Parcel Size','parcelSquareFootage'),
        ('Sales Programs Eligible','s_custom_0001'),
        ('Status','currentStatus'),
        #('Vacant Lot Program Eligible',''),
        #('Property ID', 'id'),
    )

    try:
        mtime = getmtime(FILENAME)
    except OSError:
        mtime = 0
    tdelta = datetime.datetime.now() - datetime.datetime.fromtimestamp(mtime)

    if tdelta.total_seconds() > REFRESH_SECONDS:
        workbook = xlsxwriter.Workbook(FILENAME)
        worksheet = workbook.add_worksheet('Available Landbank Inventory')
        sold_worksheet = workbook.add_worksheet('Sold Properties - Not Available')
        pending_worksheet = workbook.add_worksheet('Sale Pending Properties')
        bep_worksheet = workbook.add_worksheet('Demolition Pending Properties')
        currency_format = workbook.add_format()
        currency_format.set_num_format(0x05)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(3, 3, 25)
        currency_fields = (5,)


        epp = ePPHelper(sandbox=False, debug=False)
        json_obj = epp.get_published_properties()

        if json_obj['success'] == True:

            # Write column names across the first row.
            for indx,field in enumerate(fields):
                worksheet.write(0, indx, field[0])
                sold_worksheet.write(0, indx, field[0])
                pending_worksheet.write(0, indx, field[0])
                bep_worksheet.write(0, indx, field[0])

            # For each record returned, write the fields we care about to the spreadsheet.
            sold_counter = 1 # so ugly now, it was beautiful
            available_counter = 1
            pending_counter = 1
            bep_counter = 1
            for row,record in enumerate(json_obj['rows'], start=1):
                if record['currentStatus'] == 'Available':
                    counter = available_counter
                    available_counter = available_counter + 1
                    active_sheet = worksheet
                elif record['currentStatus'] == 'Sold':
                    counter = sold_counter
                    sold_counter = sold_counter + 1
                    active_sheet = sold_worksheet
                elif record['currentStatus'] == 'Sale Pending':
                    counter = pending_counter
                    pending_counter = pending_counter + 1
                    active_sheet = pending_worksheet
                elif record['currentStatus'] == 'BEP Slated':
                    counter = bep_counter
                    bep_counter = bep_counter + 1
                    active_sheet = bep_worksheet
                else:
                    counter = available_counter
                    available_counter = available_counter + 1
                    active_sheet = worksheet


                for indx,field in enumerate(fields):

                    if indx in currency_fields:
                        active_sheet.write(counter, indx, record[field[1]], currency_format)
                    else:
                        active_sheet.write(counter, indx, record[field[1]])

        else:
            print("Endpoint returned success = false")
            return HttpResponse(status=500)
        workbook.close()
        os.chmod(FILENAME, 0o777)
    else:
        print('File cached, not re-fetching.')
    wrapper = FileWrapper(open(FILENAME,'rb'))
    content_type = mimetypes.MimeTypes().guess_type(FILENAME)[0]
    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(FILENAME)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(FILENAME))
    return response

import collections
class propertyImportCreator(View):
    def get(self, request, *args, **kwargs):
        parcel = kwargs.pop('parcel', None)
        prop = get_object_or_404(Property, parcel=parcel)

        sales_program = 'Homestead'
        if not prop.homestead_only:
            sales_program += '|Standard'
        if prop.future_development_program_eligible:
            sales_program += '|Future Development Lot'

        property_class = 'Residential Vacant Lot'
        if prop.structureType == 'Residential Dwelling':
            property_class = 'Residential Building'
        if prop.structureType == 'Mixed Use Commercial':
            property_class = 'Commercial Building'

        blc_id = ''
        blc = blc_listing.objects.filter(Property=prop).first()
        if blc:
            blc_id = blc.blc_id

        property_status = 'Available'
        if 'Sold' in prop.status:
            property_status = 'Sold'
        if 'Sale' in prop.status:
            property_status = 'Sale Pending'

        d = collections.OrderedDict()
        d['Parcel Number'] = prop.parcel,
        d['Property Status'] = property_status,
        d['Property Class'] = property_class,
        d['Owner Party Number'] = '',
        d['Owner Party External System Id'] = 'INDY1001' if prop.renew_owned else 'INDY1000',
        d['Property Address.Address1'] = prop.streetAddress,
        d['Property Address.Address2'] = '',
        d['Property Address.City'] = 'INDIANAPOLIS',
        d['Property Address.County'] = 'MARION',
        d['Property Address.State'] = 'IN',
        d['Property Address.Postal Code'] = prop.zipcode.name,
        d['Status Date'] = '',
        d['Property Manager Party Number'] = '',
        d['Property Manager Party External System Id'] = 'INDY1005' if prop.renew_owned else 'INDY1003',
        d['Update'] = '',
        d['Available'] = 'Y' if prop.status == 'Available' else 'N',
        d['Foreclosure Year'] = '',
        d['Inventory Type'] = 'Land Bank', ###
        d['Legal Description'] = prop.short_legal_description,
        d['Listing Comments'] = '',
        d['Maintenance Manager Party External System Id'] = 'INDY1008' if prop.renew_owned else 'INDY1007',
        d['Maintenance Manager Party Number'] = '',
        d['Parcel Square Footage'] = prop.area,
        d['Parcel Length'] = prop.geometry[0].transform(2965, clone=True).extent[2] - prop.geometry[0].transform(2965, clone=True).extent[0],
        d['Parcel Width'] = prop.geometry[0].transform(2965, clone=True).extent[3] - prop.geometry[0].transform(2965, clone=True).extent[1],
        d['Published'] = 'Y' if prop.is_active and 'Available' in prop.status else 'N',
        d['Tags'] = '',
        d['Latitude'] = prop.centroid_geometry.y,
        d['Longitude'] = prop.centroid_geometry.x,
        d['Parcel Boundary'] = prop.geometry.wkt,
        d['Census Tract'] = prop.census_tract.name,
        d['Congressional District'] = '',
        d['Legislative District'] = '',
        d['Local District'] = '',
        d['Neighborhood'] = prop.neighborhood.name,
        d['School District'] = '',
        d['Voting Precinct'] = '',
        d['Zoned As'] = prop.zone.name,
        d['Acquisition Amount'] = '',
        d['Acquisition Date'] = prop.renew_acquisition_date if prop.renew_owned else prop.acquisition_date,
        d['Acquisition Method'] = '',
        d['Sold Amount'] = prop.price if 'Sold' in prop.status else '',
        d['Sold Date'] = prop.status[-10] if 'Sold' in prop.status else '',
        d['Actual Disposition'] = '',
        d['Asking Price'] = prop.price,
        d['Assessment Year'] = '',
        d['Current Assessment'] = '',
        d['Minimum Bid Amount'] = '',
        d['Block Condition'] = '',
        d['Brush Removal'] = '',
        d['Cleanup Assessment'] = '',
        d['Demolition Needed'] = '',
        d['Environmental Cleanup Needed'] = '',
        d['Market Condition'] = MVAClassifcation.objects.filter(geometry__contains=prop.centroid_geometry).first(),
        d['Potential Use'] = '',
        d['Property Condition'] = '',
        d['Property of Interest'] = '',
        d['Quiet Title'] = 'Y' if prop.quiet_title_complete else 'N',
        d['Rehab Candidate'] = '',
        d['Target Disposition'] = '',
        d['Trash Removal '] = '',
        d['Custom.BEP Mortgage Expiration Date'] = '',
        d['Custom.BLC Number'] = blc_id,
        d['Custom.CDC'] = '',
        d['Custom.Grant Program'] = 'BEP' if prop.hhf_demolition else '',
        d['Custom.Mow List'] = 'Y',
        d['Custom.Mow List Change Date'] = timezone.now(),
        d['Custom.Mowing List Notes'] = '',
        d['Custom.Mowing Type'] = 'Mow',
        d['Custom.Sales Program'] = sales_program,

        header_text_fields = [u'Parcel Number']
        header_date_fields = [u'Custom.Mow List Change Date', u'Sold Date', u'Acquisition Date']
        workbook = xlsxwriter.Workbook('property-import-{0}.xlsx'.format(prop.parcel,))
        workbook.remove_timezone = True
        worksheet = workbook.add_worksheet('PropertyDescription')
        text_format = workbook.add_format({'num_format': '@'})
        date_format = workbook.add_format({'num_format': 'MM/DD/YY'})

        idx = 0
        for k, v in d.items():
            worksheet.write(0, idx, k)
            idx += 1

        idx = 0
        for k, v in d.items():
            if k in header_text_fields:
                worksheet.write(1, idx, v[0], text_format) # write parcel numbers as text
            elif k in header_date_fields:
               worksheet.write(1, idx, v[0], date_format)
            else:
                worksheet.write(1, idx, v[0] )
            idx += 1


        workbook.close()
        FILENAME = 'property-import-{0}.xlsx'.format(prop.parcel,)
        wrapper = FileWrapper(open(FILENAME,'rb'))
        content_type = mimetypes.MimeTypes().guess_type(FILENAME)[0]
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(FILENAME)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(FILENAME))
        return response
