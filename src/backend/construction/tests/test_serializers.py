import os
from datetime import date, time, timedelta
from unittest import expectedFailure

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from freezegun import freeze_time

from cbcommon import mommy_recipes

from .. import models, serializers

UserModel = get_user_model()
midnight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
monday = midnight - timedelta(days=midnight.weekday()) + timedelta(days=1)


class CompanySerializerTestCase(TestCase):
    @expectedFailure
    def test_fields(self):
        nine = time(9)
        five = time(17)
        company = models.Company.objects.create(
            name='Test Company', start_of_day=nine, end_of_day=five)
        expected_data = {
            'id': company.id,
            'name': 'Test Company',
            'billing_address': '',
            'address_line_2': '',
            'city': '',
            'state': '',
            'zip': '',
            'start_of_day': str(nine),
            'end_of_day': str(five),
            'reminder_time': '00:00:00',
            'monday': True,
            'tuesday': True,
            'wednesday': True,
            'thursday': True,
            'friday': True,
            'saturday': False,
            'sunday': False,
            'type': models.Company.TYPE_CONTRACTOR,
            'type_display': company.get_type_display(),
            'users': [],
            'current_plan': models.Company.PLAN_FREE,
            'current_balance': '0.00',
            'scheduling_options': None
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.CompanySerializer(instance=company).data, expected_data)


class CompanyRoleSerializerTestCase(TestCase):
    @expectedFailure
    def test_fields(self):
        user = UserModel.objects.create_user(email='test@example.com', password='password')
        company = models.Company.objects.create(name='Test Company')
        role = models.CompanyRole.objects.create(user=user, company=company, is_admin=True)
        expected_data = {
            'id': role.id,
            'user_types_display': 'Admin',
            'user': serializers.UserSerializer(instance=user).data,
            'company': company.id,
            'company_name': 'Test Company',
            'company_type': company.get_type_display(),
            'company_reminder_time': '00:00:00',
            'is_active': True,
            'is_employed': True,
            'is_admin': True,
            'is_builder': False,
            'is_crew_leader': False,
            'is_superintendent': False,
            'is_contact': False,
            'default_calendar_filter': 1,
            'page_size': 20,
            'crew_leader': None,
            'connections': [],
            'user_enable_text_notifications': role.user.enable_text_notifications,
            'user_enable_email_notifications': role.user.enable_email_notifications,
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.CompanyRoleSerializer(instance=role).data, expected_data)


class SubdivisionSerializerTestCase(TestCase):
    def test_fields(self):
        builder = models.Company.objects.create(name='Builder')
        subdivision = models.Subdivision.objects.create(company=builder, name="Some Subdivision")
        expected_data = {
            'id': subdivision.id,
            'name': "Some Subdivision",
            'company': serializers.CompanySerializer(subdivision.company).data,
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.SubdivisionSerializer(instance=subdivision).data, expected_data)


class NoteTimelineSerializerTestCase(TestCase):
    def test_fields(self):
        task = mommy_recipes.task.make()
        note = mommy_recipes.note.make(task=task)
        expected_data = {
            "id": note.id,
            "created_timestamp": note.created_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "modified_timestamp": note.modified_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "author": serializers.UserSerializer(instance=note.author).data,
            "job": None,
            "task": task.id,
            "text": note.text,
            "text_es": note.text_es,
            "orig_is_en": note.orig_is_en,
            "note_type": "Task"
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.NoteTimelineSerializer(instance=note).data, expected_data)


class JobSerializerTestCase(TestCase):
    @expectedFailure
    def test_fields(self):
        job = mommy_recipes.job.make()

        expected_data = {
            'id': job.id,
            'owner_non_working_days_in_day_of_week': job.owner_non_working_days_in_day_of_week,
            'street_address': job.street_address,
            'city': job.city,
            'state': job.state,
            'zip': job.zip,
            'lot_number': job.lot_number,
            'subdivision': job.subdivision.id,
            'created_by': job.created_by.id,
            'owner': job.owner.id,
            'builder': job.builder.id,
            'subcontractor': job.subcontractor.id,
            'superintendent': job.superintendent.id,
            'date_added': str(date.today()),
            'is_archived': job.is_archived,
            'subdivision_name': job.subdivision.name,
            'created_by_name': job.created_by.name,
            'owner_name': job.owner.name,
            'builder_name': job.builder.user.get_full_name(),
            'subcontractor_name': job.subcontractor.user.get_full_name(),
            'superintendent_name': job.superintendent.user.get_full_name(),
            'builder_data': serializers.CompanyRoleSerializer(instance=job.builder).data,
            'subcontractor_data': serializers.CompanyRoleSerializer(instance=job.subcontractor).data,
            'superintendent_data': serializers.CompanyRoleSerializer(instance=job.superintendent).data,
            'roles': serializers.CompanyRoleSerializer(instance=job.roles, many=True).data,
            'contacts': serializers.NestedContactSerializer(instance=job.contacts.all(), many=True).data,
            'notes': serializers.NoteTimelineSerializer(instance=job.notes.all(), many=True).data,
            'documents': serializers.NestedDocumentSerializer(instance=job.documents.all(), many=True).data,
            'location': job.location,
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.JobSerializer(instance=job).data, expected_data)


class TaskSerializerTestCase(TestCase):
    @expectedFailure
    def test_fields(self):
        task = mommy_recipes.task.make()
        task.make_participants()
        task.participants.filter(user=task.builder.user).update(response=models.Participation.RESPONSE_NOT_APPLICABLE)
        task.participants.filter(user=task.subcontractor.user).update(response=models.Participation.RESPONSE_ACCEPTED)
        task.participants.filter(user=task.superintendent.user).delete()

        expected_data = {
            'id': task.id,
            'job_is_archived': task.job.is_archived,
            'start_date': str(task.start_date),
            'end_date': str(task.end_date),
            'start_time': str(task.start_time),
            'end_time': str(task.end_time),
            'between': str(task.between),
            'status': task.status,
            'is_completed': task.is_completed,
            'name': task.name,
            'category': task.category.id,
            'subcategory': task.subcategory.id,
            'job': task.job.id,
            'author': task.author,
            'subcontractor': task.subcontractor.id,
            'superintendent': task.superintendent.id,
            'builder': task.builder.id,
            'category_name': task.category.name,
            'subcategory_name': task.subcategory.name,
            'job_data': serializers.JobSerializer(instance=task.job).data,
            'job_location': task.job.location,
            'job_address': task.job.street_address,
            'subcontractor_data': serializers.CompanyRoleSerializer(instance=task.subcontractor).data,
            'superintendent_data': serializers.CompanyRoleSerializer(instance=task.superintendent).data,
            'builder_data': serializers.CompanyRoleSerializer(instance=task.builder).data,
            'subcontractor_name': task.subcontractor.user.get_full_name(),
            'superintendent_name': task.superintendent.user.get_full_name(),
            'builder_name': task.builder.user.get_full_name(),
            'participants': serializers.TaskParticipationSerializer(instance=task.participants.all(), many=True).data,
            'contacts': serializers.NestedContactSerializer(instance=task.contacts.all(), many=True).data,
            'all_contacts': serializers.NestedContactSerializer(instance=task.all_contacts.all(), many=True).data,
            'notes': serializers.NoteTimelineSerializer(instance=task.notes.all(), many=True).data,
            'all_notes': serializers.NoteTimelineSerializer(instance=task.all_notes.all(), many=True).data,
            'documents': serializers.NestedDocumentSerializer(instance=task.documents.all(), many=True).data,
            'reminders': serializers.ReminderSerializer(instance=task.reminders.all(), many=True).data,
            'duration': None,
            'status_display': task.get_status_display(),
            'participant_statuses': [
                {
                    'label': 'B',
                    'status': 'not-applicable',
                    'participation_id': task.participants.filter(user=task.builder.user)[0].id,
                },
                {
                    'label': 'SC',
                    'status': 'accepted',
                    'participation_id': task.participants.filter(user=task.subcontractor.user)[0].id,
                },
                {'label': 'CR', 'status': 'default', 'participation_id': None},
            ],
            'has_queued_notification': task.has_queued_notification,
            'author_display': None,
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.TaskSerializer(instance=task).data, expected_data)


class TaskCategorySerializerTestCase(TestCase):
    def test_fields(self):
        contractor = mommy_recipes.contractor.make()
        task_category = models.TaskCategory.objects.create(contractor=contractor, name="Some Category")
        expected_data = {
            "id": task_category.id,
            "name": "Some Category",
            "contractor": contractor.id,
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.TaskCategorySerializer(instance=task_category).data, expected_data)


class TaskSubCategorySerializerTestCase(TestCase):
    def test_fields(self):
        contractor = mommy_recipes.contractor.make()
        task_category = models.TaskCategory.objects.create(contractor=contractor, name="Some Category")
        task_subcategory = models.TaskSubCategory.objects.create(category=task_category, name="Some Sub Category")
        expected_data = {
            "id": task_subcategory.id,
            "name": "Some Sub Category",
            "category": task_category.id,
            "category_name": "Some Category",
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.TaskSubCategorySerializer(instance=task_subcategory).data, expected_data)


class ParticipationSerializerTestCase(TestCase):
    def test_fields(self):
        superintendent = mommy_recipes.superintendent.make()
        task = mommy_recipes.task.make()
        now = timezone.now()
        participation = models.Participation.objects.create(
            response=models.Participation.RESPONSE_ACCEPTED,
            contact_flag=True,
            invited_timestamp=now,
            response_timestamp=now,
            user=superintendent.user,
            task=task
        )
        expected_data = {
            'id': participation.id,
            'response': models.Participation.RESPONSE_ACCEPTED,
            'contact_flag': True,
            'invited_timestamp': now.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'response_timestamp': now.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'user': superintendent.user.id,
            'task': task.id,
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.ParticipationSerializer(instance=participation).data, expected_data)


class ContactSerializerTestCase(TestCase):
    def test_fields(self):
        job = mommy_recipes.job.make()
        contact = mommy_recipes.contact.make(job=job)
        expected_data = {
            "id": contact.id,
            "created_timestamp": contact.created_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "modified_timestamp": contact.modified_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "author_data": serializers.UserSerializer(instance=contact.author).data,
            "job_data": serializers.JobSerializer(instance=contact.job).data,
            "task_data": None,
            "author": contact.author.id,
            "job": contact.job.id,
            "task": None,
            "name": contact.name,
            "note": contact.note,
            "email": contact.email,
            "mobile_number": contact.mobile_number,
            "contact_type": "Job",
            "enable_text_notifications": False,
            "enable_email_notifications": False,
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.ContactSerializer(instance=contact).data, expected_data)


class NoteSerializerTestCase(TestCase):
    def test_fields(self):
        job = mommy_recipes.job.make()
        note = mommy_recipes.note.make(job=job)
        expected_data = {
            "id": note.id,
            "created_timestamp": note.created_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "modified_timestamp": note.modified_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "author_data": serializers.UserSerializer(instance=note.author).data,
            "job_data": serializers.JobSerializer(instance=note.job).data,
            "task_data": None,
            "author": note.author.id,
            "job": note.job.id,
            "task": None,
            "text": note.text,
            "text_es": note.text_es,
            "orig_is_en": note.orig_is_en,
            "note_type": "Job"
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.NoteSerializer(instance=note).data, expected_data)


class NestedDocumentSerializerTestCase(TestCase):
    def test_fields(self):
        task = mommy_recipes.task.make()
        document = mommy_recipes.document.make(task=task)
        expected_data = {
            "id": document.id,
            "created_timestamp": document.created_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "modified_timestamp": document.modified_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "author": document.author.id,
            "task": document.task.id,
            "job": None,
            "filename": os.path.join(settings.MEDIA_URL, document.filename.name),
            "file_type": 'TXT',
            "file_name": document.file_name
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.NestedDocumentSerializer(instance=document).data, expected_data)


class DocumentSerializerTestCase(TestCase):
    def test_fields(self):
        task = mommy_recipes.task.make()
        document = mommy_recipes.document.make(task=task)
        expected_data = {
            "id": document.id,
            "created_timestamp": document.created_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "modified_timestamp": document.modified_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "author": document.author.id,
            "job": None,
            "task": document.task.id,
            "filename": os.path.join(settings.MEDIA_URL, document.filename.name)
        }
        self.maxDiff = None
        self.assertDictEqual(serializers.DocumentSerializer(instance=document).data, expected_data)


# @freeze_time(monday)
# class CalendarUserListSerializerTestCase(TestCase):
#     def test_fields(self):
#         builder = mommy_recipes.builder_admin.make()
#         task_one = mommy_recipes.task.make(
#             builder=builder, subcontractor=None, superintendent=None,
#             start_date=monday, end_date=monday + timedelta(days=2),
#         )
#         task_one.make_participants()
#         one = task_one.participants.get()
#         task_two = mommy_recipes.task.make(
#             builder=builder, subcontractor=None, superintendent=None,
#             start_date=monday + timedelta(days=2), end_date=monday + timedelta(days=4),
#         )
#         task_two.make_participants()
#         two = task_two.participants.get()
#
#         expected_data = {
#             'id': builder.user.id,
#             'email': builder.user.email,
#             'mobile_number': builder.user.mobile_number,
#             'first_name': builder.user.first_name,
#             'last_name': builder.user.last_name,
#             'is_active': builder.user.is_active,
#             'participations_weekly': serializers.CalendarParticipationSerializer([one, two], many=True).data,
#             'role_id': builder.id,
#         }
#         self.maxDiff = None
#         self.assertDictEqual(serializers.CalendarUserListSerializer(instance=builder, context={
#             'start_date': monday,
#             'end_date': monday + timedelta(days=7),
#             'task_search': None,
#             'task_status': None,
#             'role': 'builder',
#         }).data, expected_data)
#
#
# @freeze_time(monday)
# class CalendarJobListSerializerTestCase(TestCase):
#     def test_fields(self):
#         job = mommy_recipes.job.make()
#         one = mommy_recipes.task.make(
#             job=job, subcontractor=None, superintendent=None, builder=None,
#             start_date=monday, end_date=monday + timedelta(days=2),
#         )
#         two = mommy_recipes.task.make(
#             job=job, subcontractor=None, superintendent=None, builder=None,
#             start_date=monday + timedelta(days=2), end_date=monday + timedelta(days=4),
#         )
#
#         expected_data = {
#             'id': job.id,
#             'street_address': job.street_address,
#             'city': job.city,
#             'state': job.state,
#             'zip': job.zip,
#             'lot_number': job.lot_number,
#             'subdivision': job.subdivision.id,
#             'owner': job.owner.id,
#             'superintendent': job.superintendent.id,
#             'date_added': str(date.today()),
#             'subdivision_name': job.subdivision.name,
#             'owner_name': job.owner.name,
#             'builder_name': job.builder.user.get_full_name(),
#             'location': job.location,
#             'tasks_weekly': serializers.CalendarTaskSerializer([one, two], many=True).data,
#         }
#         self.maxDiff = None
#         self.assertDictEqual(serializers.CalendarJobListSerializer(instance=job, context={
#             'start_date': monday,
#             'end_date': monday + timedelta(days=7),
#             'task_search': None,
#             'task_status': None,
#         }).data, expected_data)
