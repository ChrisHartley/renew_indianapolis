# -*- coding: utf-8 -*-


from django.db import models
from property_inventory.models import census_tract
from django.utils.encoding import python_2_unicode_compatible


# Model saves census tract level analysis of sales disclosures
# for the past 12 months. Should be updated monthly.
"""
insert into market_activity_tract_sdf_summary(
created,
census_tract_id,
bottom_10_percent_per_sq_ft,
top_90_percent_per_sq_ft,
median_per_sq_ft,
average_per_sq_ft,
minimum_per_sq_ft,
maximum_per_sq_ft,

bottom_10_percent,
top_90_percent,
median,
average,
minimum,
maximum,
number_qualifying_sales,
with_improvements
)
(
select now(), ct.id,
quantile(s.sales_price/st_area(p.geom),0.1) as "bottom 10% price per sq ft",
quantile(s.sales_price/st_area(p.geom),0.9) as "top 90% price per sq ft",
quantile(s.sales_price/st_area(p.geom),0.5) as "median price per sq ft",
avg(s.sales_price/st_area(p.geom)) as "ave sales price per sq ft",
min(s.sales_price/st_area(p.geom)) as "min sales price per sq ft",
max(s.sales_price/st_area(p.geom)) as "max sales price per sq ft",
quantile(s.sales_price,0.1) as "bottom 10%",
quantile(s.sales_price,0.9) as "top 90%",
quantile(s.sales_price,0.5) as "median",
round(avg(s.sales_price),2) as "avg sales price",
min(s.sales_price) as "min sales price",
max(s.sales_price) as "max sales price",
count(s.*) as "num qualifying sales",
False
from property_inventory_census_tract ct
inner join parcels p on st_within(p.geom, st_transform(ct.geometry, 2965))
inner join sales_disclosure_auto s on s.parcel = p.state_parcel
where
s.property_class_code like '5%'
and s.b3_vacant_land = True
and s.conveyance_date >= (CURRENT_DATE - interval '12 months')
and s.valid_for_trending = True
and s.num_parcels = 1 -- exclude bulk sales
group by ct.id
)
"""

@python_2_unicode_compatible
class tract_sdf_summary(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    census_tract = models.ForeignKey(census_tract, related_name='sdf_summary', on_delete=models.CASCADE)
    bottom_10_percent = models.DecimalField(max_digits=15, decimal_places=2)
    top_90_percent = models.DecimalField(max_digits=15, decimal_places=2)
    median = models.DecimalField(max_digits=15, decimal_places=2)
    average = models.DecimalField(max_digits=15, decimal_places=2)
    minimum = models.DecimalField(max_digits=15, decimal_places=2)
    maximum = models.DecimalField(max_digits=15, decimal_places=2)

    bottom_10_percent_per_sq_ft = models.DecimalField(max_digits=15, decimal_places=3)
    top_90_percent_per_sq_ft = models.DecimalField(max_digits=15, decimal_places=3)
    median_per_sq_ft = models.DecimalField(max_digits=15, decimal_places=3)
    average_per_sq_ft = models.DecimalField(max_digits=15, decimal_places=3)
    minimum_per_sq_ft = models.DecimalField(max_digits=15, decimal_places=3)
    maximum_per_sq_ft = models.DecimalField(max_digits=15, decimal_places=3)


    number_qualifying_sales = models.IntegerField()


    LOT = False
    IMPROVEMENTS = True

    IMPROV_CHOICES = (
        (LOT, 'Vacant lot'),
        (IMPROVEMENTS, 'Structure'),
    )

    with_improvements = models.BooleanField(choices=IMPROV_CHOICES)

    class Meta:
        verbose_name = 'Census Tract Sales Summary'
        verbose_name_plural = 'Census Tract Sales Summaries'

    def __str__(self):              # __str__ on Python 2
        return '{} - {} - {}'.format(self.census_tract, self.created, self.get_with_improvements_display())
