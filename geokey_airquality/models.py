from django.conf import settings
from django.dispatch import receiver
from django.db import models
from django.contrib.gis.db import models as gis

from django_pgjson.fields import JsonBField

from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

from geokey.projects.models import Project


class AirQualityProject(StatusModel, TimeStampedModel):

    """
    Air Quality Project - relation to GeoKey project.
    """

    STATUS = Choices('active', 'inactive')

    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey(
        'projects.Project',
        related_name='airquality'
    )


@receiver(models.signals.post_save, sender=Project)
def post_save_project(sender, instance, **kwargs):
    """
    Receiver that is called after a project is saved. Removes it from Air
    Quality, when original project is deleted.
    """
    if instance.status == 'deleted':
        try:
            project = AirQualityProject.objects.get(project=instance)
            project.delete()
        except AirQualityProject.DoesNotExist:
            pass


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
    type = models.CharField(max_length=25, null=False, choices=TYPES)

    category = models.ForeignKey(
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
        (u'results', u'01. Results'),
        (u'date_out', u'02. Date out'),
        (u'time_out', u'03. Time out'),
        (u'date_collected', u'04. Date collected'),
        (u'time_collected', u'05. Time collected'),
        (u'exposure_min', u'06. Exposure time (min)'),
        (u'distance_from_road', u'07. Distance from the road'),
        (u'height', u'08. Height from ground'),
        (u'site_characteristics', u'09. Site characteristics'),
        (u'additional_details', u'10. Additional details')
    )
    type = models.CharField(max_length=50, null=False, choices=TYPES)

    field = models.ForeignKey(
        'categories.Field',
        related_name='airquality'
    )
    category = models.ForeignKey(
        'AirQualityCategory',
        related_name='fields'
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
