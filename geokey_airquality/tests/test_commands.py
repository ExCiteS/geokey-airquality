from datetime import timedelta

from django.test import TestCase
from django.core import mail
from django.utils import timezone

from geokey.users.tests.model_factories import UserFactory

from geokey_airquality.management.commands.check_measurements import Command
from geokey_airquality.tests.model_factories import (
    AirQualityLocationFactory,
    AirQualityMeasurementFactory
)


class CheckMeasurementsTest(TestCase):

    def test_check_measurements(self):

        user_1 = UserFactory.create(**{'is_superuser': False})
        user_2 = UserFactory.create(**{'is_superuser': False})

        long_time_ago = timezone.now() - timedelta(60)

        location_1 = AirQualityLocationFactory.create(
            creator=user_1,
            created=long_time_ago
        )
        location_2 = AirQualityLocationFactory.create(
            creator=user_1,
            created=long_time_ago
        )
        location_3 = AirQualityLocationFactory.create(
            creator=user_2,
            created=long_time_ago
        )
        location_4 = AirQualityLocationFactory.create(
            creator=user_2,
            created=long_time_ago
        )

        AirQualityMeasurementFactory.create(
            creator=user_1,
            location=location_1,
            barcode='102701',
            started=timezone.now() - timedelta(26)
        )
        AirQualityMeasurementFactory.create(
            creator=user_1,
            location=location_1,
            barcode='102801',
            started=timezone.now() - timedelta(28)  # expiring in 3 days
        )
        AirQualityMeasurementFactory.create(
            creator=user_1,
            location=location_1,
            barcode='102801',
            started=timezone.now() - timedelta(29)  # expiring in 2 days
        )
        AirQualityMeasurementFactory.create(
            creator=user_1,
            location=location_1,
            barcode='102901',
            started=timezone.now() - timedelta(31)  # already expired
        )
        AirQualityMeasurementFactory.create(
            creator=user_1,
            location=location_2,
            barcode='102802',
            started=timezone.now() - timedelta(28)  # expiring in 3 days
        )
        AirQualityMeasurementFactory.create(
            creator=user_1,
            location=location_2,
            barcode='102802',
            started=timezone.now() - timedelta(30)  # expiring in 1 day
        )
        AirQualityMeasurementFactory.create(
            creator=user_1,
            location=location_2,
            barcode='102902',
            started=timezone.now() - timedelta(31)  # already expired
        )
        AirQualityMeasurementFactory.create(
            creator=user_1,
            location=location_2,
            barcode='103002',
            started=timezone.now() - timedelta(32)  # already expired
        )
        AirQualityMeasurementFactory.create(
            creator=user_2,
            location=location_3,
            barcode='200403',
            started=timezone.now() - timedelta(4)
        )
        AirQualityMeasurementFactory.create(
            creator=user_2,
            location=location_4,
            barcode='201104',
            started=timezone.now() - timedelta(11)
        )

        command = Command()

        command.check_measurements()
        self.assertEquals(len(mail.outbox), 1)
