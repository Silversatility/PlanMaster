import os
from io import StringIO

from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory

from account.management.commands import generate_user_data
from construction import models as construction_models

from .management.commands import seed_app
from .pagination import RemovablePagination

UserModel = get_user_model()


class APIDocsTestCase(TestCase):
    def test_require_login(self):
        response = self.client.get(reverse('api-docs:docs-index'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user = UserModel.objects.create_user(email='test@example.com', password='password')
        self.client.login(email=user.email, password='password')
        response = self.client.get(reverse('api-docs:docs-index'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class HealthCheckTestCase(TestCase):
    def test_accessible(self):
        # URL is hardcoded because Pingdom would store it hardcoded
        response = self.client.get('/ht/')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MaintenanceModeTestCase(TestCase):
    def test_maintenance_mode(self):
        user = UserModel.objects.create_user(email='test@example.com', password='password')
        self.client.login(email=user.email, password='password')
        self.assertEqual(self.client.session['_auth_user_id'], str(user.id))
        with self.settings(MAINTENANCE_MODE=True):
            response = self.client.get('/')
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertNotIn('_auth_user_id', self.client.session)


class SeedAppTestCase(TestCase):
    def test_seed_users(self):
        generate_user_data.Command(stdout=StringIO()).handle(
            set_count=5, password='crewpass', filename='test_data', compact=False, fixture=False)
        seed_app.Command(stdout=StringIO()).handle(filename='test_data.json')
        fixtures_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '../account/fixtures'))
        os.remove(os.path.join(fixtures_dir, 'test_data.json'))

        superuser = authenticate(email='root@example.com', password='crewpass')
        self.assertTrue(superuser)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_seed_all_models(self):
        generate_user_data.Command(stdout=StringIO()).handle(
            set_count=5, password='crewpass', filename='test_data', compact=False, fixture=False)
        seed_app.Command(stdout=StringIO()).handle(filename='test_data.json')
        fixtures_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '../account/fixtures'))
        os.remove(os.path.join(fixtures_dir, 'test_data.json'))

        self.assertGreater(UserModel.objects.count(), 0)
        self.assertGreater(construction_models.Company.objects.count(), 0)
        self.assertGreater(construction_models.CompanyRole.objects.count(), 0)
        self.assertGreater(construction_models.Subdivision.objects.count(), 0)
        self.assertGreater(construction_models.Job.objects.count(), 0)
        self.assertGreater(construction_models.TaskCategory.objects.count(), 0)
        self.assertGreater(construction_models.TaskSubCategory.objects.count(), 0)
        self.assertGreater(construction_models.Task.objects.count(), 0)
        self.assertGreater(construction_models.Participation.objects.count(), 0)
        self.assertGreater(construction_models.Note.objects.count(), 0)
        self.assertGreater(construction_models.Document.objects.count(), 0)


class RemovablePaginationTestCase(TestCase):
    def test_limit_zero_removes_pagination(self):
        pagination = RemovablePagination()
        factory = APIRequestFactory()

        request = factory.get('/')
        request.query_params = {}
        self.assertEquals(pagination.get_page_size(request), 20)

        request = factory.get('/?limit=1')
        request.query_params = {'limit': 1}
        self.assertEquals(pagination.get_page_size(request), 1)

        request = factory.get('/?limit=0')
        request.query_params = {'limit': 0}
        self.assertEquals(pagination.get_page_size(request), 0)
