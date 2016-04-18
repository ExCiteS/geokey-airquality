"""All models for the extension."""

from django.conf import settings
from django.core import mail
from django.dispatch import receiver
from django.db import models
from django.template import Context
from django.template.loader import get_template
from django.contrib.gis.db import models as gis

from django_pgjson.fields import JsonBField

from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

from geokey.projects.models import Project
from geokey.categories.models import Category, TextField


def email_user(template, subject, receiver, action,
               project_name=None, category_name=None, field_name=None):
    """Email user."""
    message = get_template(
        template
    ).render(Context({
        'receiver': receiver.display_name,
        'project_name': project_name,
        'category_name': category_name,
        'field_name': field_name,
        'action': action
    }))

    message = mail.EmailMessage(
        'Air Quality: %s' % subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [receiver.email]
    )

    connection = mail.get_connection()
    connection.open()
    connection.send_messages([message])
    connection.close()


class AirQualityProject(StatusModel, TimeStampedModel):
    """Store a single Air Quality project."""

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
    Quality, when original project is marked as deleted or inactive.
    """
    if instance.status != 'active':
        try:
            project = AirQualityProject.objects.get(project=instance)
            user = project.creator
            project.delete()

            if instance.status == 'inactive':
                action = 'made inactive'
            else:
                action = 'deleted'

            email_user(
                'emails/project_not_active.txt',
                'Project %s %s' % (instance.name, action),
                user,
                action,
                instance.name
            )
        except AirQualityProject.DoesNotExist:
            pass


@receiver(models.signals.pre_delete, sender=Project)
def pre_delete_project(sender, instance, **kwargs):
    """
    Receiver that is called after a project is deleted. Removes it from Air
    Quality.
    """

    try:
        project = AirQualityProject.objects.get(project=instance)
        user = project.creator
        project.delete()

        action = 'deleted'

        email_user(
            'emails/project_not_active.txt',
            'Project %s %s' % (instance.name, action),
            user,
            action,
            instance.name
        )
    except AirQualityProject.DoesNotExist:
        pass


class AirQualityCategory(models.Model):
    """Store a single Air Quality category."""

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


@receiver(models.signals.post_save, sender=Category)
def post_save_category(sender, instance, **kwargs):
    """
    Receiver that is called after a category is saved. Makes associated Air
    Quality project inactive, if category is no longer active.
    """
    if instance.status != 'active':
        try:
            category = AirQualityCategory.objects.get(category=instance)
            category.project.status = 'inactive'
            category.project.save()
            user = category.project.creator
            category.delete()

            action = 'made inactive'

            email_user(
                'emails/category_not_active.txt',
                'Category %s %s' % (instance.name, action),
                user,
                action,
                instance.project.name,
                instance.name
            )
        except AirQualityCategory.DoesNotExist:
            pass


@receiver(models.signals.pre_delete, sender=Category)
def pre_delete_category(sender, instance, **kwargs):
    """
    Receiver that is called after a category is deleted. Makes associated Air
    Quality project inactive.
    """

    try:
        category = AirQualityCategory.objects.get(category=instance)
        category.project.status = 'inactive'
        category.project.save()
        user = category.project.creator
        category.delete()

        action = 'deleted'

        email_user(
            'emails/category_not_active.txt',
            'Category %s %s' % (instance.name, action),
            user,
            action,
            instance.project.name,
            instance.name
        )
    except AirQualityCategory.DoesNotExist:
        pass


class AirQualityField(models.Model):
    """Store a single Air Quality field."""

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


@receiver(models.signals.post_save, sender=TextField)
def post_save_field(sender, instance, **kwargs):
    """
    Receiver that is called after a text field is saved. Makes associated Air
    Quality project inactive, if field is no longer active.
    """
    if instance.status != 'active':
        try:
            field = AirQualityField.objects.get(field=instance)
            field.category.project.status = 'inactive'
            field.category.project.save()
            user = field.category.project.creator
            field.delete()

            action = 'made inactive'

            email_user(
                'emails/field_not_active.txt',
                'Field %s %s' % (instance.name, action),
                user,
                action,
                instance.category.project.name,
                instance.category.name,
                instance.name
            )
        except AirQualityField.DoesNotExist:
            pass


@receiver(models.signals.pre_delete, sender=TextField)
def pre_delete_field(sender, instance, **kwargs):
    """
    Receiver that is called after a text field is deleted. Makes associated Air
    Quality project inactive.
    """

    try:
        field = AirQualityField.objects.get(field=instance)
        field.category.project.status = 'inactive'
        field.category.project.save()
        user = field.category.project.creator
        field.delete()

        action = 'deleted'

        email_user(
            'emails/field_not_active.txt',
            'Field %s %s' % (instance.name, action),
            user,
            action,
            instance.category.project.name,
            instance.category.name,
            instance.name
        )
    except AirQualityField.DoesNotExist:
        pass


class AirQualityLocation(models.Model):
    """Store a single Air Quality location."""

    name = models.CharField(max_length=100)
    geometry = gis.GeometryField(geography=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=False)
    properties = JsonBField(default={})


class AirQualityMeasurement(models.Model):
    """Store a single Air Quality measurement."""

    location = models.ForeignKey(
        'AirQualityLocation',
        related_name='measurements'
    )
    barcode = models.CharField(max_length=25)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    started = models.DateTimeField(auto_now_add=False)
    finished = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    properties = JsonBField(default={})
