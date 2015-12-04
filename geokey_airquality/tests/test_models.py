from django.test import TestCase

from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectF

from geokey_airquality.models import AirQualityProject, post_save_project
from geokey_airquality.tests.model_factories import AirQualityProjectF


class ProjectSaveTest(TestCase):

    def test_post_save_project_when_deleting(self):

        project = ProjectF.create(status='active')
        aq_project = AirQualityProjectF.create(project=project)

        project.status = 'deleted'
        project.save

        post_save_project(Project, instance=project)

        self.assertEqual(
            AirQualityProject.objects.filter(pk=aq_project.id).exists(),
            False
        )
