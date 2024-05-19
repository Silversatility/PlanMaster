import os

from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

from rest_framework.views import APIView

from account.models import AuthToken
from construction.tasks import send_task_reminders

from .mixins import MaintenanceTaskMixin


class DeleteExpiredTokensView(MaintenanceTaskMixin, APIView):
    def run(self):
        AuthToken.objects.filter(timestamp_expires__lt=timezone.now()).delete()


# To load the backups, run `python manage.py flush --noinput && python manage.py loaddata [path_to_backup_file]`
# Note: `python manage.py flush --noinput` will clear all data before loading the backup
class MakeBackupView(MaintenanceTaskMixin, APIView):
    def run(self):
        if not os.path.exists(settings.BACKUP_DIR):
            os.makedirs(settings.BACKUP_DIR)
        filename = timezone.now().strftime("%Y%m%d-%H%M%S") + '.json'
        with open(os.path.join(settings.BACKUP_DIR, filename), 'w') as fd:
            call_command('dumpdata', stdout=fd)


class SendTaskReminders(MaintenanceTaskMixin, APIView):
    def run(self):
        send_task_reminders()
