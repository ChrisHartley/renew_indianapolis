# -*- coding: utf-8 -*-


from django.test import TestCase
from django.contrib.auth import get_user_model
from .forms import CommIndApplicationForm
from .models import Property
from django.utils import timezone
from django.contrib.gis.geos import GEOSGeometry

class AAPropertyModelTest(TestCase):
    def setUp(self):
        geom_wkt="MULTIPOLYGON(((-86.1537182676678 39.7691153433008,-86.1534844655753 39.7691088775751,-86.1527363528052 39.7690881836752,-86.1527376760509 39.7690536676549,-86.152757862556 39.7685276505405,-86.1527582106241 39.768518582194,-86.1542506886641 39.7685514977556,-86.154229916604 39.7690865835228,-86.15422825501 39.7691294470766,-86.1542273111364 39.7691294212607,-86.1538114498664 39.7691179200849,-86.1537182676678 39.7691153433008)))"
        meadows = Property.objects.create(
            parcel = '1097671',
            geometry = GEOSGeometry(geom_wkt, srid=4326),
            street_address = '202 E MARKET ST',
            property_name = 'The City Market and the Platform',
            status = Property.AVAILABLE_STATUS,
            status_date = timezone.now(),
            price = 5000000.00,
            published = True,
            parcel_size = GEOSGeometry(geom_wkt, srid=4326).transform(2965, clone=True).area,
            zoning = 'CS',
            environmental_information = 'Unknown',
            has_improvement = True,
            building_size = 40000,
            location_notes = 'North of the City-County Building',
            property_notes = 'Includes market, gym and co-working space.',
        )

    def test_property_is_published(self):
        meadows = Property.objects.get(parcel='1097671')
        self.assertTrue(meadows.published)


    def test_property_geometry_area(self):
        meadows = Property.objects.get(parcel='1097671')
        self.assertTrue(meadows.parcel_size>1)

class CommIndApplicationFormTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            'zoidberg'
        )


    def test_init(self):
        CommIndApplicationForm(
            Property=Property.objects.get(parcel='1097671'),
            user = self.user,
        )

    def test_init_without_entry(self):
        with self.assertRaises(KeyError):
            CommIndApplicationForm()
