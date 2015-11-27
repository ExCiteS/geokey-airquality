from django.test import TestCase
from django.core.urlresolvers import reverse, resolve

from geokey_airquality import views


class UrlsTests(TestCase):

    def test_index(self):
        reversed_url = reverse('geokey_airquality:index')
        self.assertEqual(reversed_url, '/admin/airquality/')

        resolved = resolve('/admin/airquality/')
        view = views.AQIndexView
        self.assertEqual(resolved.func.func_name, view.__name__)

    def test_api_locations(self):
        reversed_url = reverse('geokey_airquality:api_locations')
        self.assertEqual(reversed_url, '/api/airquality/locations/')

        resolved = resolve('/api/airquality/locations/')
        view = views.AQLocationsAPIView
        self.assertEqual(resolved.func.func_name, view.__name__)

    def test_api_locations_single(self):
        reversed_url = reverse(
            'geokey_airquality:api_locations_single',
            kwargs={'location_id': 1}
        )
        self.assertEqual(reversed_url, '/api/airquality/locations/1/')

        resolved_url = resolve('/api/airquality/locations/1/')
        view = views.AQLocationsSingleAPIView
        self.assertEqual(resolved_url.func.func_name, view.__name__)
        self.assertEqual(int(resolved_url.kwargs['location_id']), 1)

    def test_api_measurements(self):
        reversed_url = reverse(
            'geokey_airquality:api_measurements',
            kwargs={'location_id': 1}
        )
        self.assertEqual(
            reversed_url,
            '/api/airquality/locations/1/measurements/'
        )

        resolved_url = resolve('/api/airquality/locations/1/measurements/')
        view = views.AQMeasurementsAPIView
        self.assertEqual(resolved_url.func.func_name, view.__name__)
        self.assertEqual(int(resolved_url.kwargs['location_id']), 1)

    def test_api_measurements_single(self):
        reversed_url = reverse(
            'geokey_airquality:api_measurements_single',
            kwargs={'location_id': 1, 'measurement_id': 5}
        )
        self.assertEqual(
            reversed_url,
            '/api/airquality/locations/1/measurements/5/'
        )

        resolved_url = resolve('/api/airquality/locations/1/measurements/5/')
        view = views.AQMeasurementsSingleAPIView
        self.assertEqual(resolved_url.func.func_name, view.__name__)
        self.assertEqual(int(resolved_url.kwargs['location_id']), 1)
        self.assertEqual(int(resolved_url.kwargs['measurement_id']), 5)

    def test_api_projects(self):
        reversed_url = reverse('geokey_airquality:api_projects')
        self.assertEqual(reversed_url, '/api/airquality/projects/')

        resolved_url = resolve('/api/airquality/projects/')
        view = views.AQProjectsAPIView
        self.assertEqual(resolved_url.func.func_name, view.__name__)
