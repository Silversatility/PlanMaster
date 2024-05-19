import random
import re
from datetime import time, timedelta
from unittest import expectedFailure
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from freezegun import freeze_time

from account.models import AuthToken, User
from cbcommon import mommy_recipes

from ..serializers import UserSerializer
from .. import models

UserModel = get_user_model()
midnight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
monday = midnight - timedelta(days=midnight.weekday()) + timedelta(days=1)


class ProtectedViewMixIn:
    def setUp(self):
        """\
        Must be called explicitly from the setUp method of the class inheriting from TestCase, as shown below:
        ProtectedViewMixIn.setUp(self)
        """
        self.superuser = mommy_recipes.user.make(is_superuser=True, is_staff=True)

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


@freeze_time(monday)
class UserViewSetTestCase(APITestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('user-list')
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.builder = mommy_recipes.builder.make(connections=[self.company_admin])
        job = mommy_recipes.job.make(
            subdivision__company=company, roles=[self.builder], created_by=company, owner=company)
        self.task = mommy_recipes.task.make(
            job=job, builder=self.builder, start_date=monday, end_date=monday + timedelta(days=2))
        self.task.make_participants()

    @expectedFailure
    def test_active_this_month(self):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        url = reverse('user-active-this-month')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        self.task.participants.update(response=1)  # Participation.RESPONSE_ACCEPTED

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

        # Replace start_date and end_date month
        months_without_current = list(range(1, 13))
        months_without_current.remove(self.task.start_date.month)
        new_month = random.choice(months_without_current)
        data = {
            'start_date': self.task.start_date.replace(month=new_month),
            'duration': 30,
        }

        self.client.patch(reverse('task-detail', args=[self.task.id]), data)  # Update task

        self.task.participants.update(response=1)  # Participation.RESPONSE_ACCEPTED

        # Task not on the same month
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        # Prove month is not the same
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.start_date.month, timezone.now().month)
        self.assertNotEqual(self.task.start_date.month, timezone.now().month)

    @expectedFailure
    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 7)  # plus extras created by model-mommy

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_search(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url + f'?search={self.company_admin.user.get_full_name()}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    # def test_order_by_user_type_asc(self):
    #     self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     response = self.client.get(self.url + '?order_by_user_type=true')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['count'], 6)
    #     self.assertEqual(response.data['results'], UserSerializer([
    #         self.superuser,
    #         self.company_admin.user,
    #         self.task.subcontractor.user,
    #         self.task.job.superintendent.user,
    #         self.task.superintendent.user,
    #         self.builder.user,
    #     ], many=True).data)
    #
    # def test_order_by_user_type_desc(self):
    #     self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     response = self.client.get(self.url + '?order_by_user_type=false')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['count'], 6)
    #     self.assertEqual(response.data['results'], UserSerializer([
    #         self.builder.user,
    #         self.task.superintendent.user,
    #         self.task.job.superintendent.user,
    #         self.task.subcontractor.user,
    #         self.company_admin.user,
    #         self.superuser,
    #     ], many=True).data)

    # def test_calendar_response_default_this_week(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     today = timezone.now().date()
    #     start_date = today - timedelta(days=today.weekday())
    #
    #     response = self.client.get(reverse('calendar-user-list') + '?role=builder')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['start_date'], start_date)
    #     self.assertEqual(response.data['week_number'], start_date.isocalendar()[1])
    #     self.assertEqual(
    #         response.data['users'][1]['participations_weekly'][0]['task'],
    #         CalendarTaskSerializer(self.task).data,
    #     )
    #
    # def test_calendar_search(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     url = reverse('calendar-user-list') + '?role=builder&task-search={}'
    #     participant = self.task.participants.get(user=self.builder.user)
    #
    #     response = self.client.get(reverse('calendar-user-list') + '?role=builder&task-search=random-text')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFalse(response.data['users'][1]['participations_weekly'])
    #
    #     response = self.client.get(url.format(participant.task.name))
    #     self.assertEqual(
    #         response.data['users'][1]['participations_weekly'][0]['task'],
    #         CalendarTaskSerializer(self.task).data,
    #     )
    #
    #     response = self.client.get(url.format(participant.task.job.street_address))
    #     self.assertEqual(
    #         response.data['users'][1]['participations_weekly'][0]['task'],
    #         CalendarTaskSerializer(self.task).data,
    #     )
    #
    #     response = self.client.get(url.format(participant.task.job.subdivision.name))
    #     self.assertEqual(
    #         response.data['users'][1]['participations_weekly'][0]['task'],
    #         CalendarTaskSerializer(self.task).data,
    #     )
    #
    # def test_calendar_response_two_weeks_ago_has_no_data(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     today = timezone.now().date()
    #     start_date = today - timedelta(days=today.weekday())
    #     two_weeks_ago = start_date - timedelta(weeks=2)
    #     week_param = two_weeks_ago.strftime('%G-%V')
    #
    #     response = self.client.get(reverse('calendar-user-list') + '?role=builder&week=' + week_param)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['start_date'], two_weeks_ago)
    #     self.assertEqual(response.data['week_number'], two_weeks_ago.isocalendar()[1])
    #     self.assertEqual(response.data['users'][1]['participations_weekly'], [])

    # def test_create_user(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     data = {
    #         'email': 'test@example.com',
    #         'company_name': 'builder',
    #     }
    #     response = self.client.post(reverse('user-list'), data)
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(response.data['email'], 'test@example.com')
    #
    #     user = User.objects.get(email=response.data['email'])
    #     self.assertEqual(user.roles.count(), 1)
    #     self.assertEqual(user.is_active, True)
    #
    # def test_create_superintendent_without_name(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     data = {
    #         'email': 'test@example.com',
    #         'user_type': 'superintendent',
    #         'company_name': '',
    #     }
    #     response = self.client.post(reverse('user-list'), data)
    #     self.assertEqual(response.status_code, 201)
    #
    # def test_create_builder_with_blank_name(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     data = {
    #         'email': 'test@example.com',
    #         'user_type': 'builder',
    #         'company_name': '',
    #     }
    #     response = self.client.post(reverse('user-list'), data)
    #     self.assertEqual(response.status_code, 400)
    #
    # def test_create_builder_without_name(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     data = {
    #         'email': 'test@example.com',
    #         'user_type': 'builder',
    #     }
    #     response = self.client.post(reverse('user-list'), data)
    #     self.assertEqual(response.status_code, 400)


@freeze_time(monday)
class JobViewSetTestCase(APITestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('job-list')
        self.company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=self.company)
        self.builder = mommy_recipes.builder.make(company=self.company)
        self.subcontractor = mommy_recipes.subcontractor.make(invited_roles=[self.builder])
        self.superintendent = mommy_recipes.superintendent.make(company=self.company)
        self.otheruser = mommy_recipes.user.make()
        self.job_count = 10
        for i in range(self.job_count):
            mommy_recipes.job.make(owner=self.company)
        job = mommy_recipes.job.make(owner=self.company, roles=[self.builder])
        self.task = mommy_recipes.task.make(job=job, start_date=monday, end_date=monday + timedelta(days=2))

    @expectedFailure
    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 11)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 11)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        self.client.login(email=self.subcontractor.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        self.client.login(email=self.superintendent.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        self.client.login(email=self.otheruser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_job_response(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], self.job_count + 1)

    # def test_calendar_response_default_this_week(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     today = timezone.now().date()
    #     start_date = today - timedelta(days=today.weekday())
    #
    #     response = self.client.get(reverse('job-calendar'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['start_date'], start_date)
    #     self.assertEqual(response.data['week_number'], start_date.isocalendar()[1])
    #     self.assertEqual(
    #         response.data['jobs'][0]['tasks_weekly'][0],
    #         CalendarTaskSerializer(self.task).data,
    #     )
    #
    # def test_calendar_search(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     url = reverse('job-calendar') + '?task-search={}'
    #
    #     response = self.client.get(reverse('job-calendar') + '?task-search=random-text')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFalse(response.data['jobs'][0]['tasks_weekly'])
    #
    #     response = self.client.get(url.format(self.task.name))
    #     self.assertEqual(
    #         response.data['jobs'][0]['tasks_weekly'][0],
    #         CalendarTaskSerializer(self.task).data,
    #     )
    #
    #     response = self.client.get(url.format(self.task.job.street_address))
    #     self.assertEqual(
    #         response.data['jobs'][0]['tasks_weekly'][0],
    #         CalendarTaskSerializer(self.task).data,
    #     )
    #
    #     response = self.client.get(url.format(self.task.job.subdivision.name))
    #     self.assertEqual(
    #         response.data['jobs'][0]['tasks_weekly'][0],
    #         CalendarTaskSerializer(self.task).data,
    #     )
    #
    # def test_calendar_response_two_weeks_ago_has_no_data(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     today = timezone.now().date()
    #     start_date = today - timedelta(days=today.weekday())
    #     two_weeks_ago = start_date - timedelta(weeks=2)
    #     week_param = two_weeks_ago.strftime('%G-%V')
    #     response = self.client.get(reverse('job-calendar') + '?week=' + week_param)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['start_date'], two_weeks_ago)
    #     self.assertEqual(response.data['week_number'], two_weeks_ago.isocalendar()[1])
    #     self.assertEqual(response.data['jobs'][0]['tasks_weekly'], [])

    # def test_create_autofills_company(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     builder = mommy_recipes.builder.make()
    #     subdivision = mommy_recipes.subdivision.make(company=builder)
    #     data = {
    #         'street_address': '123 Street',
    #         'city': 'New York',
    #         'state': 'NY',
    #         'zip': '12354',
    #         'lot_number': '23',
    #         'subdivision': subdivision.id,
    #         'superintendent': self.superintendent.id,
    #         'owner': builder.id,
    #     }
    #     response = self.client.post(reverse('job-list'), data)
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(response.data['street_address'], '123 Street')
    #     self.assertEqual(response.data['company'], self.company_admin.company.id)

    def test_create_no_uniqueness_checks(self):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        builder = mommy_recipes.builder.make()
        subdivision = mommy_recipes.subdivision.make(company=builder.company)
        job = models.Job.objects.create(
            street_address='123 Street', city='New York', state='NY', zip='12354', lot_number='23',
            subdivision=subdivision, created_by=self.builder.company, owner=self.builder.company,
            superintendent=self.superintendent, builder=builder, subcontractor=self.subcontractor)
        job.roles.add(self.superintendent, builder)
        data = {
            'street_address': '123 Street',
            'city': 'New York',
            'state': 'NY',
            'zip': '12354',
            'lot_number': '23',
            'subdivision': subdivision.id,
            'superintendent': self.superintendent.id,
            'subcontractor': self.subcontractor.id,
            'created_by': builder.company.id,
            'owner': builder.company.id,
            'builder': builder.id,
        }
        response = self.client.post(reverse('job-list'), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['street_address'], '123 Street')

        job = models.Job.objects.get(id=response.data['id'])
        self.assertEqual(job.notes.count(), 0)

    def test_create_with_note(self):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        builder = mommy_recipes.builder.make()
        subdivision = mommy_recipes.subdivision.make(company=builder.company)
        data = {
            'street_address': '123 Street',
            'city': 'New York',
            'state': 'NY',
            'zip': '12354',
            'lot_number': '23',
            'subdivision': subdivision.id,
            'superintendent': self.superintendent.id,
            'subcontractor': self.subcontractor.id,
            'created_by': builder.company.id,
            'owner': builder.company.id,
            'builder': builder.id,
            'note_text': 'This is a test note.',
        }
        response = self.client.post(reverse('job-list'), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['street_address'], '123 Street')

        job = models.Job.objects.get(id=response.data['id'])
        self.assertEqual(job.notes.get().text, 'This is a test note.')

    def test_update_with_custom_subdivision(self):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        data = {'custom_subdivision': 'Custom'}
        response = self.client.patch(reverse('job-detail', args=[self.task.job.id]), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['subdivision_name'], 'Custom')


@freeze_time(monday)
class TaskViewSetTestCase(APITestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.otheruser = mommy_recipes.user.make()
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.subcontractor = mommy_recipes.subcontractor.make(connections=[self.company_admin])
        self.superintendent = mommy_recipes.superintendent.make(company=company)
        self.builder = mommy_recipes.builder.make(company=company)
        self.url = reverse('task-list')

        date = timezone.now().date()
        nine = time(9)
        five = time(17)
        self.one = mommy_recipes.task.make(
            job__owner=self.company_admin.company,
            job__superintendent=self.superintendent,
            subcontractor=self.subcontractor,
            superintendent=self.superintendent,
            builder=self.builder,
            start_date=date,
            end_date=date + timedelta(days=2),
            start_time=nine,
            end_time=five,
        )
        self.two = mommy_recipes.task.make(
            job__owner=self.company_admin.company,
            start_date=date + timedelta(days=1),
            end_date=date + timedelta(days=3),
            start_time=nine,
            end_time=five,
        )
        self.other = mommy_recipes.task.make(
            start_date=date + timedelta(days=2),
            end_date=date + timedelta(days=4),
            start_time=nine,
            end_time=five,
        )

    def test_accept_participation_reload_calendar(self):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)

        # Move task two days forward
        url = reverse('task-detail', kwargs={'pk': self.one.pk})
        start_date = self.one.start_date + timedelta(days=2)
        end_date = self.one.end_date + timedelta(days=2)
        data = {'start_date': start_date, 'end_date': end_date}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)

        # Send notifications to key participants
        url = reverse('task-send-notification', kwargs={'pk': self.one.pk})
        # No notifications sent yet
        self.assertEqual(AuthToken.objects.count(), 0)
        self.client.put(url)
        self.assertEqual(response.status_code, 200)
        # Notifications sent to three key participants
        self.assertEqual(AuthToken.objects.count(), 3)

        # Test if reload_calendar method is called when a key participant responds "accept" to participation
        url = reverse('task-accept')
        # crew-leader
        with patch('construction.consumers.CalendarConsumer.reload_calendar') as reload_calendar:
            self.assertEqual(self.subcontractor.user.tokens.count(), 1)
            token = self.subcontractor.user.tokens.first().token
            response = self.client.get(url + '?token={}'.format(token))
            reload_calendar.assert_called_once()

        # superintendent
        with patch('construction.consumers.CalendarConsumer.reload_calendar') as reload_calendar:
            self.assertEqual(self.superintendent.user.tokens.count(), 1)
            token = self.superintendent.user.tokens.first().token
            response = self.client.get(url + '?token={}'.format(token))
            reload_calendar.assert_called_once()
        # builder
        with patch('construction.consumers.CalendarConsumer.reload_calendar') as reload_calendar:
            self.assertEqual(self.builder.user.tokens.count(), 1)
            token = self.builder.user.tokens.first().token
            response = self.client.get(url + '?token={}'.format(token))
            reload_calendar.assert_called_once()

    @expectedFailure
    def test_reject_participation_reload_calendar(self):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)

        # Move task two days forward
        url = reverse('task-detail', kwargs={'pk': self.one.pk})
        start_date = self.one.start_date + timedelta(days=2)
        end_date = self.one.end_date + timedelta(days=2)
        data = {'start_date': start_date, 'end_date': end_date}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)

        # Send notifications to key participants
        url = reverse('task-send-notification', kwargs={'pk': self.one.pk})
        # No notifications sent yet
        self.assertEqual(AuthToken.objects.count(), 0)
        self.client.put(url)
        self.assertEqual(response.status_code, 200)
        # Notifications sent to three key participants
        self.assertEqual(AuthToken.objects.count(), 3)

        # Test if reload_calendar method is called when a key participant responds "reject" to participation
        url = reverse('task-reject')
        # crew-leader
        with patch('construction.consumers.CalendarConsumer.reload_calendar') as reload_calendar:
            self.assertEqual(self.subcontractor.user.tokens.count(), 1)
            token = self.subcontractor.user.tokens.first().token
            response = self.client.get(url + '?token={}'.format(token))
            reload_calendar.assert_called_once()

        # superintendent
        with patch('construction.consumers.CalendarConsumer.reload_calendar') as reload_calendar:
            self.assertEqual(self.superintendent.user.tokens.count(), 2)
            token = self.superintendent.user.tokens.first().token
            response = self.client.get(url + '?token={}'.format(token))
            reload_calendar.assert_called_once()
        # builder
        with patch('construction.consumers.CalendarConsumer.reload_calendar') as reload_calendar:
            self.assertEqual(self.builder.user.tokens.count(), 1)
            token = self.builder.user.tokens.first().token
            response = self.client.get(url + '?token={}'.format(token))
            reload_calendar.assert_called_once()

    @expectedFailure
    def test_filtered_queryset(self):
        url = reverse('task-list')

        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

        self.client.login(email=self.superintendent.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        self.client.login(email=self.otheruser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_search(self):
        url = reverse('task-list')
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)

        response = self.client.get(url + f'?search={self.one.job.street_address}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        response = self.client.get(url + f'?search={self.one.subcontractor.user.get_full_name()}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        response = self.client.get(url + f'?search={self.one.superintendent.user.get_full_name()}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        response = self.client.get(url + f'?search={self.one.builder.user.get_full_name()}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        response = self.client.get(url + f'?search={self.one.name}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    # def test_calendar_response_default_this_week(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     today = timezone.now().date()
    #     start_date = today - timedelta(days=today.weekday())
    #
    #     response = self.client.get(reverse('task-calendar'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['start_date'], start_date)
    #     self.assertEqual(response.data['week_number'], start_date.isocalendar()[1])
    #     self.assertEqual(response.data['count'], 2)
    #     self.assertEqual(response.data['results'][0], CalendarTaskSerializer(instance=self.one).data)
    #
    # def test_calendar_response_two_weeks_ago_has_no_data(self):
    #     self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
    #     today = timezone.now().date()
    #     start_date = today - timedelta(days=today.weekday())
    #     two_weeks_ago = start_date - timedelta(weeks=2)
    #     week_param = two_weeks_ago.strftime('%G-%V')
    #
    #     response = self.client.get(reverse('task-calendar') + '?week=' + week_param)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['start_date'], two_weeks_ago)
    #     self.assertEqual(response.data['week_number'], two_weeks_ago.isocalendar()[1])
    #     self.assertEqual(response.data['count'], 0)
    #     self.assertEqual(response.data['results'], [])

    @patch('account.models.AuthToken.send_message')
    def test_update_with_start_and_end(self, _):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        duration = 7
        new_start = self.one.start_date + timedelta(days=duration)
        new_end = self.one.end_date + timedelta(days=duration)

        data = {'start_date': new_start, 'end_date': new_end}
        response = self.client.patch(reverse('task-detail', args=[self.one.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['start_date'], str(new_start))
        self.assertEqual(response.data['end_date'], str(new_end))
        self.assertEqual(response.data['job'], self.one.job.id)

    @expectedFailure
    @patch('account.models.AuthToken.send_message')
    def test_change_schedule_status_to_pending(self, _):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        participants = self.one.make_participants()
        for participant in participants:
            participant.response = participant.RESPONSE_ACCEPTED
            participant.save()
        self.one.sync_status()
        self.assertEqual(self.one.status, self.one.STATUS_SCHEDULED)
        duration = 7
        new_start = self.one.start_date + timedelta(days=duration)
        new_end = self.one.end_date + timedelta(days=duration)

        data = {'start_date': new_start, 'duration': duration}
        response = self.client.patch(reverse('task-detail', args=[self.one.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['start_date'], str(new_start))
        self.assertEqual(response.data['end_date'], str(new_end))
        self.assertEqual(response.data['status'], self.one.STATUS_PENDING)
        self.assertEqual(response.data['participant_statuses'][0]['status'], 'pending')
        self.assertEqual(response.data['participant_statuses'][1]['status'], 'pending')
        self.assertEqual(response.data['participant_statuses'][2]['status'], 'pending')

    @expectedFailure
    @patch('account.models.AuthToken.send_message')
    def test_update_with_start_and_duration(self, _):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        duration = 7
        new_start = self.one.start_date + timedelta(days=duration)
        new_end = self.one.end_date + timedelta(days=duration)

        data = {'start_date': new_start, 'duration': 2}
        response = self.client.patch(reverse('task-detail', args=[self.one.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['start_date'], str(new_start))
        self.assertEqual(response.data['end_date'], str(new_end))
        self.assertEqual(response.data['job'], self.one.job.id)

    @expectedFailure
    @patch('account.models.AuthToken.send_message')
    def test_update_with_duration_only(self, _):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        duration = 7
        new_end = self.one.end_date + timedelta(days=duration)

        data = {'duration': duration + 2}  # 2 is the original distance between start and end
        response = self.client.patch(reverse('task-detail', args=[self.one.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['start_date'], str(self.one.start_date))
        self.assertEqual(response.data['end_date'], str(new_end))
        self.assertEqual(response.data['job'], self.one.job.id)

    @patch('account.models.AuthToken.send_message')
    def test_create(self, _):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        duration = 7
        new_start = self.one.start_date + timedelta(days=duration)
        new_end = self.one.end_date + timedelta(days=duration)
        builder = mommy_recipes.builder.make()
        job = mommy_recipes.job.make()
        data = {
            'name': 'Builder',
            'email': 'test@example.com',
            'builder': builder.id,
            'start_date': new_start,
            'end_date': new_end,
            'job': job.id,
            'subcontractor': self.subcontractor.id,
            'superintendent': self.superintendent.id,
        }
        response = self.client.post(reverse('task-list'), data)
        self.client.force_authenticate(user=self.company_admin.user)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Builder')

        task = models.Task.objects.get(name=response.data['name'])
        self.assertEqual(task.participants.count(), 3)
        self.assertEqual(task.notes.count(), 0)

    @patch('account.models.AuthToken.send_message')
    def test_create_with_note(self, _):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        duration = 7
        new_start = self.one.start_date + timedelta(days=duration)
        new_end = self.one.end_date + timedelta(days=duration)
        builder = mommy_recipes.builder.make()
        job = mommy_recipes.job.make()
        data = {
            'name': 'Tasky',
            'email': 'test@example.com',
            'builder': builder.id,
            'start_date': new_start,
            'end_date': new_end,
            'job': job.id,
            'note_text': 'This is a test note.',
        }
        response = self.client.post(reverse('task-list'), data)
        self.client.force_authenticate(user=self.company_admin.user)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Tasky')

        task = models.Task.objects.get(id=response.data['id'])
        self.assertEqual(task.notes.get().text, 'This is a test note.')

    @patch('account.models.AuthToken.send_message')
    def test_update_with_custom_category_and_custom_subcategory(self, _):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        data = {'custom_category': 'Cat', 'custom_subcategory': 'Sub'}
        response = self.client.patch(reverse('task-detail', args=[self.one.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['category_name'], 'Cat')
        self.assertEqual(response.data['subcategory_name'], 'Sub')
        subcategory = models.TaskSubCategory.objects.get(id=response.data['subcategory'])
        self.assertEqual(subcategory.category_id, response.data['category'])

    @patch('account.models.AuthToken.send_message')
    def test_update_with_category_and_custom_subcategory(self, _):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        data = {
            'name': self.one.name,
            'builder': self.one.builder.id,
            'start_date': self.one.start_date,
            'end_date': self.one.end_date,
            'job': self.one.job.id,
            'category': self.one.category.pk,
            'custom_subcategory': 'Sub'
        }
        response = self.client.put(reverse('task-detail', args=[self.one.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['category_name'], self.one.category.name)
        self.assertEqual(response.data['subcategory_name'], 'Sub')
        subcategory = models.TaskSubCategory.objects.get(id=response.data['subcategory'])
        self.assertEqual(subcategory.category_id, response.data['category'])

    @patch('account.models.AuthToken.send_message')
    def test_failing_update_with_subcategory_but_no_category(self, _):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        data = {
            'name': self.one.name,
            'builder': self.one.builder.id,
            'start_date': self.one.start_date,
            'end_date': self.one.end_date,
            'job': self.one.job.id,
            'custom_subcategory': 'Sub'
        }
        response = self.client.put(reverse('task-detail', args=[self.one.pk]), data)
        self.assertEqual(response.status_code, 400)

    @patch('account.models.AuthToken.send_message')
    def test_cannot_update_with_non_admin_staff(self, _):
        self.client.login(email=self.subcontractor.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.patch(reverse('task-detail', args=[self.one.pk]), {'name': 'NEW NAME'})
        self.assertEqual(response.status_code, 403)
        data = {
            'name': 'NEW NAME',
            'builder': self.one.builder.id,
            'start_date': self.one.start_date,
            'end_date': self.one.end_date,
            'job': self.one.job.id,
            'category': self.one.category.pk,
            'subcategory': self.one.subcategory.pk,
        }
        response = self.client.put(reverse('task-detail', args=[self.one.pk]), data)
        self.assertEqual(response.status_code, 403)


class CompanyViewSetTestCase(TestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('company-list')
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.subcontractor = mommy_recipes.subcontractor.make(connections=[self.company_admin])
        self.company_count = 10
        for i in range(self.company_count):
            mommy_recipes.contractor.make()

    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 12)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        self.client.login(email=self.subcontractor.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_company_response(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], self.company_count + 2)


class CompanyRoleViewSetTestCase(TestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('company-role-list')
        company = mommy_recipes.contractor.make()
        self.otheruser = mommy_recipes.user.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.superintendent = mommy_recipes.superintendent.make(company=company)
        self.subcontractor = mommy_recipes.subcontractor.make(connections=[self.company_admin])
        self.company_admin_count = 10
        for i in range(self.company_admin_count):
            mommy_recipes.contractor_admin.make()

    def test_filtered_queryset(self):
        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

        self.client.login(email=self.superintendent.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

        self.client.login(email=self.subcontractor.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)


class SubdivisionViewSetTestCase(TestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('subdivision-list')
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.builder = mommy_recipes.builder.make(connections=[self.company_admin])
        mommy_recipes.subdivision.make(company=self.company_admin.company)
        self.subdivision_count = 10
        for i in range(self.subdivision_count):
            mommy_recipes.subdivision.make()

    def test_subdivision_response(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], self.subdivision_count + 1)

    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 11)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)


class TaskCategoryViewSetTestCase(TestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('task_category-list')
        self.category_count = 50
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.builder = mommy_recipes.builder.make(connections=[self.company_admin])

        for i in range(self.category_count):
            models.TaskCategory.objects.create(contractor=company, name=f"Category {i}")

    def test_taskcategory_response(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], self.category_count)

        for category in response.data['results']:
            self.assertRegex(category['name'], "Category [0-9]+")

    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)


class TaskSubCategoryViewSetTestCase(TestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('task_subcategory-list')
        self.category_count = 5
        self.subcategory_count = 50
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.builder = mommy_recipes.builder.make(connections=[self.company_admin])

        for i in range(self.category_count):
            category = models.TaskCategory.objects.create(contractor=company, name=f"Category {i}")
            for j in range(self.subcategory_count):
                models.TaskSubCategory.objects.create(name=f"Subcategory {i}-{j}", category=category)

    def test_tasksubcategory_response(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], self.subcategory_count * self.category_count)

        for category in response.data['results']:
            self.assertRegex(category['name'], "Subcategory [0-9]+-[0-9]+")
            self.assertRegex(category['category_name'], "Category [0-9]+")
            category_re = re.compile(r".+ (?P<category>[0-9]+)")
            subcategory_re = re.compile(r".+ (?P<category>[0-9]+)-(?P<subcategory>[0-9]+)")
            category_match = category_re.search(category['category_name'])
            subcategory_match = subcategory_re.search(category['name'])
            self.assertEqual(category_match.group('category'), subcategory_match.group('category'))

    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 250)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 250)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)


class ParticipationViewSetTestCase(TestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('participation-list')
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.builder = mommy_recipes.builder.make(connections=[self.company_admin])
        task = mommy_recipes.task.make(job__owner=company)
        self.participation_count = 50
        mommy_recipes.participation.make(_quantity=self.participation_count, task=task)

    def test_participation_response(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], self.participation_count)

    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)


class ContactViewSetTestCase(TestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('contact-list')
        self.contact_count = 50
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.builder = mommy_recipes.builder.make(connections=[self.company_admin])
        job = mommy_recipes.job.make(owner=company)
        mommy_recipes.contact.make(_quantity=self.contact_count, job=job)

    def test_contact_response(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], self.contact_count)

    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)


class NoteViewSetTestCase(TestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('note-list')
        self.note_count = 50
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.builder = mommy_recipes.builder.make(connections=[self.company_admin])
        job = mommy_recipes.job.make(owner=company)
        mommy_recipes.note.make(_quantity=self.note_count, job=job)

    def test_note_response(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], self.note_count)

    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)


class DocumentViewSetTestCase(TestCase, ProtectedViewMixIn):
    def setUp(self):
        ProtectedViewMixIn.setUp(self)
        self.url = reverse('document-list')
        self.document_count = 50
        company = mommy_recipes.contractor.make()
        self.company_admin = mommy_recipes.contractor_admin.make(company=company)
        self.builder = mommy_recipes.builder.make(connections=[self.company_admin])
        job = mommy_recipes.job.make(owner=company)
        mommy_recipes.document.make(_quantity=self.document_count, job=job)

    def test_document_response(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], self.document_count)

    def test_filtered_queryset(self):
        self.client.login(email=self.superuser.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.company_admin.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 50)

        self.client.login(email=self.builder.user.email, password=mommy_recipes.SEEDER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
