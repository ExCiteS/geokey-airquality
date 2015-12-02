from django.conf.urls import patterns, url

from geokey_airquality import views


urlpatterns = patterns(
    '',

    # ###########################
    # ADMIN
    # ###########################

    url(r'^admin/airquality/$',
        views.AQIndexView.as_view(),
        name='index'),
    url(r'^admin/airquality/new/$',
        views.AQNewView.as_view(),
        name='new'),
    url(r'^admin/airquality/(?P<project_id>[0-9]+)/$',
        views.AQProjectView.as_view(),
        name='project'),

    # ###########################
    # API
    # ###########################

    url(r'^api/airquality/'
        r'locations/$',
        views.AQLocationsAPIView.as_view(),
        name='api_locations'),
    url(r'^api/airquality/'
        r'locations/(?P<location_id>[0-9]+)/$',
        views.AQLocationsSingleAPIView.as_view(),
        name='api_locations_single'),
    url(r'^api/airquality/'
        r'locations/(?P<location_id>[0-9]+)/'
        r'measurements/$',
        views.AQMeasurementsAPIView.as_view(),
        name='api_measurements'),
    url(r'^api/airquality/'
        r'locations/(?P<location_id>[0-9]+)/'
        r'measurements/(?P<measurement_id>[0-9]+)/$',
        views.AQMeasurementsSingleAPIView.as_view(),
        name='api_measurements_single'),
    url(r'^api/airquality/'
        r'projects/$',
        views.AQProjectsAPIView.as_view(),
        name='api_projects'),
)
