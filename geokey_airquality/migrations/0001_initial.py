# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_remove_admins_contact'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
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
                ('project', models.OneToOneField(related_name='airquality', primary_key=True, serialize=False, to='projects.Project')),
            ],
        ),
    ]
