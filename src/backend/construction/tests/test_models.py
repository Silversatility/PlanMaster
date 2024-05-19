from datetime import time, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone

from cbcommon import mommy_recipes

from .. import models

UserModel = get_user_model()


class CompanyModelTestCase(TestCase):

    def test_create_stores_data(self):
        nine = time(9)
        five = time(17)
        company = models.Company.objects.create(name='Test Company', start_of_day=nine, end_of_day=five)

        company.refresh_from_db()
        self.assertEqual(company.name, 'Test Company')
        self.assertEqual(company.start_of_day, nine)
        self.assertEqual(company.end_of_day, five)

    def test_required_fields(self):
        nine = time(9)
        five = time(17)
        with self.assertRaises(ValidationError):
            models.Company.objects.create(start_of_day=nine, end_of_day=five)


class CompanyRoleModelTestCase(TestCase):

    def test_create_stores_data(self):
        user = mommy_recipes.user.make()
        company = models.Company.objects.create(name='Test Company')
        subcontractor = models.CompanyRole.objects.create(user=user, company=company, is_admin=True)
        company.refresh_from_db()
        self.assertEqual(subcontractor.is_admin, True)
        self.assertEqual(subcontractor.user, user)
        self.assertEqual(user.roles.count(), 1)

    def test_required_fields(self):
        company = models.Company.objects.create(name='Test Company')
        with self.assertRaises(ValidationError):
            models.CompanyRole.objects.create(company=company)


class SubdivisionModelTestCase(TestCase):

    def test_create_stores_data(self):
        company = mommy_recipes.contractor.make()
        subdivision = models.Subdivision.objects.create(name='Subdivision', company=company)
        subdivision.refresh_from_db()
        self.assertEqual(subdivision.name, 'Subdivision')
        self.assertEqual(subdivision.company, company)

    def test_required_fields(self):
        company = mommy_recipes.contractor.make()
        with self.assertRaises(ValidationError):
            models.Subdivision.objects.create(name='Subdivision')
        with self.assertRaises(ValidationError):
            models.Subdivision.objects.create(company=company)


class JobModelTestCase(TestCase):

    def test_create_stores_data(self):
        company = mommy_recipes.contractor.make()
        builder = mommy_recipes.builder.make()
        subcontractor = mommy_recipes.subcontractor.make()
        superintendent = mommy_recipes.superintendent.make(company=company)
        subdivision = mommy_recipes.subdivision.make(company=company)
        job = models.Job.objects.create(
            street_address='123 Test St',
            city='Testopia',
            state='NY',
            zip='90210',
            lot_number='B-2',
            subdivision=subdivision,
            created_by=company,
            owner=company,
            builder=builder,
            subcontractor=subcontractor,
            superintendent=superintendent,
        )
        job.refresh_from_db()
        self.assertEqual(job.street_address, '123 Test St')
        self.assertEqual(job.city, 'Testopia')
        self.assertEqual(job.state, 'NY')
        self.assertEqual(job.zip, '90210')
        self.assertEqual(job.lot_number, 'B-2')
        self.assertEqual(job.subdivision, subdivision)
        self.assertEqual(job.created_by, company)
        self.assertEqual(job.owner, company)
        self.assertEqual(job.builder, builder)
        self.assertEqual(job.subcontractor, subcontractor)
        self.assertEqual(job.superintendent, superintendent)

    def test_minimal_data(self):
        company = mommy_recipes.contractor.make()
        builder = mommy_recipes.builder.make()
        job = models.Job.objects.create(
            street_address='123 Test St',
            city='Testopia',
            state='NY',
            zip='90210',
            created_by=company,
            builder=builder,
        )
        self.assertTrue(job.id)

    def test_required_fields(self):
        with self.assertRaises(ValidationError):
            models.Job.objects.create(city='Testopia', state='NY', zip='90210')
        with self.assertRaises(ValidationError):
            models.Job.objects.create(
                street_address='123 Test St', state='NY', zip='90210')
        with self.assertRaises(ValidationError):
            models.Job.objects.create(
                street_address='123 Test St', city='Testopia', zip='90210')
        with self.assertRaises(ValidationError):
            models.Job.objects.create(
                street_address='123 Test St', city='Testopia', state='NY')

    def test_state_and_zip_format(self):
        with self.assertRaises(ValidationError):
            models.Job.objects.create(city='Testopia', state='Wrong State', zip='90210')
        with self.assertRaises(ValidationError):
            models.Job.objects.create(city='Testopia', state='NY', zip='1234579')


class TaskCategoryModelTestCase(TestCase):

    def test_create_stores_data(self):
        company = mommy_recipes.contractor.make()
        category = models.TaskCategory.objects.create(contractor=company, name='Test Category 1')
        category.refresh_from_db()
        self.assertEqual(category.contractor, company)
        self.assertEqual(category.name, 'Test Category 1')

    def test_required_fields(self):
        company = mommy_recipes.contractor.make()
        with self.assertRaises(ValidationError):
            models.TaskCategory.objects.create(contractor=company)
        with self.assertRaises(ValidationError):
            models.TaskCategory.objects.create(name='Test Category 1')


class TaskSubCategoryModelTestCase(TestCase):

    def test_create_stores_data(self):
        category = mommy_recipes.category.make()
        subcategory = models.TaskSubCategory.objects.create(category=category, name='Test Subcategory 1-1')
        subcategory.refresh_from_db()
        self.assertEqual(subcategory.category, category)
        self.assertEqual(subcategory.name, 'Test Subcategory 1-1')

    def test_required_fields(self):
        category = mommy_recipes.category.make()
        with self.assertRaises(ValidationError):
            models.TaskSubCategory.objects.create(category=category)
        with self.assertRaises(ValidationError):
            models.TaskSubCategory.objects.create(name='Test Subcategory 1-1')


class TaskModelTestCase(TestCase):

    def test_create_stores_data(self):
        category = mommy_recipes.category.make()
        subcategory = mommy_recipes.subcategory.make()
        job = mommy_recipes.job.make()
        subcontractor = mommy_recipes.subcontractor.make()
        superintendent = mommy_recipes.superintendent.make()
        builder = mommy_recipes.builder.make()
        today = timezone.now().date()
        later = today + timedelta(days=30)
        nine = time(9)
        five = time(17)
        task = models.Task.objects.create(
            name='Somename',
            category=category,
            subcategory=subcategory,
            job=job,
            subcontractor=subcontractor,
            superintendent=superintendent,
            builder=builder,
            start_date=today,
            end_date=later,
            start_time=nine,
            end_time=five,
            status=models.Task.STATUS_TENTATIVE,
        )
        task.refresh_from_db()
        self.assertEqual(task.name, 'Somename')
        self.assertEqual(task.category, category)
        self.assertEqual(task.subcategory, subcategory)
        self.assertEqual(task.job, job)
        self.assertEqual(task.subcontractor, subcontractor)
        self.assertEqual(task.superintendent, superintendent)
        self.assertEqual(task.builder, builder)
        self.assertEqual(task.start_date, today)
        self.assertEqual(task.end_date, later)
        self.assertEqual(task.start_time, nine)
        self.assertEqual(task.end_time, five)
        self.assertEqual(task.status, models.Task.STATUS_TENTATIVE)

    def test_minimal_data(self):
        job = mommy_recipes.job.make()
        task = models.Task.objects.create(job=job, name='Somename', status=models.Task.STATUS_TENTATIVE)
        self.assertTrue(task.id)

    def test_required_fields(self):
        job = mommy_recipes.job.make()
        with self.assertRaises(ValidationError):
            models.Task.objects.create(job=job)
        with self.assertRaises(ValidationError):
            models.Task.objects.create(name='Somename')

    def test_make_participants(self):
        job = mommy_recipes.job.make()
        subcontractor = mommy_recipes.subcontractor.make()
        superintendent = mommy_recipes.superintendent.make()
        builder = mommy_recipes.builder.make()
        task = models.Task.objects.create(
            job=job,  name='Somename', subcontractor=subcontractor, superintendent=superintendent, builder=builder)
        task.make_participants()
        self.assertEqual(task.participants.count(), 3)
        self.assertTrue(task.participants.filter(user=subcontractor.user).exists())
        self.assertTrue(task.participants.filter(user=superintendent.user).exists())
        self.assertTrue(task.participants.filter(user=builder.user).exists())

    def test_make_participants_twice_doesnt_duplicate(self):
        job = mommy_recipes.job.make()
        subcontractor = mommy_recipes.subcontractor.make()
        superintendent = mommy_recipes.superintendent.make()
        builder = mommy_recipes.builder.make()
        task = models.Task.objects.create(
            job=job,  name='Somename', subcontractor=subcontractor, superintendent=superintendent, builder=builder)
        self.assertEqual(task.participants.count(), 0)
        task.make_participants()
        self.assertEqual(task.participants.count(), 3)
        task.make_participants()
        self.assertEqual(task.participants.count(), 3)

    def task_sync_status_rules(self):
        job = mommy_recipes.job.make()
        task = models.Task.objects.create(job=job, name='Somename', status=models.Task.STATUS_TENTATIVE)
        task.sync_status()
        self.assertEqual(task.status, task.STATUS_TENTATIVE)

        task.subcontractor = mommy_recipes.subcontractor.make()
        participation = task.make_participants()[0]
        self.assertEqual(task.status, task.STATUS_PENDING)

        participation.response = participation.RESPONSE_ACCEPTED
        participation.save()
        self.assertEqual(task.status, task.STATUS_SCHEDULED)

        participation.response = participation.RESPONSE_REJECTED
        participation.save()
        self.assertEqual(task.status, task.STATUS_TENTATIVE)


class ParticipationModelTestCase(TestCase):

    def test_create_stores_data(self):
        user = mommy_recipes.user.make()
        task = mommy_recipes.task.make()
        now = timezone.now()
        participation = models.Participation.objects.create(
            response=models.Participation.RESPONSE_ACCEPTED,
            contact_flag=True,
            task=task,
            invited_timestamp=now,
            response_timestamp=now,
            user=user,
        )
        self.assertEqual(participation.response, models.Participation.RESPONSE_ACCEPTED)
        self.assertEqual(participation.contact_flag, True)
        self.assertEqual(participation.task, task)
        self.assertEqual(participation.invited_timestamp, now)
        self.assertEqual(participation.response_timestamp, now)
        self.assertEqual(participation.user, user)

    def test_minimal_data(self):
        user = mommy_recipes.user.make()
        task = mommy_recipes.task.make()
        now = timezone.now()
        participation = models.Participation.objects.create(
            response=models.Participation.RESPONSE_ACCEPTED,
            contact_flag=True,
            task=task,
            invited_timestamp=now,
            user=user,
        )
        self.assertTrue(participation.id)

    def test_required_fields(self):
        user = mommy_recipes.user.make()
        task = mommy_recipes.task.make()
        response = models.Participation.RESPONSE_ACCEPTED
        now = timezone.now()
        with self.assertRaises(ValidationError):
            models.Participation.objects.create(contact_flag=True, task=task, invited_timestamp=now, user=user)
        with self.assertRaises(ValidationError):
            models.Participation.objects.create(response=response, task=task, invited_timestamp=now, user=user)
        with self.assertRaises(ValidationError):
            models.Participation.objects.create(response=response, contact_flag=True, invited_timestamp=now, user=user)
        with self.assertRaises(ValidationError):
            models.Participation.objects.create(response=response, contact_flag=True, task=task, user=user)
        with self.assertRaises(ValidationError):
            models.Participation.objects.create(response=response, contact_flag=True, task=task, invited_timestamp=now)

    def test_bump_task_status_to_scheduled(self):
        task = mommy_recipes.task.make()
        task.make_participants()
        self.assertEqual(task.status, task.STATUS_PENDING)
        for participation in task.participants.all():
            participation.response = participation.RESPONSE_ACCEPTED
            participation.save()
        task.refresh_from_db()
        self.assertEqual(task.status, task.STATUS_SCHEDULED)


class ContactModelTestCase(TestCase):

    def test_create_with_job_stores_data(self):
        user = mommy_recipes.user.make()
        job = mommy_recipes.job.make()
        now = timezone.now()
        contact = models.Contact.objects.create(
            name='Test Name',
            note='Note',
            email='test@example.com',
            mobile_number='(202) 555-3485',
            job=job,
            created_timestamp=now,
            modified_timestamp=now,
            author=user,
        )
        contact.refresh_from_db()
        self.assertEqual(contact.name, 'Test Name')
        self.assertEqual(contact.note, 'Note')
        self.assertEqual(contact.email, 'test@example.com')
        self.assertEqual(contact.mobile_number, '(202) 555-3485')
        self.assertEqual(contact.job, job)
        self.assertEqual(contact.created_timestamp, now)
        self.assertEqual(contact.modified_timestamp, now)
        self.assertEqual(contact.author, user)

    def test_create_with_task_stores_data(self):
        user = mommy_recipes.user.make()
        task = mommy_recipes.task.make()
        now = timezone.now()
        contact = models.Contact.objects.create(
            name='Test Name',
            email='test@example.com',
            mobile_number='(202) 555-3485',
            task=task,
            created_timestamp=now,
            modified_timestamp=now,
            author=user,
        )
        contact.refresh_from_db()
        self.assertEqual(contact.task, task)

    def test_required_fields(self):
        name = 'Test Name'
        email = 'test@example.com'
        num = '(202) 555-3485'
        user = mommy_recipes.user.make()
        job = mommy_recipes.job.make()
        now = timezone.now()
        with self.assertRaises(ValidationError):
            models.Contact.objects.create(
                email=email, mobile_number=num, job=job, created_timestamp=now, modified_timestamp=now)
        with self.assertRaises(ValidationError):
            models.Contact.objects.create(
                name=name, email=email, mobile_number=num, created_timestamp=now, modified_timestamp=now)
        with self.assertRaises(ValidationError):
            models.Contact.objects.create(
                name=name, email=email, mobile_number=num, job=job, modified_timestamp=now)
        with self.assertRaises(ValidationError):
            models.Contact.objects.create(
                name=name, email=email, mobile_number=num, job=job, created_timestamp=now)

    def test_job_or_task_required(self):
        user = mommy_recipes.user.make()
        job = mommy_recipes.job.make()
        task = mommy_recipes.task.make(job=job)
        now = timezone.now()
        with self.assertRaises(ValidationError):
            models.Contact.objects.create(
                name='Test Name',
                email='test@example.com',
                mobile_number='(202) 555-3485',
                job=job,
                task=task,
                created_timestamp=now,
                modified_timestamp=now,
                author=user,
            )
        with self.assertRaises(ValidationError):
            models.Contact.objects.create(
                name='Test Name',
                email='test@example.com',
                mobile_number='(202) 555-3485',
                created_timestamp=now,
                modified_timestamp=now,
                author=user,
            )


class NoteModelTestCase(TestCase):

    def test_create_with_job_stores_data(self):
        user = mommy_recipes.user.make()
        job = mommy_recipes.job.make()
        now = timezone.now()
        note = models.Note.objects.create(
            text='This is a note',
            job=job,
            created_timestamp=now,
            modified_timestamp=now,
            author=user,
        )
        note.refresh_from_db()
        self.assertEqual(note.text, 'This is a note')
        self.assertEqual(note.job, job)
        self.assertEqual(note.created_timestamp, now)
        self.assertEqual(note.modified_timestamp, now)
        self.assertEqual(note.author, user)

    def test_create_with_task_stores_data(self):
        user = mommy_recipes.user.make()
        task = mommy_recipes.task.make()
        now = timezone.now()
        note = models.Note.objects.create(
            text='This is a note',
            task=task,
            created_timestamp=now,
            modified_timestamp=now,
            author=user,
        )
        note.refresh_from_db()
        self.assertEqual(note.task, task)

    def test_required_fields(self):
        job = mommy_recipes.job.make()
        now = timezone.now()
        with self.assertRaises(ValidationError):
            models.Note.objects.create(job=job, modified_timestamp=now)
        with self.assertRaises(ValidationError):
            models.Note.objects.create(job=job, created_timestamp=now)

    def test_job_or_task_required(self):
        job = mommy_recipes.job.make()
        task = mommy_recipes.task.make(job=job)
        now = timezone.now()
        with self.assertRaises(ValidationError):
            models.Note.objects.create(job=job, task=task, created_timestamp=now, modified_timestamp=now)
        with self.assertRaises(ValidationError):
            models.Note.objects.create(created_timestamp=now, modified_timestamp=now)


@override_settings(MEDIA_ROOT='/tmp/django_test')
class DocumentModelTestCase(TestCase):

    def test_create_with_job_stores_data(self):
        file = SimpleUploadedFile('test_file.txt', b'test contents!')
        user = mommy_recipes.user.make()
        job = mommy_recipes.job.make()
        now = timezone.now()
        document = models.Document.objects.create(
            filename=file,
            job=job,
            created_timestamp=now,
            modified_timestamp=now,
            author=user,
        )
        document.refresh_from_db()
        self.assertEqual(document.filename.read(), b'test contents!')
        self.assertEqual(document.job, job)
        self.assertEqual(document.created_timestamp, now)
        self.assertEqual(document.modified_timestamp, now)
        self.assertEqual(document.author, user)

    def test_create_with_task_stores_data(self):
        file = SimpleUploadedFile('test_file.txt', b'test contents!')
        user = mommy_recipes.user.make()
        task = mommy_recipes.task.make()
        now = timezone.now()
        document = models.Document.objects.create(
            filename=file,
            task=task,
            created_timestamp=now,
            modified_timestamp=now,
            author=user,
        )
        document.refresh_from_db()
        self.assertEqual(document.task, task)

    def test_required_fields(self):
        file = SimpleUploadedFile('test_file.txt', b'test contents!')
        user = mommy_recipes.user.make()
        job = mommy_recipes.job.make()
        now = timezone.now()
        with self.assertRaises(ValidationError):
            models.Document.objects.create(job=job, created_timestamp=now, modified_timestamp=now)
        with self.assertRaises(ValidationError):
            models.Document.objects.create(filename=file, created_timestamp=now, modified_timestamp=now)
        with self.assertRaises(ValidationError):
            models.Document.objects.create(filename=file, job=job, modified_timestamp=now)
        with self.assertRaises(ValidationError):
            models.Document.objects.create(filename=file, job=job, created_timestamp=now)

    def test_job_or_task_required(self):
        file = SimpleUploadedFile('test_file.txt', b'test contents!')
        user = mommy_recipes.user.make()
        job = mommy_recipes.job.make()
        task = mommy_recipes.task.make(job=job)
        now = timezone.now()
        with self.assertRaises(ValidationError):
            models.Document.objects.create(
                filename=file, job=job, task=task, created_timestamp=now, modified_timestamp=now)
        with self.assertRaises(ValidationError):
            models.Document.objects.create(filename=file, created_timestamp=now, modified_timestamp=now)


class MessageModelTestCase(TestCase):

    def test_create_with_job_stores_data(self):
        job = mommy_recipes.job.make()
        user = mommy_recipes.user.make()
        now = timezone.now()
        message = models.Message.objects.create(
            timestamp=now,
            subject='This is just a subject text',
            body='This is just a body text',
            type=models.Message.TYPE_EMAIL,
            job=job,
            user=user,
            reason=models.Message.REASON_LOGIN,
        )
        message.refresh_from_db()
        self.assertEqual(message.timestamp, now)
        self.assertEqual(message.subject, 'This is just a subject text')
        self.assertEqual(message.body, 'This is just a body text')
        self.assertEqual(message.type, models.Message.TYPE_EMAIL)
        self.assertEqual(message.job, job)
        self.assertEqual(message.reason, models.Message.REASON_LOGIN)

    def test_create_with_task_stores_data(self):
        task = mommy_recipes.task.make()
        user = mommy_recipes.user.make()
        now = timezone.now()
        message = models.Message.objects.create(
            timestamp=now,
            subject='This is just a subject text',
            body='This is just a body text',
            type=models.Message.TYPE_EMAIL,
            task=task,
            user=user,
            reason=models.Message.REASON_LOGIN,
        )
        message.refresh_from_db()
        self.assertEqual(message.task, task)

    def test_required_fields(self):
        job = mommy_recipes.job.make()
        now = timezone.now()
        subject = 'This is just a subject text'
        body = 'This is just a body text'
        type = models.Message.TYPE_EMAIL
        user = mommy_recipes.user.make()
        rsn = models.Message.REASON_LOGIN

        with self.assertRaises(ValidationError):
            models.Message.objects.create(subject=subject, body=body, type=type, job=job, user=user, reason=rsn)
        with self.assertRaises(ValidationError):
            models.Message.objects.create(timestamp=now, body=body, type=type, job=job, user=user, reason=rsn)
        with self.assertRaises(ValidationError):
            models.Message.objects.create(timestamp=now, subject=subject, body=body, job=job, user=user, reason=rsn)
        with self.assertRaises(ValidationError):
            models.Message.objects.create(timestamp=now, subject=subject, body=body, type=type, job=job, user=user)

    @patch('construction.models.send_mail')
    def test_send_with_email_goes_to_email(self, send_mail):
        with self.settings(SEND_MESSAGES_TO_ADMIN=False):
            message = mommy_recipes.message.make(type=models.Message.TYPE_EMAIL)
            message.send()
            send_mail.assert_called()

    @patch('construction.models.send_mail')
    def test_send_email_with_setting_sends_twice(self, send_mail):
        with self.settings(SEND_MESSAGES_TO_ADMIN=True):
            company = mommy_recipes.contractor.make()
            mommy_recipes.contractor_admin.make(company=company)
            mommy_recipes.contractor_admin.make(company=company)
            message = mommy_recipes.message.make(type=models.Message.TYPE_EMAIL, task__job__owner=company)
            message.send()
            self.assertEqual(send_mail.call_count, 2)

    @patch('construction.models.send_mail')
    def test_send_email_without_setting_sends_once(self, send_mail):
        with self.settings(SEND_MESSAGES_TO_ADMIN=False):
            company = mommy_recipes.contractor.make()
            mommy_recipes.contractor_admin.make(company=company)
            mommy_recipes.contractor_admin.make(company=company)
            message = mommy_recipes.message.make(type=models.Message.TYPE_EMAIL, task__job__owner=company)
            message.send()
            self.assertEqual(send_mail.call_count, 1)

    @patch('construction.models.Message.send_sms')
    def test_send_with_sms_goes_to_sms(self, send_sms):
        with self.settings(SEND_MESSAGES_TO_ADMIN=False):
            message = mommy_recipes.message.make(type=models.Message.TYPE_SMS)
            message.send()
            send_sms.assert_called()

    @patch('cbcommon.twilio_client.twilio_client.send_sms')
    def test_send_sms_with_setting_sends_twice(self, send_sms):
        with self.settings(SEND_MESSAGES_TO_ADMIN=True):
            user = mommy_recipes.user.make(mobile_number='(203) 555-0999')
            user.refresh_from_db()
            company = mommy_recipes.contractor.make()
            mommy_recipes.contractor_admin.make(
                company=company, user=mommy_recipes.user.make(mobile_number='(203) 555-0998'))
            mommy_recipes.contractor_admin.make(
                company=company, user=mommy_recipes.user.make(mobile_number='(203) 555-0997'))
            message = mommy_recipes.message.make(
                type=models.Message.TYPE_SMS, task__job__owner=company, user=user)
            message.send()
            self.assertEqual(send_sms.call_count, 2)

    @patch('cbcommon.twilio_client.twilio_client.send_sms')
    def test_send_sms_without_setting_sends_once(self, send_sms):
        with self.settings(SEND_MESSAGES_TO_ADMIN=False):
            user = mommy_recipes.user.make(mobile_number='(203) 555-0999')
            user.refresh_from_db()
            company = mommy_recipes.contractor.make()
            mommy_recipes.contractor_admin.make(company=company, user__mobile_number='(203) 555-0998')
            mommy_recipes.contractor_admin.make(company=company, user__mobile_number='(203) 555-0997')
            message = mommy_recipes.message.make(
                type=models.Message.TYPE_SMS, task__job__owner=company, user=user)
            message.send()
            self.assertEqual(send_sms.call_count, 1)
