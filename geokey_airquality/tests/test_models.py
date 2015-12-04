from django.core import mail
from django.test import TestCase

from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectF

from geokey_airquality.models import (
    AirQualityProject,
    post_save_project,
    post_delete_project
)
from geokey_airquality.tests.model_factories import (
    AirQualityProjectF
)


class ProjectSaveTest(TestCase):

    def test_post_save_when_project_made_inactive(self):

        project = ProjectF.create(status='active')
        aq_project = AirQualityProjectF.create(project=project)

        project.status = 'inactive'
        project.save

        post_save_project(Project, instance=project)

        self.assertEqual(
            AirQualityProject.objects.filter(pk=aq_project.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)

    def test_post_save_when_project_made_deleted(self):

        project = ProjectF.create(status='active')
        aq_project = AirQualityProjectF.create(project=project)

        project.status = 'deleted'
        project.save

        post_save_project(Project, instance=project)

        self.assertEqual(
            AirQualityProject.objects.filter(pk=aq_project.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)


class ProjectDeleteTest(TestCase):

    def test_post_delete_project(self):

        project = ProjectF.create(status='active')
        aq_project = AirQualityProjectF.create(project=project)

        project.delete()

        post_delete_project(Project, instance=project)

        self.assertEqual(
            AirQualityProject.objects.filter(pk=aq_project.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)
