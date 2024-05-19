from datetime import timedelta
from unittest.mock import patch
import pytz

from freezegun import freeze_time
from django.test import TestCase
from django.utils import timezone

from cbcommon import mommy_recipes

from ..tasks import send_task_reminders
from ..models import Reminder

midnight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
today = midnight.date()


@freeze_time(midnight)
class SendTaskRemindersTestCase(TestCase):
    def test_remind_today(self):
        midnight_local = timezone.now().astimezone(pytz.timezone('America/Chicago')).time()
        contractor = mommy_recipes.contractor.make(reminder_time=midnight_local)
        Reminder.objects.create(
            task=mommy_recipes.task.make(
                job__owner=contractor,
                start_date=today + timedelta(days=5),
                end_date=today + timedelta(days=5),
            ),
            reminder_days=5,
        )  # to remind today
        Reminder.objects.create(
            task=mommy_recipes.task.make(
                job__owner=contractor,
                start_date=today + timedelta(days=7),
                end_date=today + timedelta(days=7),
            ),
            reminder_days=6,
        )  # to remind tomorrow

        with patch('construction.models.Task.send_reminder_to_participants') as send_reminder:
            send_task_reminders()
            send_reminder.assert_called_once()

    def test_avoid_double_reminders(self):
        midnight_local = timezone.now().astimezone(pytz.timezone('America/Chicago')).time()
        contractor = mommy_recipes.contractor.make(reminder_time=midnight_local)
        Reminder.objects.create(
            task=mommy_recipes.task.make(
                job__owner=contractor,
                start_date=today + timedelta(days=5),
                end_date=today + timedelta(days=5),
            ),
            reminder_days=5,
        )  # to remind today

        with patch('construction.models.Task.send_reminder_to_participants') as send_reminder:
            send_task_reminders()
            send_task_reminders()  # already reminded
            send_reminder.assert_called_once()

    def test_remind_catch_yesterday(self):
        midnight_local = timezone.now().astimezone(pytz.timezone('America/Chicago')).time()
        contractor = mommy_recipes.contractor.make(reminder_time=midnight_local)
        Reminder.objects.create(
            task=mommy_recipes.task.make(
                job__owner=contractor,
                start_date=today + timedelta(days=1),
                end_date=today + timedelta(days=1),
            ),
            reminder_days=2,
        )  # to remind yesterday

        with patch('construction.models.Task.send_reminder_to_participants') as send_reminder:
            send_task_reminders()
            send_reminder.assert_called_once()
