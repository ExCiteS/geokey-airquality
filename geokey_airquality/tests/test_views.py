import json

from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from rest_framework.test import APIRequestFactory, force_authenticate

from geokey.users.tests.model_factories import UserF

from geokey_airquality import views
from geokey_airquality.models import AirQualityLocation
from geokey_airquality.tests.model_factories import AirQualityLocationF


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

    def test_post_with_anonymous(self):
        force_authenticate(self.request_post, user=self.anonym)
        response = self.view(self.request_post).render()
        self.assertEqual(response.status_code, 403)

    def test_post_with_user(self):
        force_authenticate(self.request_post, user=self.user)
        response = self.view(self.request_post).render()
        self.assertEqual(response.status_code, 201)


class AQLocationsSingleAPIViewTest(TestCase):

    def setUp(self):
        self.creator = UserF.create()
        self.user = UserF.create()
        self.anonym = AnonymousUser()

        self.location_1 = AirQualityLocationF.create(creator=self.creator)
        self.location_2 = AirQualityLocationF.create(creator=UserF.create())

        self.url = '/api/airquality/locations/%s/' % self.location_1.id
        self.factory = APIRequestFactory()
        self.request_delete = self.factory.delete(
            self.url,
            content_type='application/json'
        )
        self.view = views.AQLocationsSingleAPIView.as_view()

        def test_delete_with_anonymous(self):
            force_authenticate(self.request_delete, user=self.anonym)
            response = self.view(self.request_delete).render()
            self.assertEqual(response.status_code, 403)

        def test_delete_with_user(self):
            force_authenticate(self.request_delete, user=self.user)
            response = self.view(self.request_delete).render()
            self.assertEqual(response.status_code, 403)

        def test_delete_with_creator(self):
            force_authenticate(self.request_delete, user=self.creator)
            response = self.view(self.request_delete).render()
            self.assertEqual(response.status_code, 204)
            self.assertEqual(
                AirQualityLocation.get(pk=self.location_1.id).exists(),
                False
            )

        def test_delete_when_no_project(self):
            AirQualityLocation.get(pk=self.location_1.id).delete()
            force_authenticate(self.request_delete, user=self.creator)
            response = self.view(self.request_delete).render()
            self.assertEqual(response.status_code, 404)
