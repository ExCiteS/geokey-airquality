import json

from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from rest_framework.test import APIRequestFactory, force_authenticate

from geokey.users.tests.model_factories import UserF

from geokey_airquality import views
from geokey_airquality.models import (
    AirQualityLocation,
    AirQualityMeasurement
)
from geokey_airquality.tests.model_factories import (
    AirQualityLocationF,
    AirQualityMeasurementF
)


class AQLocationsAPIViewTest(TestCase):

    def setUp(self):

        self.creator = UserF.create()
        self.user = UserF.create()
        self.anonym = AnonymousUser()

        self.url = '/api/airquality/locations/'
        self.data = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [-0.134, 51.524]
            },
            'name': 'Test Location',
            'properties': {
                'distance': 2
            }
        }

        self.factory = APIRequestFactory()
        self.request_get = self.factory.get(self.url)
        self.request_post = self.factory.post(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        self.view = views.AQLocationsAPIView.as_view()

        self.location_1 = AirQualityLocationF.create(creator=self.creator)
        self.location_2 = AirQualityLocationF.create(creator=UserF.create())

    def test_get_with_anonymous(self):

        force_authenticate(self.request_get, user=self.anonym)
        response = self.view(self.request_get).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_user(self):

        force_authenticate(self.request_get, user=self.user)
        response = self.view(self.request_get).render()
        locations = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(locations), 0)

    def test_get_with_creator(self):

        force_authenticate(self.request_get, user=self.creator)
        response = self.view(self.request_get).render()
        locations = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(locations), 1)
        self.assertEqual(len(locations[0]['measurements']), 0)

    def test_get_together_with_measurements(self):

        AirQualityMeasurementF.create(
            location=self.location_1,
            creator=self.location_1.creator
        )
        AirQualityMeasurementF.create(
            location=self.location_2,
            creator=self.location_2.creator
        )

        force_authenticate(self.request_get, user=self.creator)
        response = self.view(self.request_get).render()
        locations = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(locations), 1)
        self.assertEqual(len(locations[0]['measurements']), 1)

    def test_post_with_anonymous(self):

        force_authenticate(self.request_post, user=self.anonym)
        response = self.view(self.request_post).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityLocation.objects.count(), 2)

    def test_post_with_user(self):

        force_authenticate(self.request_post, user=self.user)
        response = self.view(self.request_post).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AirQualityLocation.objects.count(), 3)


class AQLocationsSingleAPIViewTest(TestCase):

    def setUp(self):

        self.creator = UserF.create()
        self.user = UserF.create()
        self.anonym = AnonymousUser()

        self.location = AirQualityLocationF.create(creator=self.creator)

        self.url = '/api/airquality/locations/%s/' % self.location.id
        self.factory = APIRequestFactory()
        self.request_delete = self.factory.delete(
            self.url,
            content_type='application/json'
        )
        self.view = views.AQLocationsSingleAPIView.as_view()

    def test_delete_with_anonymous(self):

        force_authenticate(self.request_delete, user=self.anonym)
        response = self.view(
            self.request_delete,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityLocation.objects.count(), 1)

    def test_delete_with_user(self):

        force_authenticate(self.request_delete, user=self.user)
        response = self.view(
            self.request_delete,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityLocation.objects.count(), 1)

    def test_delete_with_creator(self):

        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            AirQualityLocation.objects.filter(pk=self.location.id).exists(),
            False
        )

    def test_delete_when_no_location(self):

        AirQualityLocation.objects.get(pk=self.location.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 404)


class AQMeasurementsAPIViewTest(TestCase):

    def setUp(self):

        self.creator = UserF.create()
        self.user = UserF.create()
        self.anonym = AnonymousUser()

        self.location = AirQualityLocationF.create(creator=self.creator)

        self.url = '/api/airquality/locations/%s/measurements/' % (
            self.location.id
        )
        self.data = {
            'barcode': 123456
        }

        self.factory = APIRequestFactory()
        self.request_post = self.factory.post(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        self.view = views.AQMeasurementsAPIView.as_view()

    def test_post_with_anonymous(self):

        force_authenticate(self.request_post, user=self.anonym)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)

    def test_post_with_user(self):

        force_authenticate(self.request_post, user=self.user)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)

    def test_post_with_creator(self):

        force_authenticate(self.request_post, user=self.creator)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AirQualityMeasurement.objects.count(), 1)
