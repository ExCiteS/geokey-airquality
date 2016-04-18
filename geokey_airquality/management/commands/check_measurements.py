"""`check_measurements` command."""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta
from pytz import utc

from django.conf import settings
from django.core import mail
from django.utils import timezone
from django.core.management.base import NoArgsCommand
from django.template import Context
from django.template.loader import get_template

from geokey.users.models import User

from geokey_airquality.models import AirQualityMeasurement


class Command(NoArgsCommand):
    """A command to check for expiring/expired measurements."""

    def check_measurements(self):
        """
        Check all measurements that are due to expire or already expired.

        Inform creators of those measurements by sending an email with all the
        required information.
        """
        some_time_ago = timezone.now() - timedelta(28)
        some_time_ago = datetime(
            some_time_ago.year,
            some_time_ago.month,
            some_time_ago.day,
            0, 0, 0
        ).replace(tzinfo=utc)
        some_time_ago = some_time_ago + timedelta(1)  # checking a day after

        messages = []
        for user in User.objects.exclude(display_name='AnonymousUser'):
            measurements = AirQualityMeasurement.objects.filter(
                creator=user,
                started__lt=some_time_ago,
                finished__isnull=True
            ).select_related('location')

            due_to_expire = measurements.filter(
                started__gte=some_time_ago - timedelta(1)  # on that day
            )
            already_expired = measurements.filter(
                started__lt=some_time_ago - timedelta(3),  # more than 30 days
                started__gte=some_time_ago - timedelta(4)  # but only once
            )

            if len(due_to_expire) > 0 or len(already_expired) > 0:
                message = get_template(
                    'emails/measurements_to_be_finished.txt'
                ).render(Context({
                    'receiver': user.display_name,
                    'due_to_expire': due_to_expire,
                    'already_expired': already_expired
                }))

                messages.append(mail.EmailMessage(
                    'Air Quality: Measurements to be finished',
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                ))

        if len(messages) > 0:
            connection = mail.get_connection()
            connection.open()
            connection.send_messages(messages)
            connection.close()

    def handle(self, *args, **options):
        """Execute the code when the command is run."""
        self.check_measurements()
