from django.views.generic import TemplateView

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from braces.views import LoginRequiredMixin

from geokey.users.models import User
from geokey.projects.models import Project
from geokey.projects.serializers import ProjectSerializer
from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.extensions.views import SuperuserMixin

from geokey_airquality.models import (
    AirQualityPoint,
    AirQualityMeasurement,
    AirQualityProject
)
from geokey_airquality.serializers import (
    PointSerializer,
    MeasurementSerializer
)


class AQProjectsView(LoginRequiredMixin, SuperuserMixin, TemplateView):

    template_name = 'aq_index.html'
    exception_message = 'Managing Air Quality is for superusers only.'

    def get_context_data(self, *args, **kwargs):
        projects = Project.objects.all()
        enabled = AirQualityProject.objects.filter(project__in=projects)

        return super(AQProjectsView, self).get_context_data(
            projects=projects,
            enabled=enabled,
            *args,
            **kwargs
        )

    def update_projects(self, projects, enabled, form=[]):
        for project in projects:
            if project in enabled and not str(project.id) in form:
                AirQualityProject.objects.get(project=project).delete()
            elif project not in enabled and str(project.id) in form:
                AirQualityProject.objects.create(project=project)

    def post(self, request):
        context = self.get_context_data()

        self.update_projects(
            context.get('projects'),
            [aq.project for aq in context.get('enabled')],
            self.request.POST.getlist('airquality_project')
        )

        return self.render_to_response(context)


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


class AQPointsAPIView(APIView):

    """
    API endpoint for all points.
    """

    def get(self, request):
        """
        Returns a list of all points.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised points.
        """

        user = request.user

        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        points = AirQualityPoint.objects.filter(creator=user)
        serializer = PointSerializer(points, many=True, context={'user': user})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Adds a point. Returns created and serialised point.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.

        Returns
        -------
        rest_framework.reponse.Response
            Contains the serialised point or an error message.
        """

        user = request.user
        data = request.data

        if user.is_anonymous():
            return Response(
                {'error': 'You have no rights to add a point.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PointSerializer(
            data=data, context={'user': user, 'data': data}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class AQPointsSingleAPIView(APIView):

    """
    API endpoint for a single point.
    """

    def delete(self, request, point_id):
        """
        Deletes a single point.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.
        point_id : int
            Identifies the point in the database.

        Returns
        -------
        rest_framework.response.Respone
            Contains empty response indicating successful delete or an error
            message.
        """

        try:
            point = AirQualityPoint.objects.get(pk=point_id)
        except AirQualityPoint.DoesNotExist:
            return Response(
                {'error': 'Point not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != point.creator:
            return Response(
                {'error': 'You have no rights to delete this point.'},
                status=status.HTTP_403_FORBIDDEN
            )

        for measurement in AirQualityMeasurement.objects.filter(point=point):
            measurement.delete()

        point.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AQMeasurementsAPIView(APIView):

    """
    API endpoint for all measurements.
    """

    def post(self, request, point_id):
        """
        Adds a measurement. Returns created and serialised measurement.

        Parameter
        ---------
        request : rest_framework.request.Request
            Object representing the request.
        point_id : int
            Identifies the point in the database.

        Returns
        -------
        rest_framework.reponse.Response
            Contains the serialised measurement or an error message.
        """

        user = request.user
        data = request.data

        try:
            point = AirQualityPoint.objects.get(pk=point_id)
        except AirQualityPoint.DoesNotExist:
            return Response(
                {'error': 'Point not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != point.creator:
            return Response(
                {'error': 'You have no rights to add a measurement.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MeasurementSerializer(
            data=data, context={'user': user, 'point': point, 'data': data}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class AQMeasurementsSingleAPIView(APIView):

    """
    API endpoint for a single measurement.
    """

    def patch(self, request, point_id, measurement_id):
        """
        Updates a single measurement.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.
        point_id : int
            Identifies the point in the database.
        measurement_id : int
            Identifies the measurement in the database.

        Returns
        -------
        rest_framework.response.Respone
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
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, point_id, measurement_id):
        """
        Deletes a single measurement.

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request.
        point_id : int
            Identifies the point in the database.
        measurement_id : int
            Identifies the measurement in the database.

        Returns
        -------
        rest_framework.response.Respone
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
