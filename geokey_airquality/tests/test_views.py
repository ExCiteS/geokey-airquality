import json
import collections
import operator

from datetime import timedelta

from django.core import mail
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.test import APIRequestFactory, force_authenticate

from geokey import version
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.models import Category
from geokey.categories.tests.model_factories import (
    CategoryFactory,
    TextFieldFactory
)
from geokey.contributions.models import Location, Observation

from geokey_airquality import views
from geokey_airquality.models import (
    AirQualityProject,
    AirQualityCategory,
    AirQualityField,
    AirQualityLocation,
    AirQualityMeasurement
)
from geokey_airquality.tests.model_factories import (
    AirQualityProjectFactory,
    AirQualityCategoryFactory,
    AirQualityFieldFactory,
    AirQualityLocationFactory,
    AirQualityMeasurementFactory
)


permission_denied = 'Managing Air Quality is for superusers only.'


# ############################################################################
#
# Admin Views
#
# ############################################################################

class AQIndexViewTest(TestCase):

    def setUp(self):

        self.superuser = UserFactory.create(**{'is_superuser': True})
        self.user = UserFactory.create(**{'is_superuser': False})
        self.anonym = AnonymousUser()

        self.template = 'aq_index.html'
        self.view = views.AQIndexView.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

        self.project = AirQualityProjectFactory.create(
            project=ProjectFactory.create()
        )

    def test_get_with_anonymous(self):

        self.request.user = self.anonym
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):

        self.request.user = self.user
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Permission denied.',
                'error_description': permission_denied
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_superuser(self):

        self.request.user = self.superuser
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'projects': [self.project]
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)


class AQAddViewTest(TestCase):

    def setUp(self):

        self.superuser = UserFactory.create(**{'is_superuser': True})
        self.user = UserFactory.create(**{'is_superuser': False})
        self.anonym = AnonymousUser()

        self.template = 'aq_add.html'
        self.view = views.AQAddView.as_view()
        self.request = HttpRequest()

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

        self.project = ProjectFactory.create()

        self.category_types = collections.OrderedDict(
            sorted(dict(AirQualityCategory.TYPES).items())
        )
        self.field_types = collections.OrderedDict(
            sorted(
                dict(AirQualityField.TYPES).items(),
                key=operator.itemgetter(1)
            )
        )

    def test_get_with_anonymous(self):

        self.request.user = self.anonym
        self.request.method = 'GET'
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):

        self.request.user = self.user
        self.request.method = 'GET'
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Permission denied.',
                'error_description': permission_denied
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_superuser(self):

        self.request.user = self.superuser
        self.request.method = 'GET'
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'projects': [self.project],
                'category_types': self.category_types,
                'field_types': self.field_types
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_when_project_marked_as_inactive(self):

        self.project.status = 'inactive'
        self.project.save()
        self.request.user = self.superuser
        self.request.method = 'GET'
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'projects': [],
                'category_types': self.category_types,
                'field_types': self.field_types
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_when_project_marked_as_deleted(self):

        self.project.status = 'deleted'
        self.project.save()
        self.request.user = self.superuser
        self.request.method = 'GET'
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'projects': [],
                'category_types': self.category_types,
                'field_types': self.field_types
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_anonymous(self):

        self.request.user = self.anonym
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_with_user(self):

        self.request.user = self.user
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Permission denied.',
                'error_description': permission_denied
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_when_project_marked_as_inactive(self):

        self.project.status = 'inactive'
        self.project.save()
        self.request.user = self.superuser
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'projects': [],
                'category_types': self.category_types,
                'field_types': self.field_types,
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_when_project_marked_as_deleted(self):

        self.project.status = 'deleted'
        self.project.save()
        self.request.user = self.superuser
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(self.request).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'projects': [],
                'category_types': self.category_types,
                'field_types': self.field_types,
                'messages': get_messages(self.request)
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)


class AQProjectViewTest(TestCase):

    def setUp(self):

        self.superuser = UserFactory.create(**{'is_superuser': True})
        self.user = UserFactory.create(**{'is_superuser': False})
        self.anonym = AnonymousUser()

        self.template = 'aq_project.html'
        self.view = views.AQProjectView.as_view()
        self.request = HttpRequest()

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

        self.project = ProjectFactory.create()
        self.aq_project = AirQualityProjectFactory.create(project=self.project)

        self.category_types = collections.OrderedDict(
            sorted(dict(AirQualityCategory.TYPES).items())
        )
        self.field_types = collections.OrderedDict(
            sorted(
                dict(AirQualityField.TYPES).items(),
                key=operator.itemgetter(1)
            )
        )

    def test_get_with_anonymous(self):

        self.request.user = self.anonym
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):

        self.request.user = self.user
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Permission denied.',
                'error_description': permission_denied
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_superuser(self):

        self.request.user = self.superuser
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'projects': [self.project],
                'project': self.aq_project,
                'category_types': self.category_types,
                'field_types': self.field_types
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_when_project_marked_as_inactive(self):

        self.project.status = 'inactive'
        self.project.save()
        self.request.user = self.superuser
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Not found.',
                'error_description': 'Project not found.'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_when_project_marked_as_deleted(self):

        self.project.status = 'deleted'
        self.project.save()
        self.request.user = self.superuser
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Not found.',
                'error_description': 'Project not found.'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_when_no_project(self):

        Project.objects.get(pk=self.project.id).delete()
        self.request.user = self.superuser
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Not found.',
                'error_description': 'Project not found.'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_when_no_aq_project(self):

        AirQualityProject.objects.get(pk=self.aq_project.id).delete()
        self.request.user = self.superuser
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Not found.',
                'error_description': 'Project not found.'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_with_anonymous(self):

        self.request.user = self.anonym
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_with_user(self):

        self.request.user = self.user
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Permission denied.',
                'error_description': permission_denied
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_when_project_marked_as_inactive(self):

        self.project.status = 'inactive'
        self.project.save()
        self.request.user = self.superuser
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Not found.',
                'error_description': 'Project not found.'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_when_project_marked_as_deleted(self):

        self.project.status = 'deleted'
        self.project.save()
        self.request.user = self.superuser
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Not found.',
                'error_description': 'Project not found.'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_when_no_project(self):

        Project.objects.get(pk=self.project.id).delete()
        self.request.user = self.superuser
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Not found.',
                'error_description': 'Project not found.'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_post_when_no_aq_project(self):

        AirQualityProject.objects.get(pk=self.aq_project.id).delete()
        self.request.user = self.superuser
        self.request.method = 'POST'
        self.request.POST = {
            'project': self.project.id
        }
        response = self.view(
            self.request,
            project_id=self.aq_project.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Not found.',
                'error_description': 'Project not found.'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)


class AQRemoveViewTest(TestCase):

    def setUp(self):

        self.superuser = UserFactory.create(**{'is_superuser': True})
        self.user = UserFactory.create(**{'is_superuser': False})
        self.anonym = AnonymousUser()

        self.template = 'base.html'
        self.view = views.AQRemoveView.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

        self.project = ProjectFactory.create()
        self.category = CategoryFactory.create()
        self.field = TextFieldFactory.create()

        self.aq_project_1 = AirQualityProjectFactory.create(
            project=self.project
        )
        self.aq_category_1 = AirQualityCategoryFactory.create(
            category=self.category,
            project=self.aq_project_1
        )
        self.aq_field_1 = AirQualityFieldFactory.create(
            field=self.field,
            category=self.aq_category_1
        )

        self.aq_project_2 = AirQualityProjectFactory.create(
            project=self.project
        )
        self.aq_category_2 = AirQualityCategoryFactory.create(
            category=self.category,
            project=self.aq_project_2
        )
        self.aq_field_1 = AirQualityFieldFactory.create(
            field=self.field,
            category=self.aq_category_2
        )

    def test_get_with_anonymous(self):

        self.request.user = self.anonym
        response = self.view(
            self.request,
            project_id=self.aq_project_1.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):

        self.request.user = self.user
        response = self.view(
            self.request,
            project_id=self.aq_project_1.id
        ).render()

        rendered = render_to_string(
            self.template,
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error': 'Permission denied.',
                'error_description': permission_denied
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_superuser(self):

        self.request.user = self.superuser
        response = self.view(
            self.request,
            project_id=self.aq_project_1.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/airquality/', response['location'])
        self.assertEqual(AirQualityProject.objects.count(), 1)
        self.assertEqual(AirQualityCategory.objects.count(), 1)
        self.assertEqual(AirQualityField.objects.count(), 1)

    def test_get_when_no_project(self):

        AirQualityProject.objects.get(pk=self.aq_project_1.id).delete()
        self.request.user = self.superuser
        response = self.view(
            self.request,
            project_id=self.aq_project_1.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/airquality/', response['location'])


# ############################################################################
#
# AJAX API Views
#
# ############################################################################

class AQProjectsSingleAjaxViewTest(TestCase):

    def setUp(self):

        self.superuser = UserFactory.create(**{'is_superuser': True})
        self.creator = UserFactory.create(**{'is_superuser': False})
        self.user = UserFactory.create(**{'is_superuser': False})
        self.anonym = AnonymousUser()

        self.project = ProjectFactory.create(add_contributors=[self.creator])

        self.url = '/ajax/airquality/projects/%s/' % self.project.id

        self.factory = APIRequestFactory()
        self.request_get = self.factory.get(self.url)
        self.view = views.AQProjectsSingleAjaxView.as_view()

    def test_get_with_anonymous(self):

        force_authenticate(self.request_get, user=self.anonym)
        response = self.view(
            self.request_get,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_user(self):

        force_authenticate(self.request_get, user=self.user)
        response = self.view(
            self.request_get,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_creator(self):

        force_authenticate(self.request_get, user=self.creator)
        response = self.view(
            self.request_get,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_superuser(self):

        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id
        ).render()
        project = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(project['id'], self.project.id)

    def test_get_when_project_marked_as_inactive(self):

        self.project.status = 'inactive'
        self.project.save()
        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_get_when_project_marked_as_deleted(self):

        self.project.status = 'deleted'
        self.project.save()
        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_get_when_no_project(self):

        Project.objects.get(pk=self.project.id).delete()
        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id
        ).render()

        self.assertEqual(response.status_code, 404)


class AQCategoriesSingleAjaxViewTest(TestCase):

    def setUp(self):

        self.superuser = UserFactory.create(**{'is_superuser': True})
        self.creator = UserFactory.create(**{'is_superuser': False})
        self.user = UserFactory.create(**{'is_superuser': False})
        self.anonym = AnonymousUser()

        self.project = ProjectFactory.create(add_contributors=[self.creator])
        self.category = CategoryFactory.create(
            creator=self.creator,
            project=self.project
        )

        self.url = '/ajax/airquality/projects/%s/categories/%s/' % (
            self.project.id,
            self.category.id
        )

        self.factory = APIRequestFactory()
        self.request_get = self.factory.get(self.url)
        self.view = views.AQCategoriesSingleAjaxView.as_view()

    def test_get_with_anonymous(self):

        force_authenticate(self.request_get, user=self.anonym)
        response = self.view(
            self.request_get,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_user(self):

        force_authenticate(self.request_get, user=self.user)
        response = self.view(
            self.request_get,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_creator(self):

        force_authenticate(self.request_get, user=self.creator)
        response = self.view(
            self.request_get,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_superuser(self):

        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()
        category = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(category['id'], self.category.id)

    def test_get_when_project_marked_as_inactive(self):

        self.project.status = 'inactive'
        self.project.save()
        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_get_when_project_marked_as_deleted(self):

        self.project.status = 'deleted'
        self.project.save()
        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_get_when_no_project(self):

        Project.objects.get(pk=self.project.id).delete()
        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_get_when_category_marked_as_inactive(self):

        self.category.status = 'inactive'
        self.category.save()
        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_get_when_no_category(self):

        Category.objects.get(pk=self.category.id).delete()
        force_authenticate(self.request_get, user=self.superuser)
        response = self.view(
            self.request_get,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 404)


# ############################################################################
#
# Public API Views
#
# ############################################################################

class AQSheetAPIViewTest(TestCase):

    def setUp(self):

        self.creator = UserFactory.create()
        self.user = UserFactory.create()
        self.anonym = AnonymousUser()

        self.url = '/api/airquality/sheet/'
        self.factory = APIRequestFactory()
        self.request_get = self.factory.get(self.url)
        self.view = views.AQSheetAPIView.as_view()

        self.location_1 = AirQualityLocationFactory.create(
            creator=self.creator
        )
        self.location_2 = AirQualityLocationFactory.create(
            creator=UserFactory.create()
        )

        AirQualityMeasurementFactory.create(
            location=self.location_1,
            creator=self.location_1.creator,
            finished=timezone.now()
        )
        AirQualityMeasurementFactory.create(
            location=self.location_1,
            creator=self.location_1.creator
        )

    def test_get_with_anonymous(self):

        force_authenticate(self.request_get, user=self.anonym)
        response = self.view(self.request_get).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_user(self):

        force_authenticate(self.request_get, user=self.user)
        response = self.view(self.request_get).render()

        self.assertEqual(response.status_code, 204)
        self.assertEquals(len(mail.outbox), 1)

    def test_get_with_creator(self):

        force_authenticate(self.request_get, user=self.creator)
        response = self.view(self.request_get).render()

        self.assertEqual(response.status_code, 204)
        self.assertEquals(len(mail.outbox), 1)


class AQProjectsAPIViewTest(TestCase):

    def setUp(self):

        self.contributor = UserFactory.create()
        self.user = UserFactory.create()
        self.anonym = AnonymousUser()

        self.url = '/api/airquality/projects/'
        self.factory = APIRequestFactory()
        self.request_get = self.factory.get(self.url)
        self.view = views.AQProjectsAPIView.as_view()

        self.project_1 = ProjectFactory.create(
            add_contributors=[self.contributor]
        )
        self.project_2 = ProjectFactory.create(
            add_contributors=[self.contributor]
        )
        self.project_3 = ProjectFactory.create(
            add_contributors=[self.contributor]
        )
        self.aq_project_1 = AirQualityProjectFactory.create(
            project=self.project_1
        )
        self.aq_project_2 = AirQualityProjectFactory.create(
            status='inactive',
            project=self.project_2
        )

    def test_get_with_anonymous(self):

        force_authenticate(self.request_get, user=self.anonym)
        response = self.view(self.request_get).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_user(self):

        force_authenticate(self.request_get, user=self.user)
        response = self.view(self.request_get).render()
        projects = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 0)

    def test_get_with_contributor(self):

        force_authenticate(self.request_get, user=self.contributor)
        response = self.view(self.request_get).render()
        projects = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['id'], self.project_1.id)

    def test_get_when_original_project_deleted(self):

        self.aq_project_3 = AirQualityProjectFactory.create(
            project=self.project_3
        )
        self.project_3.delete()

        force_authenticate(self.request_get, user=self.contributor)
        response = self.view(self.request_get).render()
        projects = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(projects), 1)
        self.assertEqual(AirQualityProject.objects.count(), 2)


class AQLocationsAPIViewTest(TestCase):

    def setUp(self):

        self.creator = UserFactory.create()
        self.user = UserFactory.create()
        self.anonym = AnonymousUser()

        self.url = '/api/airquality/locations/'
        self.data = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [-0.134, 51.524]
            },
            'name': 'Test Location',
            'properties': {
                'distance': 2
            }
        }

        self.factory = APIRequestFactory()
        self.request_get = self.factory.get(self.url)
        self.request_post = self.factory.post(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        self.view = views.AQLocationsAPIView.as_view()

        self.location_1 = AirQualityLocationFactory.create(
            creator=self.creator
        )
        self.location_2 = AirQualityLocationFactory.create(
            creator=UserFactory.create()
        )

    def test_get_with_anonymous(self):

        force_authenticate(self.request_get, user=self.anonym)
        response = self.view(self.request_get).render()

        self.assertEqual(response.status_code, 403)

    def test_get_with_user(self):

        force_authenticate(self.request_get, user=self.user)
        response = self.view(self.request_get).render()
        locations = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(locations), 0)

    def test_get_with_creator(self):

        force_authenticate(self.request_get, user=self.creator)
        response = self.view(self.request_get).render()
        locations = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(locations), 1)
        self.assertEqual(len(locations[0]['measurements']), 0)

    def test_get_together_with_measurements(self):

        AirQualityMeasurementFactory.create(
            location=self.location_1,
            creator=self.location_1.creator
        )
        AirQualityMeasurementFactory.create(
            location=self.location_2,
            creator=self.location_2.creator
        )

        force_authenticate(self.request_get, user=self.creator)
        response = self.view(self.request_get).render()
        locations = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(locations), 1)
        self.assertEqual(len(locations[0]['measurements']), 1)

    def test_post_with_anonymous(self):

        force_authenticate(self.request_post, user=self.anonym)
        response = self.view(self.request_post).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityLocation.objects.count(), 2)

    def test_post_with_user(self):

        force_authenticate(self.request_post, user=self.user)
        response = self.view(self.request_post).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AirQualityLocation.objects.count(), 3)


class AQLocationsSingleAPIViewTest(TestCase):

    def setUp(self):

        self.creator = UserFactory.create()
        self.user = UserFactory.create()
        self.anonym = AnonymousUser()

        self.location = AirQualityLocationFactory.create(creator=self.creator)

        self.url = '/api/airquality/locations/%s/' % self.location.id
        self.factory = APIRequestFactory()
        self.request_delete = self.factory.delete(
            self.url,
            content_type='application/json'
        )
        self.view = views.AQLocationsSingleAPIView.as_view()

    def test_delete_with_anonymous(self):

        force_authenticate(self.request_delete, user=self.anonym)
        response = self.view(
            self.request_delete,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityLocation.objects.count(), 1)

    def test_delete_with_user(self):

        force_authenticate(self.request_delete, user=self.user)
        response = self.view(
            self.request_delete,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityLocation.objects.count(), 1)

    def test_delete_with_creator(self):

        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            AirQualityLocation.objects.filter(pk=self.location.id).exists(),
            False
        )

    def test_delete_when_there_are_measurements(self):

        self.measurement_1 = AirQualityMeasurementFactory.create(
            location=self.location,
            creator=self.location.creator
        )
        self.measurement_2 = AirQualityMeasurementFactory.create(
            location=self.location,
            creator=self.location.creator
        )

        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            AirQualityLocation.objects.filter(pk=self.location.id).exists(),
            False
        )
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)

    def test_delete_when_no_location(self):

        AirQualityLocation.objects.get(pk=self.location.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 404)


class AQMeasurementsAPIViewTest(TestCase):

    def setUp(self):

        self.creator = UserFactory.create()
        self.user = UserFactory.create()
        self.anonym = AnonymousUser()

        self.location = AirQualityLocationFactory.create(
            creator=self.creator,
            properties={
                'height': 2,
                'distance': 10
            }
        )

        self.url = '/api/airquality/locations/%s/measurements/' % (
            self.location.id
        )
        self.data = {
            'barcode': 123456,
            'started': (timezone.now() - timedelta(days=28)).isoformat(),
            'called': timezone.now().isoformat()
        }

        self.factory = APIRequestFactory()
        self.request_post = self.factory.post(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        self.view = views.AQMeasurementsAPIView.as_view()

        self.project = ProjectFactory.create(add_contributors=[self.creator])
        self.aq_project = AirQualityProjectFactory.create(project=self.project)
        self.category = CategoryFactory.create(project=self.project)
        self.aq_category = AirQualityCategoryFactory.create(
            type='40-60',
            category=self.category,
            project=self.aq_project
        )
        self.field_1 = TextFieldFactory.create(category=self.category)
        self.field_2 = TextFieldFactory.create(category=self.category)
        self.field_3 = TextFieldFactory.create(category=self.category)
        self.field_4 = TextFieldFactory.create(category=self.category)
        self.field_5 = TextFieldFactory.create(category=self.category)
        self.field_6 = TextFieldFactory.create(category=self.category)
        self.field_7 = TextFieldFactory.create(category=self.category)
        self.field_8 = TextFieldFactory.create(category=self.category)
        self.field_9 = TextFieldFactory.create(category=self.category)
        self.field_10 = TextFieldFactory.create(category=self.category)
        self.aq_field_1 = AirQualityFieldFactory.create(
            type='01. Results',
            field=self.field_1,
            category=self.aq_category
        )
        self.aq_field_2 = AirQualityFieldFactory.create(
            type='02. Date out',
            field=self.field_2,
            category=self.aq_category
        )
        self.aq_field_3 = AirQualityFieldFactory.create(
            type='03. Time out',
            field=self.field_3,
            category=self.aq_category
        )
        self.aq_field_4 = AirQualityFieldFactory.create(
            type='04. Date collected',
            field=self.field_4,
            category=self.aq_category
        )
        self.aq_field_5 = AirQualityFieldFactory.create(
            type='05. Time collected',
            field=self.field_5,
            category=self.aq_category
        )
        self.aq_field_6 = AirQualityFieldFactory.create(
            type='06. Exposure time (min)',
            field=self.field_6,
            category=self.aq_category
        )
        self.aq_field_7 = AirQualityFieldFactory.create(
            type='07. Distance from the road',
            field=self.field_7,
            category=self.aq_category
        )
        self.aq_field_8 = AirQualityFieldFactory.create(
            type='08. Height from ground',
            field=self.field_8,
            category=self.aq_category
        )
        self.aq_field_9 = AirQualityFieldFactory.create(
            type='09. Site characteristics',
            field=self.field_9,
            category=self.aq_category
        )
        self.aq_field_10 = AirQualityFieldFactory.create(
            type='10. Additional details',
            field=self.field_10,
            category=self.aq_category
        )

    def test_post_with_anonymous(self):

        force_authenticate(self.request_post, user=self.anonym)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)

    def test_post_with_user(self):

        force_authenticate(self.request_post, user=self.user)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)

    def test_post_with_creator(self):

        force_authenticate(self.request_post, user=self.creator)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AirQualityMeasurement.objects.count(), 1)

    def test_post_when_submitting_and_no_project(self):

        self.data['finished'] = timezone.now().isoformat()
        self.data['project'] = 158
        self.data['properties'] = {'results': 45.15}
        self.request_post = self.factory.post(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        force_authenticate(self.request_post, user=self.creator)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AirQualityMeasurement.objects.count(), 1)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(Observation.objects.count(), 0)

    def test_post_when_submitting(self):

        self.data['finished'] = timezone.now().isoformat()
        self.data['project'] = self.project.id
        self.data['properties'] = {'results': 48.05}

        self.request_post = self.factory.post(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        force_authenticate(self.request_post, user=self.creator)
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Observation.objects.count(), 1)

    def test_post_when_no_location(self):

        AirQualityLocation.objects.get(pk=self.location.id).delete()
        response = self.view(
            self.request_post,
            location_id=self.location.id
        ).render()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(AirQualityMeasurement.objects.count(), 0)


class AQMeasurementsSingleAPIViewTest(TestCase):

    def setUp(self):

        self.creator = UserFactory.create()
        self.user = UserFactory.create()
        self.anonym = AnonymousUser()

        self.location_1 = AirQualityLocationFactory.create(
            creator=self.creator,
            properties={
                'additional_details': 'Heavy traffic.'
            }
        )
        self.location_2 = AirQualityLocationFactory.create(creator=self.user)
        self.measurement_1 = AirQualityMeasurementFactory.create(
            location=self.location_1,
            creator=self.location_1.creator
        )
        self.measurement_2 = AirQualityMeasurementFactory.create(
            location=self.location_2,
            creator=self.location_2.creator
        )

        self.url = '/api/airquality/locations/%s/measurements/%s/' % (
            self.location_1.id,
            self.measurement_1.id
        )
        self.data = {
            'barcode': self.measurement_1.barcode,
            'started': (timezone.now() - timedelta(days=28)).isoformat(),
            'finished': timezone.now().isoformat(),
            'called': timezone.now().isoformat()
        }

        self.factory = APIRequestFactory()
        self.request_patch = self.factory.patch(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        self.request_delete = self.factory.delete(
            self.url,
            content_type='application/json'
        )
        self.view = views.AQMeasurementsSingleAPIView.as_view()

        self.project = ProjectFactory.create(add_contributors=[self.creator])
        self.aq_project = AirQualityProjectFactory.create(project=self.project)
        self.category = CategoryFactory.create(project=self.project)
        self.aq_category = AirQualityCategoryFactory.create(
            type='60-80',
            category=self.category,
            project=self.aq_project
        )
        self.field_1 = TextFieldFactory.create(category=self.category)
        self.field_2 = TextFieldFactory.create(category=self.category)
        self.field_3 = TextFieldFactory.create(category=self.category)
        self.field_4 = TextFieldFactory.create(category=self.category)
        self.field_5 = TextFieldFactory.create(category=self.category)
        self.field_6 = TextFieldFactory.create(category=self.category)
        self.field_7 = TextFieldFactory.create(category=self.category)
        self.field_8 = TextFieldFactory.create(category=self.category)
        self.field_9 = TextFieldFactory.create(category=self.category)
        self.field_10 = TextFieldFactory.create(category=self.category)
        self.aq_field_1 = AirQualityFieldFactory.create(
            type='01. Results',
            field=self.field_1,
            category=self.aq_category
        )
        self.aq_field_2 = AirQualityFieldFactory.create(
            type='02. Date out',
            field=self.field_2,
            category=self.aq_category
        )
        self.aq_field_3 = AirQualityFieldFactory.create(
            type='03. Time out',
            field=self.field_3,
            category=self.aq_category
        )
        self.aq_field_4 = AirQualityFieldFactory.create(
            type='04. Date collected',
            field=self.field_4,
            category=self.aq_category
        )
        self.aq_field_5 = AirQualityFieldFactory.create(
            type='05. Time collected',
            field=self.field_5,
            category=self.aq_category
        )
        self.aq_field_6 = AirQualityFieldFactory.create(
            type='06. Exposure time (min)',
            field=self.field_6,
            category=self.aq_category
        )
        self.aq_field_7 = AirQualityFieldFactory.create(
            type='07. Distance from the road',
            field=self.field_7,
            category=self.aq_category
        )
        self.aq_field_8 = AirQualityFieldFactory.create(
            type='08. Height from ground',
            field=self.field_8,
            category=self.aq_category
        )
        self.aq_field_9 = AirQualityFieldFactory.create(
            type='09. Site characteristics',
            field=self.field_9,
            category=self.aq_category
        )
        self.aq_field_10 = AirQualityFieldFactory.create(
            type='10. Additional details',
            field=self.field_10,
            category=self.aq_category
        )

    def test_patch_with_anonymous(self):

        force_authenticate(self.request_patch, user=self.anonym)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_patch_with_user(self):

        force_authenticate(self.request_patch, user=self.user)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 403)

    def test_patch_with_creator(self):

        force_authenticate(self.request_patch, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 200)

    def test_patch_when_submitting_and_no_project(self):

        self.data['project'] = 183
        self.data['properties'] = {'results': 70.51}
        self.request_patch = self.factory.patch(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        force_authenticate(self.request_patch, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            AirQualityMeasurement.objects.filter(
                pk=self.measurement_1.id).exists(),
            True
        )
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(Observation.objects.count(), 0)

    def test_patch_when_submitting(self):

        self.data['project'] = self.project.id
        self.data['properties'] = {'results': 72.78}
        self.request_patch = self.factory.patch(
            self.url,
            json.dumps(self.data),
            content_type='application/json'
        )
        force_authenticate(self.request_patch, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            AirQualityMeasurement.objects.filter(
                pk=self.measurement_1.id).exists(),
            False
        )
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Observation.objects.count(), 1)

    def test_patch_when_no_location(self):

        AirQualityLocation.objects.get(pk=self.location_1.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_patch_when_no_measurement(self):

        AirQualityMeasurement.objects.get(pk=self.measurement_1.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_patch,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_delete_with_anonymous(self):

        force_authenticate(self.request_delete, user=self.anonym)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityMeasurement.objects.count(), 2)

    def test_delete_with_user(self):

        force_authenticate(self.request_delete, user=self.user)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(AirQualityMeasurement.objects.count(), 2)

    def test_delete_with_creator(self):

        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            AirQualityMeasurement.objects.filter(
                pk=self.measurement_1.id).exists(),
            False
        )

    def test_delete_when_no_location(self):

        AirQualityLocation.objects.get(pk=self.location_1.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_delete_when_no_measurement(self):

        AirQualityMeasurement.objects.get(pk=self.measurement_1.id).delete()
        force_authenticate(self.request_delete, user=self.creator)
        response = self.view(
            self.request_delete,
            location_id=self.location_1.id,
            measurement_id=self.measurement_1.id
        ).render()

        self.assertEqual(response.status_code, 404)
