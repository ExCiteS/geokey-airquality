"""All views for the extension."""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import operator
import csv
import StringIO

from django.conf import settings
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.generic import View, TemplateView
from django.template.defaultfilters import date as filter_date
from django.shortcuts import redirect
from django.utils import timezone, dateformat
from django.contrib import messages

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from braces.views import LoginRequiredMixin

from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.projects.models import Project
from geokey.projects.serializers import ProjectSerializer
from geokey.categories.models import Category, Field
from geokey.categories.serializers import CategorySerializer
from geokey.contributions.serializers import ContributionSerializer
from geokey.extensions.mixins import SuperuserMixin

from geokey_airquality.models import (
    AirQualityProject,
    AirQualityCategory,
    AirQualityField,
    AirQualityLocation,
    AirQualityMeasurement
)
from geokey_airquality.serializers import (
    LocationSerializer,
    MeasurementSerializer
)


permission_denied = 'Managing Air Quality is for superusers only.'


# ###########################
# ADMIN PAGES
# ###########################

class AQIndexView(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """Main index page."""

    template_name = 'aq_index.html'
    exception_message = permission_denied

    def get_context_data(self, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        all Air Quality projects to the context.

        Returns
        -------
        dict
            Context.
        """
        return super(AQIndexView, self).get_context_data(
            projects=AirQualityProject.objects.all(),
            total_locations=AirQualityLocation.objects.count(),
            total_measurements=AirQualityMeasurement.objects.count(),
            *args,
            **kwargs
        )


class AQExportView(View):
    """A view to export all measurements."""

    def get(self, request, file, *args, **kwargs):
        """
        GET method for the view.

        Export all measurements to a CSV file.

        Parameters
        ----------
        request : django.http.HttpRequest
            Represents the request.
        file : str
            Identifies the file name.

        Returns
        -------
        django.http.HttpResponse
            CSV file.
        """
        if not request.user.is_superuser:
            return HttpResponse(status=403)

        out = HttpResponse(content_type='text/csv')
        out['Content-Disposition'] = 'attachment; filename="%s - %s.csv"' % (
            'Measurements',
            dateformat.format(timezone.now(), 'l, jS \\o\\f F, Y')
        )

        fieldnames = [
            'Barcode',
            'Location',
            'Site characteristics',
            'Height from ground (m)',
            'Distance from the road (m)',
            'Additional details',
            'Date out',
            'Date in',
            'Time out',
            'Time in',
            'Exposure time (min)',
            'Exposure time (hr)',
            'Added by'
        ]

        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()

        for measurement in AirQualityMeasurement.objects.all():
            location = measurement.location

            if measurement.finished:
                exposure = measurement.finished - measurement.started
                exposure_min = int(exposure.total_seconds() / 60)
                exposure_hr = int(exposure.total_seconds() / 3600)
                date_in = filter_date(measurement.finished, 'd/m/Y')
                time_in = filter_date(measurement.finished, 'H:i')
            else:
                exposure_min = None
                exposure_hr = None
                date_in = None
                time_in = None

            row = {
                'Barcode': measurement.barcode,
                'Location': location.name,
                'Site characteristics': location.properties.get(
                    'characteristics'),
                'Height from ground (m)': location.properties.get(
                    'height'),
                'Distance from the road (m)': location.properties.get(
                    'distance'),
                'Additional details': measurement.properties.get(
                    'additional_details'),
                'Date out': filter_date(measurement.started, 'd/m/Y'),
                'Date in': date_in,
                'Time out': filter_date(measurement.started, 'H:i'),
                'Time in': time_in,
                'Exposure time (min)': exposure_min,
                'Exposure time (hr)': exposure_hr,
                'Added by': measurement.creator.display_name
            }

            writer.writerow({key: str(value).encode('utf-8') if value else None for key, value in row.iteritems()})

        return out


class AQAddView(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """Add new Air Quality project page."""

    template_name = 'aq_add.html'
    exception_message = permission_denied

    def get_context_data(self, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        all GeoKey projects, available category and field types to the context.

        Returns
        -------
        dict
            Context.
        """
        category_types = collections.OrderedDict(
            sorted(dict(AirQualityCategory.TYPES).items())
        )
        field_types = collections.OrderedDict(
            sorted(
                dict(AirQualityField.TYPES).items(),
                key=operator.itemgetter(1)
            )
        )

        return super(AQAddView, self).get_context_data(
            projects=Project.objects.filter(status='active'),
            category_types=category_types,
            field_types=field_types,
            *args,
            **kwargs
        )

    def post(self, request):
        """
        POST method for adding a new Air Quality project.

        Parameters
        ----------
        request : django.http.HttpRequest
            Represents the request.

        Returns
        -------
        django.http.HttpResponseRedirect
            When project is added, the success message is rendered, when
            redirected to the index page.
        django.http.HttpResponse
            Rendered template with an error message.
        """
        data = request.POST
        context = self.get_context_data()

        missing = False
        project = data.get('project')
        category_types = context.get('category_types')
        field_types = context.get('field_types')

        categories = {}

        if category_types is not None:
            for key, value in category_types.items():
                try:
                    categories[key] = data.get(key)
                except:
                    missing = True

        if field_types is not None:
            for key, value in field_types.items():
                try:
                    data.getlist(key)
                except:
                    missing = True

        if project and missing is False:
            try:
                project = Project.objects.get(pk=project, status='active')
                aq_project = AirQualityProject.objects.create(
                    status='active',
                    creator=request.user,
                    project=project
                )

                try:
                    for key, value in categories.items():
                        category = Category.objects.get(
                            pk=value,
                            status='active'
                        )
                        aq_category = AirQualityCategory.objects.create(
                            type=category_types.get(key),
                            category=category,
                            project=aq_project
                        )

                        index = int(key) - 1

                        try:
                            for key, value in field_types.items():
                                list = data.getlist(key)
                                field = list[index]

                                field = Field.objects.get(
                                    pk=field,
                                    status='active'
                                )
                                AirQualityField.objects.create(
                                    type=field_types.get(key),
                                    field=field,
                                    category=aq_category
                                )
                        except Field.DoesNotExist:
                            messages.error(self.request, 'Field not found.')
                            aq_project.delete()
                            return self.render_to_response(context)
                except Category.DoesNotExist:
                    messages.error(self.request, 'Category not found.')
                    aq_project.delete()
                    return self.render_to_response(context)

                project.islocked = True
                project.save()

                messages.success(
                    self.request,
                    'The project has been added.'
                )
                return redirect('geokey_airquality:index')
            except Project.DoesNotExist:
                messages.error(self.request, 'Project not found.')

        messages.error(self.request, 'An error occurred.')
        return self.render_to_response(context)


class AQProjectView(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """Air Quality project page."""

    template_name = 'aq_project.html'
    exception_message = permission_denied

    def get_context_data(self, project_id, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        all Geokey projects, current Air Quality project, available category
        and field types to the context.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database.

        Returns
        -------
        dict
            Context.
        """
        try:
            project = AirQualityProject.objects.get(pk=project_id)
        except AirQualityProject.DoesNotExist:
            return {
                'error': 'Not found.',
                'error_description': 'Project not found.'
            }

        category_types = collections.OrderedDict(
            sorted(dict(AirQualityCategory.TYPES).items())
        )
        field_types = collections.OrderedDict(
            sorted(
                dict(AirQualityField.TYPES).items(),
                key=operator.itemgetter(1)
            )
        )

        return super(AQProjectView, self).get_context_data(
            projects=Project.objects.filter(status='active'),
            project=project,
            category_types=category_types,
            field_types=field_types,
            *args,
            **kwargs
        )

    def post(self, request, project_id):
        """
        POST method for updating Air Quality project.

        Parameters
        ----------
        request : django.http.HttpRequest
            Represents the request.
        project_id : int
            Identifies the project in the database.

        Returns
        -------
        django.http.HttpResponseRedirect
            When project is updated, the success message is rendered, when
            redirected to the index page.
        django.http.HttpResponse
            Rendered template with an error message.
        """
        data = request.POST
        context = self.get_context_data(project_id)

        missing = False
        project = data.get('project')
        aq_project = context.get('project')
        category_types = context.get('category_types')
        field_types = context.get('field_types')

        categories = {}

        if category_types is not None:
            for key, value in category_types.items():
                try:
                    categories[key] = data.get(key)
                except:
                    missing = True

        if field_types is not None:
            for key, value in field_types.items():
                try:
                    data.getlist(key)
                except:
                    missing = True

        if aq_project is not None and missing is False:
            try:
                error = False

                project = Project.objects.get(pk=project, status='active')

                # Changing project should not be allowed, but just in case...
                if aq_project.project != project:
                    aq_project.project = project

                aq_project.status = 'active'
                aq_project.save()

                try:
                    for key, value in categories.items():
                        category = Category.objects.get(
                            pk=value,
                            status='active'
                        )

                        try:
                            aq_category = AirQualityCategory.objects.get(
                                type=category_types.get(key),
                                project=aq_project
                            )

                            if aq_category.category != category:
                                aq_category.category = category
                                aq_category.save()
                        except AirQualityCategory.DoesNotExist:
                            aq_category = AirQualityCategory.objects.create(
                                type=category_types.get(key),
                                category=category,
                                project=aq_project
                            )

                        index = int(key) - 1

                        try:
                            for key, value in field_types.items():
                                list = data.getlist(key)
                                field = list[index]

                                field = Field.objects.get(
                                    pk=field,
                                    status='active'
                                )

                                try:
                                    aq_field = AirQualityField.objects.get(
                                        type=field_types.get(key),
                                        category=aq_category
                                    )

                                    if aq_field.field != field:
                                        aq_field.field = field
                                        aq_field.save()
                                except AirQualityField.DoesNotExist:
                                    AirQualityField.objects.create(
                                        type=field_types.get(key),
                                        field=field,
                                        category=aq_category
                                    )
                        except Field.DoesNotExist:
                            missing = True
                            aq_category.delete()
                            aq_project.delete()
                            error = True
                except Category.DoesNotExist:
                    missing = True
                    aq_project.delete()
                    error = True

                if error is False:
                    messages.success(
                        self.request,
                        'The project has been updated.'
                    )
                    return redirect('geokey_airquality:index')
            except Project.DoesNotExist:
                messages.error(self.request, 'Project not found.')

        messages.error(self.request, 'An error occurred.')
        return self.render_to_response(context)


class AQRemoveView(LoginRequiredMixin, SuperuserMixin, TemplateView):
    """Remove Air Quality project page."""

    template_name = 'base.html'
    exception_message = permission_denied

    def get(self, request, project_id):
        """
        GET method for removing Air Quality project.

        Parameters
        ----------
        request : django.http.HttpRequest
            Represents the request.
        project_id : int
            Identifies the project in the database.

        Returns
        -------
        django.http.HttpResponseRedirect
            When project is removed, the success message is rendered, when
            redirected to the index page.
        django.http.HttpResponse
            Renders success or error message.
        """
        try:
            project = AirQualityProject.objects.get(pk=project_id)
            project.delete()
            messages.success(self.request, 'The project has been removed.')
        except AirQualityProject.DoesNotExist:
            messages.error(self.request, 'Project not found.')

        return redirect('geokey_airquality:index')


# ###########################
# ADMIN AJAX
# ###########################

class AQProjectsSingleAjaxView(APIView):
    """
    Ajax API endpoints for a single project.
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id):
        """
        Gets the serialized project.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.
        project_id : int
            Identifies the project in the database.

        Return
        ------
        rest_framework.response.Response
            Contains the serialised project or an error message.
        """

        if not request.user.is_superuser:
            raise PermissionDenied(permission_denied)

        project = Project.objects.get(pk=project_id, status='active')

        serializer = ProjectSerializer(project, context={'user': request.user})
        return Response(serializer.data)


class AQCategoriesSingleAjaxView(APIView):
    """
    Ajax API endpoints for a single category.
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, category_id):
        """
        Gets the serialized category.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.

        Return
        ------
        rest_framework.response.Response
            Contains the serialised category or an error message.
        """

        if not request.user.is_superuser:
            raise PermissionDenied(permission_denied)

        project = Project.objects.get(pk=project_id, status='active')
        category = project.categories.get(pk=category_id, status='active')

        serializer = CategorySerializer(category)
        return Response(serializer.data)


# ###########################
# PUBLIC API
# ###########################

class AQSheetAPIView(APIView):

    """
    API endpoint for a sheet.
    """

    def get(self, request):
        """
        Sends a sheet of finished measurements started by the user.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.

        Returns
        -------
        rest_framework.response.Response
            Contains empty response indicating successful send of an email or
            an error message.
        """

        user = request.user

        if user.is_anonymous():
            return Response(
                {'error': 'You have no rights to retrieve a sheet.'},
                status=status.HTTP_403_FORBIDDEN
            )

        out = StringIO.StringIO()
        fieldnames = [
            'Barcode',
            'Location',
            'Site characteristics',
            'Height from ground (m)',
            'Distance from the road (m)',
            'Additional details',
            'Date out',
            'Date in',
            'Time out',
            'Time in',
            'Exposure time (min)',
            'Exposure time (hr)'
        ]

        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()

        for measurement in AirQualityMeasurement.objects.filter(
                creator=user
        ).exclude(finished=None).distinct():
            location = measurement.location
            exposure = measurement.finished - measurement.started

            row = {
                'Barcode': measurement.barcode,
                'Location': location.name,
                'Site characteristics': location.properties.get(
                    'characteristics'),
                'Height from ground (m)': location.properties.get(
                    'height'),
                'Distance from the road (m)': location.properties.get(
                    'distance'),
                'Additional details': measurement.properties.get(
                    'additional_details'),
                'Date out': filter_date(measurement.started, 'd/m/Y'),
                'Date in': filter_date(measurement.finished, 'd/m/Y'),
                'Time out': filter_date(measurement.started, 'H:i'),
                'Time in': filter_date(measurement.finished, 'H:i'),
                'Exposure time (min)': int(exposure.total_seconds() / 60),
                'Exposure time (hr)': int(exposure.total_seconds() / 3600)
            }

            writer.writerow({key: str(value).encode('utf-8') if value else None for key, value in row.iteritems()})

        message = mail.EmailMessage(
            'Air Quality: Sheet of finished measurements',
            'Please find the attached CSV in this email.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        message.attach('sheet.csv', out.getvalue(), 'text/csv')

        connection = mail.get_connection()
        connection.open()
        connection.send_messages([message])
        connection.close()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AQProjectsAPIView(APIView):

    """
    API endpoint for all projects.
    """

    def get(self, request):
        """
        Returns a list of all projects, added to Air Quality. It includes only
        active projects, to which current user is allowed to contribute.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.

        Returns
        -------
        rest_framework.response.Response
            Contains the serialised projects.
        """

        user = request.user

        if user.is_anonymous():
            return Response(
                {'error': 'You have no rights to retrieve all projects.'},
                status=status.HTTP_403_FORBIDDEN
            )

        aq_projects = []

        for aq_project in AirQualityProject.objects.filter(status='active'):
            if aq_project.project.can_contribute(user):
                aq_projects.append(aq_project.project)

        serializer = ProjectSerializer(
            aq_projects, many=True, context={'user': user},
            fields=('id', 'name')
        )

        return Response(serializer.data)


class AQLocationsAPIView(APIView):

    """
    API endpoint for all locations.
    """

    def get(self, request):
        """
        Returns a list of all locations created by the user.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.

        Returns
        -------
        rest_framework.response.Response
            Contains the serialised locations.
        """

        user = request.user

        if user.is_anonymous():
            return Response(
                {'error': 'You have no rights to retrieve all locations.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LocationSerializer(
            AirQualityLocation.objects.filter(creator=user),
            many=True,
            context={'user': user}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Adds a location. Returns created and serialised location.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.

        Returns
        -------
        rest_framework.reponse.Response
            Contains the serialised location or an error message.
        """

        user = request.user
        data = request.data

        if user.is_anonymous():
            return Response(
                {'error': 'You have no rights to add a new location.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LocationSerializer(
            data=data, context={'user': user, 'data': data}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class AQLocationsSingleAPIView(APIView):

    """
    API endpoint for a single location.
    """

    def patch(self, request, location_id):
        """
        Updates a single location created by the user.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.
        location_id : int
            Identifies the location in the database.

        Returns
        -------
        rest_framework.response.Response
            Contains the serialised location or an error message.
        """

        user = request.user
        data = request.data

        try:
            location = AirQualityLocation.objects.get(pk=location_id)
        except AirQualityLocation.DoesNotExist:
            return Response(
                {'error': 'Location not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user != location.creator:
            return Response(
                {'error': 'You have no rights to edit this location.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LocationSerializer(
            location, data=data, context={'user': user, 'data': data}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, location_id):
        """
        Deletes a single location created by the user.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.
        location_id : int
            Identifies the location in the database.

        Returns
        -------
        rest_framework.response.Response
            Contains empty response indicating successful delete or an error
            message.
        """

        try:
            location = AirQualityLocation.objects.get(pk=location_id)
        except AirQualityLocation.DoesNotExist:
            return Response(
                {'error': 'Location not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != location.creator:
            return Response(
                {'error': 'You have no rights to delete this location.'},
                status=status.HTTP_403_FORBIDDEN
            )

        measurements = AirQualityMeasurement.objects.filter(location=location)

        for measurement in measurements:
            measurement.delete()

        location.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeasurementAPIMixin(object):

    def submit_measurement(self, request, data, instance):

        user = request.user
        project = request.data.get('project', None)
        properties = data.get('properties', None)

        if project is not None and properties is not None:
            finished = data.get('finished', None)
            results = properties.get('results', None)

            if finished is not None and results is not None:
                try:
                    project = Project.objects.get(pk=project, status='active')
                    aq_project = AirQualityProject.objects.get(
                        status='active',
                        project=project
                    )

                    category_types = dict(AirQualityCategory.TYPES)
                    field_types = dict(AirQualityField.TYPES)
                    results = float(results)

                    if results < 40:
                        category = category_types['1']
                    elif results >= 40 and results < 60:
                        category = category_types['2']
                    elif results >= 60 and results < 80:
                        category = category_types['3']
                    elif results >= 80 and results < 100:
                        category = category_types['4']
                    else:
                        category = category_types['5']

                    aq_category = AirQualityCategory.objects.get(
                        type=category,
                        project=aq_project
                    )

                    properties = {}

                    for key, value in field_types.iteritems():
                        aq_field = AirQualityField.objects.get(
                            type=value,
                            category=aq_category
                        )
                        instance_properties = instance.location.properties

                        value = None

                        if key == 'results':
                            value = results
                        elif key == 'date_out':
                            value = filter_date(instance.started, 'd/m/Y')
                        elif key == 'time_out':
                            value = filter_date(instance.started, 'H:i')
                        elif key == 'date_collected':
                            value = filter_date(instance.finished, 'd/m/Y')
                        elif key == 'time_collected':
                            value = filter_date(instance.finished, 'H:i')
                        elif key == 'exposure_min':
                            value = instance.finished - instance.started
                            value = int(value.total_seconds() / 60)
                        elif key == 'distance_from_road':
                            value = '%sm' % instance_properties.get(
                                'distance'
                            )
                        elif key == 'height':
                            value = '%sm' % instance_properties.get(
                                'height'
                            )
                        elif key == 'site_characteristics':
                            value = instance_properties.get(
                                'characteristics'
                            )
                        elif key == 'additional_details':
                            value = instance.properties.get(
                                'additional_details'
                            )

                        if value is not None:
                            properties[aq_field.field.key] = str(value)
                except:
                    return False

                if project.can_contribute(user):
                    data = {
                        'type': 'Feature',
                        'meta': {
                            'status': 'active',
                            'category': aq_category.category.id
                        },
                        'location': {
                            'geometry': instance.location.geometry.geojson
                        },
                        'properties': properties
                    }

                    serializer = ContributionSerializer(
                        data=data,
                        context={'user': user, 'project': project}
                    )

                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        instance.delete()
                        return True

        return False


class AQMeasurementsAPIView(MeasurementAPIMixin, APIView):

    """
    API endpoint for all measurements.
    """

    def post(self, request, location_id):
        """
        Adds a measurement. Returns created and serialised measurement.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.
        location_id : int
            Identifies the location in the database.

        Returns
        -------
        rest_framework.reponse.Response
            Contains the serialised measurement or an error message.
        """

        user = request.user
        data = request.data

        try:
            location = AirQualityLocation.objects.get(pk=location_id)
        except AirQualityLocation.DoesNotExist:
            return Response(
                {'error': 'Location not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != location.creator:
            return Response(
                {'error': 'You have no rights to add a new measurement.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MeasurementSerializer(
            data=data, context={
                'user': user,
                'location': location,
                'data': data
            }
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            data = serializer.data
            instance = serializer.instance

            if self.submit_measurement(request, data, instance):
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(serializer.data, status=status.HTTP_201_CREATED)


class AQMeasurementsSingleAPIView(MeasurementAPIMixin, APIView):

    """
    API endpoint for a single measurement.
    """

    def patch(self, request, location_id, measurement_id):
        """
        Updates a single measurement created by the user.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.
        location_id : int
            Identifies the location in the database.
        measurement_id : int
            Identifies the measurement in the database.

        Returns
        -------
        rest_framework.response.Response
            Contains the serialised measurement or an error message.
        """

        user = request.user
        data = request.data

        try:
            measurement = AirQualityMeasurement.objects.get(pk=measurement_id)
        except AirQualityMeasurement.DoesNotExist:
            return Response(
                {'error': 'Measurement not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user != measurement.creator:
            return Response(
                {'error': 'You have no rights to update this measurement.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MeasurementSerializer(
            measurement, data=data, context={'user': user, 'data': data}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            data = serializer.data
            instance = serializer.instance

            if self.submit_measurement(request, data, instance):
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, location_id, measurement_id):
        """
        Deletes a single measurement created by the user.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.
        location_id : int
            Identifies the location in the database.
        measurement_id : int
            Identifies the measurement in the database.

        Returns
        -------
        rest_framework.response.Response
            Contains empty response indicating successful delete or an error
            message.
        """

        try:
            measurement = AirQualityMeasurement.objects.get(pk=measurement_id)
        except AirQualityMeasurement.DoesNotExist:
            return Response(
                {'error': 'Measurement not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != measurement.creator:
            return Response(
                {'error': 'You have no rights to delete this measurement.'},
                status=status.HTTP_403_FORBIDDEN
            )

        measurement.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
