from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.response import Response
from braces.views import LoginRequiredMixin

from geokey.projects.models import Project
from geokey.projects.serializers import ProjectSerializer
from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.extensions.views import SuperuserMixin

from geokey_airquality.models import AirQualityProject


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
