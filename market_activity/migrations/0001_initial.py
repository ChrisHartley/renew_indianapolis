# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-18 17:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('property_inventory', '0029_census_tract'),
    ]

    operations = [
        migrations.CreateModel(
            name='tract_sdf_summary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('bottom_10_percent', models.DecimalField(decimal_places=2, max_digits=15)),
                ('top_90_percent', models.DecimalField(decimal_places=2, max_digits=15)),
                ('median', models.DecimalField(decimal_places=2, max_digits=15)),
                ('average', models.DecimalField(decimal_places=2, max_digits=15)),
                ('minimum', models.DecimalField(decimal_places=2, max_digits=15)),
                ('maximum', models.DecimalField(decimal_places=2, max_digits=15)),
                ('number_qualifying_sales', models.IntegerField()),
                ('with_improvements', models.BooleanField()),
                ('census_tract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='property_inventory.census_tract')),
            ],
        ),
    ]
