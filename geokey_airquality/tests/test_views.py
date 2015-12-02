import json

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.test import APIRequestFactory, force_authenticate

from geokey import version
from geokey.users.tests.model_factories import UserF
from geokey.projects.tests.model_factories import ProjectF

from geokey_airquality import views
from geokey_airquality.models import (
    AirQualityLocation,
    AirQualityMeasurement
)
from geokey_airquality.tests.model_factories import (
    AirQualityProjectF,
    AirQualityLocationF,
    AirQualityMeasurementF
)


error_description = 'Managing Air Quality is for superusers only.'


class AQIndexViewTest(TestCase):

    def setUp(self):

        self.superuser = UserF.create(**{'is_superuser': True})
        self.user = UserF.create(**{'is_superuser': False})
        self.anonym = AnonymousUser()

        self.template = 'aq_index.html'
        self.view = views.AQIndexView.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

        self.project = AirQualityProjectF.create(project=ProjectF.create())

    def test_get_with_anonymous(self):

        self.request.user = self.anonym
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):

        self.request.user = self.user
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Permission denied.',
                'error_description': error_description
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_superuser(self):

        self.request.user = self.superuser
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'projects': [self.project]
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)


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

    def test_delete_when_there_are_measurements(self):

        self.measurement_1 = AirQualityMeasurementF.create(
            location=self.location,
            creator=self.location.creator
        )
        self.measurement_2 = AirQualityMeasurementF.create(
            location=self.location,
            creator=self.location.creator
        )

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
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)

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

    def test_post_when_submitting_and_no_project(self):

        self.data['finished'] = timezone.now().isoformat()
        self.data['project'] = 158
        self.data['properties'] = {'results': '12.5'}
        self.request_post = self.factory.post(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        force_authenticate(self.request_post, user=self.creator)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AirQualityMeasurement.objects.count(), 1)

    def test_post_when_submitting(self):

        project = ProjectF.create(add_contributors=[self.creator])
        self.data['finished'] = timezone.now().isoformat()
        self.data['project'] = project.id
        self.data['properties'] = {'results': '12.5'}
        self.request_post = self.factory.post(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        force_authenticate(self.request_post, user=self.creator)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)

    def test_post_when_no_location(self):

        AirQualityLocation.objects.get(pk=self.location.id).delete()
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)


class AQMeasurementsSingleAPIViewTest(TestCase):

    def setUp(self):

        self.creator = UserF.create()
        self.user = UserF.create()
        self.anonym = AnonymousUser()

        self.location_1 = AirQualityLocationF.create(creator=self.creator)
        self.location_2 = AirQualityLocationF.create(creator=self.user)
        self.measurement_1 = AirQualityMeasurementF.create(
            location=self.location_1,
            creator=self.location_1.creator
        )
        self.measurement_2 = AirQualityMeasurementF.create(
            location=self.location_2,
            creator=self.location_2.creator
        )

        self.url = '/api/airquality/locations/%s/measurements/%s/' % (
            self.location_1.id,
            self.measurement_1.id
        )
        self.data = {
            'barcode': self.measurement_1.barcode,
            'finished': timezone.now().isoformat()
        }

        self.factory = APIRequestFactory()
        self.request_patch = self.factory.patch(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        self.request_delete = self.factory.delete(
            self.url,
            content_type='application/json'
        )
        self.view = views.AQMeasurementsSingleAPIView.as_view()

    def test_patch_with_anonymous(self):

        force_authenticate(self.request_patch, user=self.anonym)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_patch_with_user(self):

        force_authenticate(self.request_patch, user=self.user)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_patch_with_creator(self):

        force_authenticate(self.request_patch, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 200)

    def test_patch_when_submitting_and_no_project(self):

        self.data['project'] = 183
        self.data['properties'] = {'results': '12.5'}
        self.request_patch = self.factory.patch(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        force_authenticate(self.request_patch, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            AirQualityMeasurement.objects.filter(
                pk=self.measurement_1.id).exists(),
            True
        )

    def test_patch_when_submitting(self):

        project = ProjectF.create(add_contributors=[self.creator])
        self.data['project'] = project.id
        self.data['properties'] = {'results': '12.5'}
        self.request_patch = self.factory.patch(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        force_authenticate(self.request_patch, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            AirQualityMeasurement.objects.filter(
                pk=self.measurement_1.id).exists(),
            False
        )

    def test_patch_when_no_location(self):

        AirQualityLocation.objects.get(pk=self.location_1.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_patch_when_no_measurement(self):

        AirQualityMeasurement.objects.get(pk=self.measurement_1.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_delete_with_anonymous(self):

        force_authenticate(self.request_delete, user=self.anonym)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityMeasurement.objects.count(), 2)

    def test_delete_with_user(self):

        force_authenticate(self.request_delete, user=self.user)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityMeasurement.objects.count(), 2)

    def test_delete_with_creator(self):

        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            AirQualityMeasurement.objects.filter(
                pk=self.measurement_1.id).exists(),
            False
        )

    def test_delete_when_no_location(self):

        AirQualityLocation.objects.get(pk=self.location_1.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_delete_when_no_measurement(self):

        AirQualityMeasurement.objects.get(pk=self.measurement_1.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 404)
