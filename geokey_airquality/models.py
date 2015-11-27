from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gis

from django_pgjson.fields import JsonBField


class AirQualityProject(models.Model):

    project = models.OneToOneField(
        'projects.Project',
        primary_key=True,
        related_name='airquality'
    )


class AirQualityLocation(models.Model):

    name = models.CharField(max_length=100)
    geometry = gis.GeometryField(geography=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=False)
    properties = JsonBField(default={})


class AirQualityMeasurement(models.Model):

    location = models.ForeignKey('AirQualityLocation', related_name='measurements')
    barcode = models.CharField(max_length=25)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    started = models.DateTimeField(auto_now_add=False)
    finished = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    properties = JsonBField(default={})
