from billiard import Process

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from .permissions import PrivateTokenPermission


class MaintenanceTaskMixin:
    exclude_from_schema = True
    permission_classes = (PrivateTokenPermission,)
    timeout_seconds = settings.MAINTENANCE_TASK_TIMEOUT_SECONDS

    def post(self, request, *args, **kwargs):
        try:
            self.run_timed()
            return Response()
        except MaintenanceTaskTimeout:
            return Response(status=status.HTTP_202_ACCEPTED)

    def run_timed(self):
        process = Process(target=self.run)
        process.start()
        process.join(timeout=self.timeout_seconds)
        if process.is_alive():
            process.terminate()
            self.raise_timeout()

    @staticmethod
    def raise_timeout(*args):
        raise MaintenanceTaskTimeout()


class MaintenanceTaskTimeout(Exception):
    pass
