import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'blight_fight.settings'
django.setup()

from photos.models import photo
from property_inventory.models import Property
from django.core.paginator import Paginator
import xlsxwriter
import zipfile
import datetime

last_import = datetime.datetime(2018, 1, 1)

#props = Property.objects.exclude(structureType__exact='Vacant Lot').order_by('parcel')
props = Property.objects.filter(acquisition_date__gte='2020-01-01').order_by('parcel')
#for p in props:
#    print p
header = ['Parcel Number', 'Sequence Number', 'Caption', 'Image Path', 'Published']
props_paginator = Paginator(props, 75)

for indx in props_paginator.page_range:
    props_split = props_paginator.page(indx)
    with zipfile.ZipFile('photos-{0}.zip'.format(indx,), 'w', zipfile.ZIP_DEFLATED) as myzip:

        workbook = xlsxwriter.Workbook('photos-{0}.xlsx'.format(indx,))
        worksheet = workbook.add_worksheet('PropertyImages')
        for i in range(len(header)):
            worksheet.write(0, i, header[i])
        i = 1
        #print indx
        for p in props_split:
            #print p
            seq = 1
            for photo in p.photo_set.filter(created__gte=last_import).order_by('-main_photo'):
                print(indx, p, photo)
                worksheet.write(i, 0, p.parcel)
                worksheet.write(i, 1, seq)
                worksheet.write(i, 2, photo.created.strftime('%Y-%m-%d %I:%M')) # Caption
                worksheet.write(i, 3, photo.image.path)
                worksheet.write(i, 4, 'Y') # published
                myzip.write(photo.image.path)
                seq = seq+1
                i=i+1
        workbook.close()
        myzip.write('photos-{0}.xlsx'.format(indx,))
