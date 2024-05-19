import pytz

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from construction.models import Company, Reminder, Transaction


def send_task_reminders():
    hour = timezone.now().astimezone(pytz.timezone('America/Chicago')).hour
    for contractor in Company.objects.filter(type=Company.TYPE_CONTRACTOR, reminder_time__hour=hour):
        unsent_reminders = Reminder.objects.filter(
            task__job__owner=contractor,
            task__is_completed=False,
            reminder_sent__isnull=True,
        )
        for reminder in unsent_reminders:
            if reminder.is_due():
                reminder.task.send_reminder_to_participants()
                reminder.reminder_sent = timezone.now()
                reminder.save()


def make_payments():  # make sure it only runs once a month!
    for company in Company.objects.filter(current_plan=Company.PLAN_PRO):
        with transaction.atomic():
            timezone.now()
            company.transactions.create(
                type=Transaction.TYPE_PAYMENT, amount=settings.PRO_PLAN_FEE,
                internal_fee=settings.INTERNAL_PRO_PLAN_FEE,
                description=f'Payment for Pro plan, {timezone.now():%B %Y}',
            )
            company.current_balance += settings.PRO_PLAN_FEE
            company.save()
            # FIXME: make the Stripe charge here!
