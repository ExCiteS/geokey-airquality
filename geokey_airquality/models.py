from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gis

from django_pgjson.fields import JsonBField
from model_utils.models import TimeStampedModel


class AirQualityProject(TimeStampedModel):

    project = models.OneToOneField(
        'projects.Project',
        primary_key=True,
        related_name='airquality'
    )
    points = models.ManyToManyField(
        'AirQualityPoint',
        related_name='projects'
    )


class AirQualityPoint(TimeStampedModel):

    geometry = gis.GeometryField(geography=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    properties = JsonBField(default={})
    measurements = models.ManyToManyField(
        'AirQualityMeasurement',
        related_name='points'
    )


class AirQualityMeasurement(TimeStampedModel):

    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    properties = JsonBField(default={})
