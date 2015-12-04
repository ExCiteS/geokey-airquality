from django.core import mail
from django.test import TestCase

from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectF
from geokey.categories.models import Category
from geokey.categories.tests.model_factories import CategoryFactory

from geokey_airquality.models import (
    AirQualityProject,
    AirQualityCategory,
    post_save_project,
    post_delete_project,
    post_save_category,
    post_delete_category
)
from geokey_airquality.tests.model_factories import (
    AirQualityProjectF,
    AirQualityCategoryF
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


class CategorySaveTest(TestCase):

    def test_post_save_when_category_made_inactive(self):

        project = ProjectF.create(status='active')
        category = CategoryFactory.create(project=project)

        aq_project = AirQualityProjectF.create(
            status='active',
            project=project
        )
        aq_category = AirQualityCategoryF.create(
            category=category,
            project=aq_project
        )

        category.status = 'inactive'
        category.save

        post_save_category(Category, instance=category)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'inactive')
        self.assertEqual(
            AirQualityCategory.objects.filter(pk=aq_category.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)


class CategoryDeleteTest(TestCase):

    def test_post_delete_category(self):

        project = ProjectF.create(status='active')
        category = CategoryFactory.create(project=project)

        aq_project = AirQualityProjectF.create(
            status='active',
            project=project
        )
        aq_category = AirQualityCategoryF.create(
            category=category,
            project=aq_project
        )

        category.delete()

        post_delete_category(Category, instance=category)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'inactive')
        self.assertEqual(
            AirQualityCategory.objects.filter(pk=aq_category.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)
