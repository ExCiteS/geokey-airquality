# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models

import django.utils.timezone
import django.contrib.gis.db.models.fields

import django_pgjson.fields
import model_utils.fields


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
                ('type', models.CharField(max_length=50, choices=[('results', '01. Results'), ('date_out', '02. Date out'), ('time_out', '03. Time out'), ('date_collected', '04. Date collected'), ('time_collected', '05. Time collected'), ('exposure_min', '06. Exposure time (min)'), ('distance_from_road', '07. Distance from the road'), ('height', '08. Height from ground'), ('site_characteristics', '09. Site characteristics'), ('additional_details', '10. Additional details')])),
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
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('status', model_utils.fields.StatusField(default=b'active', max_length=100, verbose_name='status', no_check_for_status=True, choices=[(b'active', b'active'), (b'inactive', b'inactive')])),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, verbose_name='status changed', monitor='status')),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(related_name='airquality', to='projects.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='airqualitycategory',
            name='project',
            field=models.ForeignKey(related_name='categories', to='geokey_airquality.AirQualityProject'),
        ),
    ]
