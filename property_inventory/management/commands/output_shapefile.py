from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from subprocess import check_call, CalledProcessError
from shutil import make_archive, rmtree
from tempfile import mkdtemp

class Command(BaseCommand):
    help = 'Create shapefile of active property inventory'


    def handle(self, *args, **options):
        query = 'select p.parcel, p."streetAddress", z.name, p."structureType", p.status, p.price, p.applicant, cdc.name as cdc, n.name as neighborhood, quiet_title_complete, hhf_demolition, sidelot_eligible, vacant_lot_eligible, homestead_only, renew_owned, acquisition_date, p.geometry from property_inventory_property p left join property_inventory_neighborhood n on p.neighborhood_id = n.id left join property_inventory_cdc cdc on cdc.id = p.cdc_id left join property_inventory_zipcode z on z.id = p.zipcode_id left join property_inventory_zoning zone on zone.id = p.zone_id left join property_inventory_census_tract ct on ct.id = p.census_tract_id where p.is_active = True'
        db = settings.DATABASES['default']['NAME']
        user = settings.DATABASES['default']['USER']
        pw = settings.DATABASES['default']['PASSWORD']
        tmp_dir = mkdtemp()
        check_call(['pgsql2shp',  '-u', user, '-P', pw, '-f', '{0}/renew_inventory.shp'.format(tmp_dir,), db, query])

        make_archive('static/renew_inventory', 'zip', tmp_dir)
        rmtree(tmp_dir)
