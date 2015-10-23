from django.conf.urls import patterns, url

from geokey_airquality.views import (
    AQProjectsView,
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
        r'projects/$',
        AQProjectsAPIView.as_view(),
        name='api_projects'),
)
