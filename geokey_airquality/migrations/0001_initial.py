# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields
import model_utils.fields
import django_pgjson.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_remove_admins_contact'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AirQualityMeasurement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('properties', django_pgjson.fields.JsonBField(default={})),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AirQualityPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326, geography=True)),
                ('properties', django_pgjson.fields.JsonBField(default={})),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('measurements', models.ManyToManyField(related_name='points', to='geokey_airquality.AirQualityMeasurement')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AirQualityProject',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('project', models.OneToOneField(related_name='airquality', primary_key=True, serialize=False, to='projects.Project')),
                ('points', models.ManyToManyField(related_name='projects', to='geokey_airquality.AirQualityPoint')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
