from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gis

from django_pgjson.fields import JsonBField


class AirQualityProject(models.Model):

    """
    Air Quality Project - relation to GeoKey project.
    """

    project = models.OneToOneField(
        'projects.Project',
        related_name='airquality'
    )


class AirQualityCategory(models.Model):

    """
    Air Quality Category - relation to GeoKey category. Can only be one of the
    possible types.
    """

    TYPES = (
        (u'1', u'<40'),
        (u'2', u'40-60'),
        (u'3', u'60-80'),
        (u'4', u'80-100'),
        (u'5', u'100+')
    )
    type = models.CharField(max_length=10, null=False, choices=TYPES)

    category = models.OneToOneField(
        'categories.Category',
        related_name='airquality'
    )
    project = models.ForeignKey(
        'AirQualityProject',
        related_name='categories'
    )


class AirQualityField(models.Model):

    """
    Air Quality Field - relation to GeoKey field. Can only be one of the
    possible types.
    """

    TYPES = (
        (u'results', u'Results'),
        (u'date_out', u'Date out'),
        (u'time_out', u'Time out'),
        (u'date_collected', u'Date collected'),
        (u'time_collected', u'Time collected'),
        (u'exposure_min', u'Exposure time (min)'),
        (u'distance_from_road', u'Distance from the road'),
        (u'height', u'Height from ground'),
        (u'site_characteristics', u'Site characteristics'),
        (u'additional_details', u'Additional details')
    )
    type = models.CharField(max_length=10, null=False, choices=TYPES)

    field = models.OneToOneField(
        'categories.Field',
        related_name='airquality'
    )
    category = models.ForeignKey(
        'AirQualityCategory',
        related_name='categories'
    )


class AirQualityLocation(models.Model):

    """
    Air Quality Location: holds a single point, to which many measurements can
    be related, also additional properties.
    """

    name = models.CharField(max_length=100)
    geometry = gis.GeometryField(geography=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=False)
    properties = JsonBField(default={})


class AirQualityMeasurement(models.Model):

    """
    Air Quality Measurement: holds information about when the measurement was
    started, finished, also additional properties.
    """

    location = models.ForeignKey(
        'AirQualityLocation',
        related_name='measurements'
    )
    barcode = models.CharField(max_length=25)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    started = models.DateTimeField(auto_now_add=False)
    finished = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    properties = JsonBField(default={})
