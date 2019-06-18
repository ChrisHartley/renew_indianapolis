import django_tables2 as tables
from property_inventory.models import Property


class PropertyStatusTable(tables.Table):

    class Meta:
        model = Property
        attrs = {"class": "paleblue"}
        fields = ("parcel", "streetAddress", "zipcode",
                  "structureType", "price", "applicant", "status", )

class reviewPendingStatusTable(tables.Table):

    class Meta:
        model = Property
        attrs = {"class": "paleblue"}
        fields = ("parcel", "streetAddress", "zipcode",
                  "structureType",)

class PropertySearchTable(tables.Table):

    class Meta:
        model = Property
        attrs = {"class": "paleblue", "id": "myTable"}
        fields = ("parcel", "streetAddress", "zipcode", "structureType", "cdc", "zoning", "nsp",
                  "quiet_title_complete", "side_lot_eligible", "area", "status", "bep_demolition", "urban_garden", "price")
