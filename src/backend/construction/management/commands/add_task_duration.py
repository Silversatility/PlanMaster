from django.core.management.base import BaseCommand

from construction.models import Task


class Command(BaseCommand):
    help = 'Generate a duration field for tasks without duration'

    def handle(self, *args, **options):
        count = Task.objects.filter(duration__isnull=True).count()
        for task in Task.objects.filter(duration__isnull=True):
            task.duration = task.get_duration()
            task.save()
        self.stdout.write(self.style.SUCCESS('{} tasks updated!'.format(count)))
