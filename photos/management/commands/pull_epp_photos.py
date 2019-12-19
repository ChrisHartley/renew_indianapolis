from django.core.management.base import BaseCommand, CommandError
from epp_connector.ePP_simple_api import ePPHelper
from property_inventory.models import Property
from photos.models import photo
from tempfile import NamedTemporaryFile
from django.core.files import File
from django.utils.text import get_valid_filename
from os.path import splitext, basename
import imghdr

class Command(BaseCommand):
    help = 'Check ePropertyPlus for new property photos and add them to Blight Fight'


    def handle(self, *args, **options):
        epp = ePPHelper(sandbox=False, debug=False)
        for prop in Property.objects.exclude(status__contains='Sold'):
            parcel = prop.parcel
            json_query = '{"criterias":[{"name":"parcelNumber","value":"%s","operator":"EQUALS"}]}' % parcel
            props = epp.get_property_search(json_query=json_query)
            p = Property.objects.get(parcel=parcel)
            phs = photo.objects.filter(prop=p)
            ph_names = []
            for ph in phs:
                root, ext = splitext(basename(ph.image.name))
                ph_names.append(root)
            for row in props['rows']:
                image_results = epp.get_image_list(row['id'])
                for image in image_results['rows']:
                    fname = get_valid_filename(image['filename'])
                    fname_root, fname_ext = splitext(fname)
                    if fname_root not in ph_names:
                        self.stdout.write("Need to fetch this image: {}".format(fname,))
                        with NamedTemporaryFile() as f:
                            f.write(epp.get_image(image['id']))
                            f.seek(0)
                            determined_ext = imghdr.what(f.name)
                            x = photo(prop=p, main_photo=False)
                            x.image.save('{}.{}'.format(fname_root, determined_ext), File(f) )
