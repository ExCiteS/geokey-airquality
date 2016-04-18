"""All URLs for the extension."""

from django.conf.urls import include, url

from rest_framework.urlpatterns import format_suffix_patterns

from geokey_airquality import views


exportpatterns = [
    url(r'^admin/airquality/export/(?P<file>[\w-]+)$',
        views.AQExportView.as_view(),
        name='export'),
]

datapatterns = format_suffix_patterns(exportpatterns, allowed=['csv'])

urlpatterns = [
    url(
        r'^', include(datapatterns)),

    # ###########################
    # ADMIN PAGES
    # ###########################

    url(r'^admin/airquality/$',
        views.AQIndexView.as_view(),
        name='index'),
    url(r'^admin/airquality/add/$',
        views.AQAddView.as_view(),
        name='add'),
    url(r'^admin/airquality/(?P<project_id>[0-9]+)/$',
        views.AQProjectView.as_view(),
        name='project'),
    url(r'^admin/airquality/(?P<project_id>[0-9]+)/remove/$',
        views.AQRemoveView.as_view(),
        name='remove'),

    # ###########################
    # ADMIN AJAX
    # ###########################

    url(r'^ajax/airquality/'
        r'projects/(?P<project_id>[0-9]+)/$',
        views.AQProjectsSingleAjaxView.as_view(),
        name='ajax_projects_single'),
    url(r'^ajax/airquality/'
        r'projects/(?P<project_id>[0-9]+)/'
        r'categories/(?P<category_id>[0-9]+)/$',
        views.AQCategoriesSingleAjaxView.as_view(),
        name='ajax_categories_single'),

    # ###########################
    # PUBLIC API
    # ###########################

    url(r'^api/airquality/'
        r'sheet/$',
        views.AQSheetAPIView.as_view(),
        name='api_sheet'),
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
]
