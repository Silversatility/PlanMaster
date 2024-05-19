from time import sleep

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from .mixins import MaintenanceTaskMixin, MaintenanceTaskTimeout

UserModel = get_user_model()


class _DummyTask(MaintenanceTaskMixin, APIView):
    def run(self):
        pass


class _PassingTask(MaintenanceTaskMixin, APIView):
    timeout_seconds = 2

    def run(self):
        sleep(1)


class _FailingTask(MaintenanceTaskMixin, APIView):
    timeout_seconds = 2

    def run(self):
        sleep(3)


class MaintenanceTaskMixinTestCase(TestCase):
    def test_timeouts(self):
        with self.settings(PRIVATE_API_TOKEN='private'):
            _PassingTask().run_timed()
            with self.assertRaises(MaintenanceTaskTimeout):
                _FailingTask().run_timed()

    def test_token_valid(self):
        with self.settings(PRIVATE_API_TOKEN='private'):
            request = APIRequestFactory().post('/?token=private')
            response = _DummyTask().dispatch(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_invalid(self):
        with self.settings(PRIVATE_API_TOKEN='private'):
            request = APIRequestFactory().post('/?token=wrong')
            response = _DummyTask().dispatch(request)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_token_empty(self):
        with self.settings(PRIVATE_API_TOKEN=None):
            request = APIRequestFactory().post('/?token=any')
            response = _DummyTask().dispatch(request)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
