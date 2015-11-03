from django.conf.urls import patterns, url

from geokey_airquality.views import (
    AQProjectsView,
    AQPointsAPIView,
    AQPointsSingleAPIView,
    AQMeasurementsAPIView,
    AQMeasurementsSingleAPIView,
    AQProjectsAPIView,
)


urlpatterns = patterns(
    '',

    # ###########################
    # ADMIN
    # ###########################

    url(r'^admin/airquality/$',
        AQProjectsView.as_view(),
        name='index'),

    # ###########################
    # API
    # ###########################

    url(r'^api/airquality/'
        r'points/$',
        AQPointsAPIView.as_view(),
        name='api_points'),
    url(r'^api/airquality/'
        r'points/(?P<point_id>[0-9]+)/$',
        AQPointsSingleAPIView.as_view(),
        name='api_points_single'),
    url(r'^api/airquality/'
        r'points/(?P<point_id>[0-9]+)/'
        r'measurements/$',
        AQMeasurementsAPIView.as_view(),
        name='api_measurements'),
    url(r'^api/airquality/'
        r'points/(?P<point_id>[0-9]+)/'
        r'measurements/(?P<measurement_id>[0-9]+)/$',
        AQMeasurementsSingleAPIView.as_view(),
        name='api_measurements_single'),
    url(r'^api/airquality/'
        r'projects/$',
        AQProjectsAPIView.as_view(),
        name='api_projects'),
)
