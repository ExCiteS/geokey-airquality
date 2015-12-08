from django.core import mail
from django.test import TestCase

from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectFactory
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
    AirQualityProjectFactory,
    AirQualityCategoryFactory,
    AirQualityFieldFactory
)


class ProjectSaveTest(TestCase):

    def test_post_save_when_project_made_inactive(self):

        project = ProjectFactory.create(status='active')
        aq_project = AirQualityProjectFactory.create(project=project)

        project.status = 'inactive'
        project.save

        post_save_project(Project, instance=project)

        self.assertEqual(
            AirQualityProject.objects.filter(pk=aq_project.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)

    def test_post_save_when_project_made_deleted(self):

        project = ProjectFactory.create(status='active')
        aq_project = AirQualityProjectFactory.create(project=project)

        project.status = 'deleted'
        project.save

        post_save_project(Project, instance=project)

        self.assertEqual(
            AirQualityProject.objects.filter(pk=aq_project.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)

    def test_post_save_when_no_aq_project(self):

        project = ProjectFactory.create(status='active')

        project.status = 'deleted'
        project.save

        post_save_project(Project, instance=project)

        self.assertEquals(len(mail.outbox), 0)


class ProjectDeleteTest(TestCase):

    def test_pre_delete_project(self):

        project = ProjectFactory.create(status='active')
        aq_project = AirQualityProjectFactory.create(project=project)

        pre_delete_project(Project, instance=project)

        self.assertEqual(
            AirQualityProject.objects.filter(pk=aq_project.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)

    def test_pre_delete_project_when_no_aq_project(self):

        project = ProjectFactory.create(status='active')

        pre_delete_project(Project, instance=project)

        self.assertEquals(len(mail.outbox), 0)


class CategorySaveTest(TestCase):

    def test_post_save_when_category_made_inactive(self):

        project = ProjectFactory.create(status='active')
        category = CategoryFactory.create(project=project)

        aq_project = AirQualityProjectFactory.create(
            status='active',
            project=project
        )
        aq_category = AirQualityCategoryFactory.create(
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

    def test_post_save_when_no_aq_category(self):

        project = ProjectFactory.create(status='active')
        category = CategoryFactory.create(project=project)

        aq_project = AirQualityProjectFactory.create(
            status='active',
            project=project
        )

        category.status = 'inactive'
        category.save

        post_save_category(Category, instance=category)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'active')
        self.assertEquals(len(mail.outbox), 0)


class CategoryDeleteTest(TestCase):

    def test_pre_delete_category(self):

        project = ProjectFactory.create(status='active')
        category = CategoryFactory.create(project=project)

        aq_project = AirQualityProjectFactory.create(
            status='active',
            project=project
        )
        aq_category = AirQualityCategoryFactory.create(
            category=category,
            project=aq_project
        )

        pre_delete_category(Category, instance=category)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'inactive')
        self.assertEqual(
            AirQualityCategory.objects.filter(pk=aq_category.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)

    def test_pre_delete_category_when_no_aq_categort(self):

        project = ProjectFactory.create(status='active')
        category = CategoryFactory.create(project=project)

        aq_project = AirQualityProjectFactory.create(
            status='active',
            project=project
        )

        pre_delete_category(Category, instance=category)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'active')
        self.assertEquals(len(mail.outbox), 0)


class FieldSaveTest(TestCase):

    def test_post_save_when_field_made_inactive(self):

        project = ProjectFactory.create(status='active')
        category = CategoryFactory.create(project=project)
        field = TextFieldFactory.create(category=category)

        aq_project = AirQualityProjectFactory.create(
            status='active',
            project=project
        )
        aq_category = AirQualityCategoryFactory.create(
            category=category,
            project=aq_project
        )
        aq_field = AirQualityFieldFactory.create(
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

    def test_post_save_when_no_aq_field(self):

        project = ProjectFactory.create(status='active')
        category = CategoryFactory.create(project=project)
        field = TextFieldFactory.create(category=category)

        aq_project = AirQualityProjectFactory.create(
            status='active',
            project=project
        )
        AirQualityCategoryFactory.create(
            category=category,
            project=aq_project
        )

        field.status = 'inactive'
        field.save

        post_save_field(TextField, instance=field)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'active')
        self.assertEquals(len(mail.outbox), 0)


class FieldDeleteTest(TestCase):

    def test_pre_delete_field(self):

        project = ProjectFactory.create(status='active')
        category = CategoryFactory.create(project=project)
        field = TextFieldFactory.create(category=category)

        aq_project = AirQualityProjectFactory.create(
            status='active',
            project=project
        )
        aq_category = AirQualityCategoryFactory.create(
            category=category,
            project=aq_project
        )
        aq_field = AirQualityFieldFactory.create(
            field=field,
            category=aq_category
        )

        pre_delete_field(TextField, instance=field)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'inactive')
        self.assertEqual(
            AirQualityField.objects.filter(pk=aq_field.id).exists(),
            False
        )
        self.assertEquals(len(mail.outbox), 1)

    def test_pre_delete_field_when_no_aq_field(self):

        project = ProjectFactory.create(status='active')
        category = CategoryFactory.create(project=project)
        field = TextFieldFactory.create(category=category)

        aq_project = AirQualityProjectFactory.create(
            status='active',
            project=project
        )
        AirQualityCategoryFactory.create(
            category=category,
            project=aq_project
        )

        pre_delete_field(TextField, instance=field)

        reference = AirQualityProject.objects.get(pk=aq_project.id)
        self.assertEqual(reference.status, 'active')
        self.assertEquals(len(mail.outbox), 0)
