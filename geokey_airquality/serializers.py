"""All serializers for the extension."""

import json

from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from rest_framework.serializers import BaseSerializer

from geokey_airquality.models import AirQualityLocation, AirQualityMeasurement


class LocationSerializer(BaseSerializer):
    """
    Serialiser for geokey_airquality.models.AirQualityLocation.
    """

    def is_valid(self, raise_exception=False):
        """
        Checks if location is valid.

        Parameter
        ---------
        raise_exception : Boolean
            Indicates if an exeption should be raised if the data is invalid.
            If set to false, the method will return False rather than raising
            an exception.

        Returns
        -------
        Boolean
            Indicating if data is valid.

        Raises
        ------
        ValidationError
            If data is invalid. Exception is raised only when raise_exception
            is set to True.
        """

        self._errors = {}
        self._validated_data = {}

        # Validate name
        name = self.initial_data.get('name')

        try:
            if name is not None:
                self._validated_data['name'] = name
            else:
                raise ValidationError('Name must be specified.')
        except ValidationError, error:
            self._errors['name'] = error

        # Validate geometry
        geometry = self.initial_data.get('geometry')

        try:
            if geometry.get('type') == 'Point':
                coordinates = geometry.get('coordinates')

                if coordinates is not None:
                    x = coordinates[0]
                    y = coordinates[1]

                    if x is not None and y is not None:
                        self._validated_data['geometry'] = Point(x, y)
                    else:
                        raise ValidationError('Coordinates are incorrect.')
                else:
                    raise ValidationError('Coordinates are not set.')
            else:
                raise ValidationError('Only points can be used.')
        except ValidationError, error:
            self._errors['geometry'] = error

        # Validate properties
        properties = self.initial_data.get('properties') or {}
        self._validated_data['properties'] = {}

        if properties is not None:
            for key, value in properties.iteritems():
                if key in ['height', 'distance', 'characteristics']:
                    self._validated_data['properties'][key] = value

        # Raise the exception
        if self._errors and raise_exception:
            raise ValidationError(self._errors)

        return not bool(self._errors)

    def create(self, validated_data):
        """
        Creates a new location and returns the instance.

        Parameter
        ---------
        validated_data : dict
            Data after validation.

        Returns
        -------
        geokey_airquality.models.AirQualityLocation
            The instance created.
        """

        data = self.context.get('data')
        created = data.get('created')
        called = data.get('called')
        now = timezone.now()

        if created is None or called is None:
            created = now
        else:
            timedelta = parse_datetime(called) - parse_datetime(created)
            created = now - timedelta

        self.instance = AirQualityLocation.objects.create(
            name=validated_data.get('name'),
            geometry=validated_data.get('geometry'),
            creator=self.context.get('user'),
            created=created,
            properties=validated_data.get('properties')
        )

        return self.instance

    def update(self, instance, validated_data):
        """
        Updates an existing location and returns the instance.

        Parameter
        ---------
        instance : geokey_airquality.models.AirQualityLocation
            The instance to be updated.
        validated_data : dict
            Data after validation.

        Returns
        -------
        geokey_airquality.models.AirQualityLocation
            The instance updated.
        """

        instance.name = validated_data.get('name')
        instance.geometry = validated_data.get('geometry')
        instance.properties = validated_data.get('properties')
        instance.save()

        return instance

    def to_representation(self, object):
        """
        Returns the native representation of a location.

        Parameter
        ---------
        object : geokey_airquality.models.AirQualityLocation
            The instance that is serialised.

        Returns
        -------
        dict
            Native represenation of the location.
        """

        measurement_serializer = MeasurementSerializer(
            object.measurements.all(),
            many=True,
            context=self.context
        )

        return {
            'type': 'Feature',
            'geometry': json.loads(object.geometry.geojson),
            'id': object.id,
            'name': object.name,
            'created': str(object.created),
            'properties': object.properties,
            'measurements': measurement_serializer.data
        }


class MeasurementSerializer(BaseSerializer):
    """
    Serialiser for geokey_airquality.models.AirQualityMeasurement.
    """

    def is_valid(self, raise_exception=False):
        """
        Checks if measurement is valid.

        Parameter
        ---------
        raise_exception : Boolean
            Indicates if an exeption should be raised if the data is invalid.
            If set to false, the method will return False rather than raising
            an exception.

        Returns
        -------
        Boolean
            Indicating if data is valid.

        Raises
        ------
        ValidationError
            If data is invalid. Exception is raised only when raise_exception
            is set to True.
        """

        self._errors = {}
        self._validated_data = {}

        # Validate barcode
        barcode = self.initial_data.get('barcode')

        try:
            if barcode is not None:
                self._validated_data['barcode'] = barcode
            else:
                raise ValidationError('Barcode must be specified.')
        except ValidationError, error:
            self._errors['barcode'] = error

        # Validate properties
        properties = self.initial_data.get('properties') or {}
        self._validated_data['properties'] = {}

        if properties is not None:
            for key, value in properties.iteritems():
                if key in ['results', 'additional_details']:
                    self._validated_data['properties'][key] = value

        # Raise the exception
        if self._errors and raise_exception:
            raise ValidationError(self._errors)

        return not bool(self._errors)

    def create(self, validated_data):
        """
        Creates a new measurement and returns the instance.

        Parameter
        ---------
        validated_data : dict
            Data after validation.

        Returns
        -------
        geokey_airquality.models.AirQualityMeasurement
            The instance created.
        """

        data = self.context.get('data')
        started = data.get('started', None)
        finished = data.get('finished', None)
        called = data.get('called', None)
        now = timezone.now()

        if started is None or called is None:
            started = now
        else:
            timedelta = parse_datetime(called) - parse_datetime(started)
            started = now - timedelta

        if finished is not None:
            if called is None:
                finished = now
            else:
                timedelta = parse_datetime(called) - parse_datetime(finished)
                finished = now - timedelta

        self.instance = AirQualityMeasurement.objects.create(
            location=self.context.get('location'),
            barcode=validated_data.get('barcode'),
            creator=self.context.get('user'),
            started=started,
            finished=finished,
            properties=validated_data.get('properties')
        )

        return self.instance

    def update(self, instance, validated_data):
        """
        Updates an existing measurement and returns the instance.

        Parameter
        ---------
        instance : geokey_airquality.models.AirQualityMeasurement
            The instance to be updated.
        validated_data : dict
            Data after validation.

        Returns
        -------
        geokey_airquality.models.AirQualityMeasurement
            The instance updated.
        """

        data = self.context.get('data')
        finished = data.get('finished', None)
        called = data.get('called', None)
        now = timezone.now()

        if finished is not None:
            if called is None:
                finished = now
            else:
                timedelta = parse_datetime(called) - parse_datetime(finished)
                finished = now - timedelta

            instance.finished = finished

        instance.barcode = validated_data.get('barcode')
        instance.properties = validated_data.get('properties')
        instance.save()

        return instance

    def to_representation(self, object):
        """
        Returns the native representation of a measurement.

        Parameter
        ---------
        object : geokey_airquality.models.AirQualityMeasurement
            The instance that is serialised.

        Returns
        -------
        dict
            Native represenation of the measurement.
        """

        finished = object.finished or None

        if finished is not None:
            finished = str(finished)

        return {
            'id': object.id,
            'barcode': object.barcode,
            'started': str(object.started),
            'finished': finished,
            'properties': object.properties
        }
