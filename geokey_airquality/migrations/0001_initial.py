# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_remove_admins_contact'),
        ('categories', '0013_auto_20150130_1440'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AirQualityCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=25, choices=[('1', '<40'), ('2', '40-60'), ('3', '60-80'), ('4', '80-100'), ('5', '100+')])),
                ('category', models.ForeignKey(related_name='airquality', to='categories.Category')),
            ],
        ),
        migrations.CreateModel(
            name='AirQualityField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=25, choices=[('results', 'Results'), ('date_out', 'Date out'), ('time_out', 'Time out'), ('date_collected', 'Date collected'), ('time_collected', 'Time collected'), ('exposure_min', 'Exposure time (min)'), ('distance_from_road', 'Distance from the road'), ('height', 'Height from ground'), ('site_characteristics', 'Site characteristics'), ('additional_details', 'Additional details')])),
                ('category', models.ForeignKey(related_name='fields', to='geokey_airquality.AirQualityCategory')),
                ('field', models.ForeignKey(related_name='airquality', to='categories.Field')),
            ],
        ),
        migrations.CreateModel(
            name='AirQualityLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326, geography=True)),
                ('created', models.DateTimeField()),
                ('properties', django_pgjson.fields.JsonBField(default={})),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AirQualityMeasurement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('barcode', models.CharField(max_length=25)),
                ('started', models.DateTimeField()),
                ('finished', models.DateTimeField(null=True, blank=True)),
                ('properties', django_pgjson.fields.JsonBField(default={})),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(related_name='measurements', to='geokey_airquality.AirQualityLocation')),
            ],
        ),
        migrations.CreateModel(
            name='AirQualityProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.ForeignKey(related_name='airquality', to='projects.Project')),
            ],
        ),
        migrations.AddField(
            model_name='airqualitycategory',
            name='project',
            field=models.ForeignKey(related_name='categories', to='geokey_airquality.AirQualityProject'),
        ),
    ]
