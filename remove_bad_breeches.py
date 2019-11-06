import sys, os, django
#sys.path.append("/path/to/store") #here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blight_fight.settings")
django.setup()

from property_inventory.models import Property
from applications.models import Application
from project_agreement_management.models import Enforcement, BreechType, BreechStatus

overdue_breech = BreechType.objects.get(name='Past two year deadline')

enfs = Enforcement.objects.filter(Application__application_type__in=[Application.SIDELOT, Application.VACANT_LOT, Application.FDL])

bses = BreechStatus.objects.filter(breech=overdue_breech).filter(enforcement__in=enfs)
for bs in bses:
    print(bs.enforcement)
    bs.status=BreechStatus.CLOSED
    bs.save()
