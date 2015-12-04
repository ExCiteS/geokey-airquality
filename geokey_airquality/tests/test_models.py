from django.core import mail
from django.test import TestCase

from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectF
from geokey.categories.models import Category, TextField
from geokey.categories.tests.model_factories import (
    CategoryFactory,
    TextFieldFactory
)

from geokey_airquality.models import (
    AirQualityProject,
    AirQualityCategory,
    AirQualityField,
    post_save_project,
    pre_delete_project,
    post_save_category,
    pre_delete_category,
    post_save_field,
    pre_delete_field
)
from geokey_airquality.tests.model_factories import (
    AirQualityProjectF,
    AirQualityCategoryF,
    AirQualityFieldF
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

    def test_pre_delete_project(self):

        project = ProjectF.create(status='active')
        aq_project = AirQualityProjectF.create(project=project)

        project.delete()

        pre_delete_project(Project, instance=project)

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

    def test_pre_delete_category(self):

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

        pre_delete_category(Category, instance=category)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'inactive')
        self.assertEqual(
            AirQualityCategory.objects.filter(pk=aq_category.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)


class FieldSaveTest(TestCase):

    def test_post_save_when_field_made_inactive(self):

        project = ProjectF.create(status='active')
        category = CategoryFactory.create(project=project)
        field = TextFieldFactory.create(category=category)

        aq_project = AirQualityProjectF.create(
            status='active',
            project=project
        )
        aq_category = AirQualityCategoryF.create(
            category=category,
            project=aq_project
        )
        aq_field = AirQualityFieldF.create(
            field=field,
            category=aq_category
        )

        field.status = 'inactive'
        field.save

        post_save_field(TextField, instance=field)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'inactive')
        self.assertEqual(
            AirQualityField.objects.filter(pk=aq_field.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)


class FieldDeleteTest(TestCase):

    def test_pre_delete_field(self):

        project = ProjectF.create(status='active')
        category = CategoryFactory.create(project=project)
        field = TextFieldFactory.create(category=category)

        aq_project = AirQualityProjectF.create(
            status='active',
            project=project
        )
        aq_category = AirQualityCategoryF.create(
            category=category,
            project=aq_project
        )
        aq_field = AirQualityFieldF.create(
            field=field,
            category=aq_category
        )

        field.delete()

        pre_delete_field(TextField, instance=field)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'inactive')
        self.assertEqual(
            AirQualityField.objects.filter(pk=aq_field.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)
