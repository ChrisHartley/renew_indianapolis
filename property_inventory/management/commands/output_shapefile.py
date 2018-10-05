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
        try:

            check_call(['pgsql2shp',  '-u', user, '-P', pw, '-f', '{0}/renew_inventory.shp'.format(tmp_dir,), db, query])
        except CalledProcessError:
            raise CalledProcessError
            # sigh I don't know, it just seemed like we shoudl acknowledge the error, even if we want to freak out about it

        #check_call(['zip', '-D', '/tmp/renew_inventory.zip', '/tmp/renew_inventory.dbf','/tmp/renew_inventory.prj','/tmp/renew_inventory.shp', '/tmp/renew_inventory.shx', '/tmp/renew_inventory.cpg'])
        make_archive('static/renew_inventory', 'zip', tmp_dir)
        rmtree(tmp_dir)
