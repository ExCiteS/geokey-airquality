import factory

from django.utils import timezone
from django.contrib.gis.geos import Point

from geokey.users.tests.model_factories import UserF

from geokey_airquality.models import AirQualityLocation, AirQualityMeasurement


class AirQualityLocationF(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: 'Location %d' % n)
    geometry = Point(-0.508, 51.682)
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
