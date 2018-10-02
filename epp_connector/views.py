# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import mimetypes
import os
from django.http import HttpResponse
from wsgiref.util import FileWrapper

import xlsxwriter
from os.path import getmtime
import datetime
from ePP_simple_api import ePPHelper

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
        print('File stale, re-fetching')

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
                print(record['currentStatus'])
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

# Create your views here.
