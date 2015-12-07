import factory
import random

from django.utils import timezone
from django.contrib.gis.geos import Point

from geokey.users.tests.model_factories import UserF
from geokey.projects.tests.model_factories import ProjectF
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


class AirQualityProjectF(factory.django.DjangoModelFactory):

    status = 'active'
    creator = factory.SubFactory(UserF)
    project = factory.SubFactory(ProjectF)

    class Meta:
        model = AirQualityProject


class AirQualityCategoryF(factory.django.DjangoModelFactory):

    type = factory.LazyAttribute(lambda s: random.choice(
        dict(AirQualityCategory.TYPES).keys())
    )
    category = factory.SubFactory(CategoryFactory)
    project = factory.SubFactory(AirQualityProjectF)

    class Meta:
        model = AirQualityCategory


class AirQualityFieldF(factory.django.DjangoModelFactory):

    type = factory.LazyAttribute(lambda s: random.choice(
        dict(AirQualityField.TYPES).keys())
    )
    field = factory.SubFactory(TextFieldFactory)
    category = factory.SubFactory(AirQualityCategoryF)

    class Meta:
        model = AirQualityField


class AirQualityLocationF(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: 'Location %d' % n)
    geometry = Point(-1.5126800537109375, 51.062975588514966)
    creator = factory.SubFactory(UserF)
    created = timezone.now()
    properties = {}

    class Meta:
        model = AirQualityLocation


class AirQualityMeasurementF(factory.django.DjangoModelFactory):

    location = factory.SubFactory(AirQualityLocationF)
    barcode = 123456
    creator = factory.SubFactory(UserF)
    started = timezone.now()
    finished = None
    properties = {}

    class Meta:
        model = AirQualityMeasurement
