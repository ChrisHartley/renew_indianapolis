import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blight_fight.settings")

import django
django.setup()

from applications.models import Application, MeetingLink, Meeting
from property_inventory.models import Property
from user_files.models import UploadedFile
from django.core.files.base import ContentFile
#parcels = ['1014357','1045714','1053819','1053818','1077379','1007209','1058628','1059843','1025250','1033374','1046931','1076327','1071972','1003893','1072980','1023819','1048095','1035011']
#parcels = ['1032075','1050963','1033774','1073948']
parcels = ['8046303',]
template_app = Application.objects.get(id=8236)
org_app =  Application.objects.get(id=8236)
print(template_app)
for parcel in parcels:
    app = org_app
    prop = Property.objects.get(parcel=parcel)
    app.id = None
    app.Property = prop
    app.price_at_time_of_submission = prop.price
    app.save()
    mls = MeetingLink.objects.filter(application=template_app).order_by('meeting__meeting_date')
    print(mls)
    for ml in mls:
        ml.application = app
        ml.id = None
        ml.save()
    files = UploadedFile.objects.filter(application=template_app)
    for f in files:
        f2 = UploadedFile(
            user=f.user,
            organization=f.organization,
            application=app,
            file_purpose=f.file_purpose,
            send_with_neighborhood_notification=f.send_with_neighborhood_notification,

        )
        fname = f.supporting_document.name.split('/')[-1]
        f2.supporting_document.save(fname, ContentFile(f.supporting_document), save=True)
