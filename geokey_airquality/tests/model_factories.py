import factory
import random

from django.utils import timezone
from django.contrib.gis.geos import Point

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import (
    CategoryFactory,
    TextFieldFactory
)

from geokey_airquality.models import (
    AirQualityProject,
    AirQualityCategory,
    AirQualityField,
    AirQualityLocation,
    AirQualityMeasurement
)


class AirQualityProjectFactory(factory.django.DjangoModelFactory):

    status = 'active'
    creator = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)

    class Meta:
        model = AirQualityProject


class AirQualityCategoryFactory(factory.django.DjangoModelFactory):

    type = factory.LazyAttribute(lambda s: random.choice(
        dict(AirQualityCategory.TYPES).keys())
    )
    category = factory.SubFactory(CategoryFactory)
    project = factory.SubFactory(AirQualityProjectFactory)

    class Meta:
        model = AirQualityCategory


class AirQualityFieldFactory(factory.django.DjangoModelFactory):

    type = factory.LazyAttribute(lambda s: random.choice(
        dict(AirQualityField.TYPES).keys())
    )
    field = factory.SubFactory(TextFieldFactory)
    category = factory.SubFactory(AirQualityCategoryFactory)

    class Meta:
        model = AirQualityField


class AirQualityLocationFactory(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: 'Location %d' % n)
    geometry = Point(-1.5126800537109375, 51.062975588514966)
    creator = factory.SubFactory(UserFactory)
    created = timezone.now()
    properties = {}

    class Meta:
        model = AirQualityLocation


class AirQualityMeasurementFactory(factory.django.DjangoModelFactory):

    location = factory.SubFactory(AirQualityLocationFactory)
    barcode = '123456'
    creator = factory.SubFactory(UserFactory)
    started = timezone.now()
    finished = None
    properties = {}

    class Meta:
        model = AirQualityMeasurement
