import collections
import operator

from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from braces.views import LoginRequiredMixin

from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.projects.models import Project
from geokey.projects.serializers import ProjectSerializer
from geokey.categories.models import Category, Field
from geokey.categories.serializer import CategorySerializer
from geokey.extensions.views import SuperuserMixin

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


# ############################################################################
#
# Admin Views
#
# ############################################################################

class AQIndexView(LoginRequiredMixin, SuperuserMixin, TemplateView):

    """
    Main page displaying a list of all projects added to Air Quality.
    """

    template_name = 'aq_index.html'
    exception_message = permission_denied

    def get_context_data(self, *args, **kwargs):
        """
        Returns the context to render the view. Overwrites the method by adding
        all Air Quality projects to the context.

        Returns
        -------
        dict
            context
        """

        projects = AirQualityProject.objects.all()

        return super(AQIndexView, self).get_context_data(
            projects=projects,
            *args,
            **kwargs
        )


class AQAddView(LoginRequiredMixin, SuperuserMixin, TemplateView):

    """
    A page for adding a new project to Air Quality.
    """

    template_name = 'aq_add.html'
    exception_message = permission_denied

    def get_context_data(self, *args, **kwargs):
        """
        Returns the context to render the view. Overwrites the method by adding
        all GeoKey projects, available category and field types to the context.

        Returns
        -------
        dict
            context
        """

        projects = Project.objects.all()

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
            projects=projects,
            category_types=category_types,
            field_types=field_types,
            *args,
            **kwargs
        )

    def post(self, request):
        """
        Adds a project.

        Parameters
        ----------
        request : django.http.HttpRequest
            Represents the request.

        Returns
        -------
        django.http.HttpResponseRedirect
            When project is added, the success message is rendered, when
            redirected to the project page.
        django.http.HttpResponse
            Rendered template with an error message.
        """

        data = request.POST
        context = self.get_context_data()

        missing = False
        project = data.get('project')
        categories = {}

        for key, value in context.get('category_types').items():
            categories[key] = data.get(key)

            if not key:
                missing = True

        field_types = context.get('field_types')

        for key, value in field_types.items():
            for entry in data.getlist(key):
                if not entry:
                    missing = True

        if project and missing is False:
            try:
                project = Project.objects.get(pk=project)
                aq_project = AirQualityProject.objects.create(
                    status='active',
                    creator=request.user,
                    project=project
                )

                try:
                    for key, value in categories.items():
                        category = Category.objects.get(pk=value)
                        aq_category = AirQualityCategory.objects.create(
                            type=context.get('category_types').get(key),
                            category=category,
                            project=aq_project
                        )

                        index = int(key) - 1

                        try:
                            for key, value in field_types.items():
                                list = data.getlist(key)
                                field = list[index]

                                field = Field.objects.get(pk=field)
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

                messages.success(
                    self.request,
                    'The project has been added.'
                )
                return redirect(
                    'geokey_airquality:project',
                    aq_project.id
                )
            except Project.DoesNotExist:
                messages.error(self.request, 'Project not found.')

        messages.error(self.request, 'An error occurred.')
        return self.render_to_response(context)


class AQProjectView(LoginRequiredMixin, SuperuserMixin, TemplateView):

    """
    A page for changing settings of a project, added to Air Quality,
    """

    template_name = 'aq_project.html'
    exception_message = permission_denied

    def get_context_data(self, project_id, *args, **kwargs):
        """
        Returns the context to render the view. Overwrites the method by adding
        all Air Quality project, available category and field types to the
        context.

        Returns
        -------
        dict
            context
        """

        projects = Project.objects.all()

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
            projects=projects,
            project=project,
            category_types=category_types,
            field_types=field_types,
            *args,
            **kwargs
        )


class AQRemoveView(LoginRequiredMixin, SuperuserMixin, TemplateView):

    """
    A page for removing a project, added to Air Quality,
    """

    template_name = 'base.html'
    exception_message = permission_denied


# ############################################################################
#
# AJAX API Views
#
# ############################################################################

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

        project = Project.objects.get(pk=project_id)

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

        project = Project.objects.get(pk=project_id)
        category = project.categories.get(pk=category_id)

        serializer = CategorySerializer(category)
        return Response(serializer.data)


# ############################################################################
#
# Public API Views
#
# ############################################################################

class AQProjectsAPIView(APIView):

    @handle_exceptions_for_ajax
    def get(self, request):
        aq_projects = []

        for aq_project in AirQualityProject.objects.all():
            if aq_project.project.can_contribute(request.user):
                aq_projects.append(aq_project.project)

        serializer = ProjectSerializer(
            aq_projects, many=True, context={'user': request.user},
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
                    project = Project.objects.get(pk=project)
                except:
                    return False

                if project.can_contribute(user):
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
