from django.core.management.base import BaseCommand

from construction.tasks import send_task_reminders


class Command(BaseCommand):
    help = 'Sends task reminders for today'

    def handle(self, *args, **options):
        send_task_reminders()
        self.stdout.write(self.style.SUCCESS('Success!'))
