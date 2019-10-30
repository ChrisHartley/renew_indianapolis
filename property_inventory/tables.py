import django_tables2 as tables
from property_inventory.models import Property

class SoldPropertyStatusTable2(tables.Table):
    address = tables.Column()
    parcel = tables.Column()
    sale_date = tables.Column()
    buyer = tables.Column()
    amount = tables.Column()
    class Meta:
        attrs = {"class": "paleblue"}


class SoldPropertyStatusTable(tables.Table):
    real_status = tables.Column(empty_values=())
    real_buyer = tables.Column(empty_values=())

    def render_real_buyer(self, value, record):
        if record.take_back.all().count() > 0:
            return record.take_back.all()[0].owner
        else:
            return record.applicant


    def render_real_status(self, value, record):
        if record.take_back.all().count() > 0:
            return record.take_back.all()[0].original_sale_date.strftime('%x')
        else:
            return record.status[5:16]
        #  return record



    class Meta:
        model = Property
        attrs = {"class": "paleblue"}
        fields = ("parcel", "streetAddress", "zipcode",
                  "structureType", "price", "applicant", "take_back__owner", "status", )

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
