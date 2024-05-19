import os
from datetime import date, time, timedelta

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.template import loader, Context, Template
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
from smtplib import SMTPException

from account.models import AuthToken, User
from cbcommon.model_utils import ValidateModelMixin, StrictPhoneNumberField
from cbcommon.twilio_client import TwilioClientException, twilio_client
from localflavor.us.models import USStateField, USZipCodeField


class Company(ValidateModelMixin, models.Model):
    TYPE_CONTRACTOR = 1
    TYPE_SUBCONTRACTOR = 2
    TYPE_OPTIONS = (
        (TYPE_CONTRACTOR, 'General Contractor'),
        (TYPE_SUBCONTRACTOR, 'Subcontractor'),
    )
    PLAN_FREE = 1
    PLAN_PRO = 2
    PLAN_OPTIONS = (
        (PLAN_FREE, 'Free'),
        (PLAN_PRO, 'Pro'),
    )
    name = models.CharField(max_length=100)
    type = models.IntegerField(choices=TYPE_OPTIONS, default=TYPE_CONTRACTOR)

    billing_address = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=20, blank=True)
    state = USStateField(blank=True)
    zip = USZipCodeField(blank=True)

    start_of_day = models.TimeField(default=time(8), null=True, blank=True)
    end_of_day = models.TimeField(default=time(17), null=True, blank=True)
    reminder_time = models.TimeField(default=time(0), null=True, blank=True)
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    users = models.ManyToManyField('account.User', related_name='companies', through='CompanyRole')
    builders = models.ManyToManyField(
        'self', limit_choices_to={'type': TYPE_CONTRACTOR}, related_name='contractors', symmetrical=False, blank=True,
    )  # DEPRECATED

    current_plan = models.IntegerField(choices=PLAN_OPTIONS, default=PLAN_FREE)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    scheduling_options = JSONField(null=True, blank=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name

    @property
    def city_state_zip(self):
        return ' '.join(part for part in [self.city + ', ' if self.city else '', self.state, self.zip] if part)

    @property
    def non_working_days_in_day_of_week(self):
        non_working_days = []
        if not self.sunday:
            non_working_days.append(0)
        if not self.monday:
            non_working_days.append(1)
        if not self.tuesday:
            non_working_days.append(2)
        if not self.wednesday:
            non_working_days.append(3)
        if not self.thursday:
            non_working_days.append(4)
        if not self.friday:
            non_working_days.append(5)
        if not self.saturday:
            non_working_days.append(6)
        return non_working_days

    @property
    def non_working_days(self):
        non_working_days = []
        if not self.monday:
            non_working_days.append('Monday')
        if not self.tuesday:
            non_working_days.append('Tuesday')
        if not self.wednesday:
            non_working_days.append('Wednesday')
        if not self.thursday:
            non_working_days.append('Thursday')
        if not self.friday:
            non_working_days.append('Friday')
        if not self.saturday:
            non_working_days.append('Saturday')
        if not self.sunday:
            non_working_days.append('Sunday')
        return non_working_days


class CompanyRole(ValidateModelMixin, models.Model):
    USER_TYPES_DISPLAY = {
        'admin': 'Admin',
        'builder': 'Builder',
        'crew_leader': 'Subcontractor',
        'superintendent': 'Crew / Flex',
        'contact': 'Contact',
    }
    CALENDAR_FILTER_SUBCONTRACTOR = 1
    CALENDAR_FILTER_SUPERINTENDENT = 2
    CALENDAR_FILTER_BUILDER = 3
    CALENDAR_FILTER_JOB = 4
    FILTER_OPTIONS = (
        (CALENDAR_FILTER_BUILDER, 'Builder'),
        (CALENDAR_FILTER_SUBCONTRACTOR, 'Subcontractor'),
        (CALENDAR_FILTER_SUPERINTENDENT, 'Crew / Flex'),
        (CALENDAR_FILTER_JOB, 'Job'),
    )
    company = models.ForeignKey(Company, related_name='roles')
    user = models.ForeignKey('account.User', related_name='roles')
    is_active = models.BooleanField(default=True)
    is_employed = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_builder = models.BooleanField(default=False)
    is_crew_leader = models.BooleanField(default=False)
    is_superintendent = models.BooleanField(default=False)
    is_contact = models.BooleanField(default=False)

    crew_leader = models.ForeignKey(
        'self', limit_choices_to={'is_crew_leader': True}, related_name='crew_staff', null=True, blank=True,
    )
    contractors = models.ManyToManyField(Company, related_name='invited_roles', blank=True)  # DEPRECATED
    connections = models.ManyToManyField('self', blank=True)
    default_calendar_filter = models.PositiveSmallIntegerField(
        choices=FILTER_OPTIONS, default=CALENDAR_FILTER_SUBCONTRACTOR
    )
    page_size = models.PositiveSmallIntegerField(default=20)
    can_see_full_job = models.BooleanField(default=False)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return '{}: {} ({})'.format(self.company, self.user, self.user_types_display)

    @property
    def name_with_company(self):
        return '{} ({})'.format(self.user, self.company)

    @property
    def user_types(self):
        types = []
        if self.is_admin:
            types.append('admin')
        if self.is_builder:
            types.append('builder')
        if self.is_crew_leader:
            types.append('crew_leader')
        if self.is_superintendent:
            types.append('superintendent')
        if self.is_contact:
            types.append('contact')
        return types

    @property
    def user_types_other(self):
        types = []
        if self.is_builder:
            types.append('builder')
        if self.is_crew_leader:
            types.append('crew_leader')
        if self.is_superintendent:
            types.append('superintendent')
        return types

    @property
    def user_types_display(self):
        return ', '.join(self.USER_TYPES_DISPLAY[type] for type in self.user_types)

    @property
    def user_types_other_display(self):
        return ', '.join(self.USER_TYPES_DISPLAY[type] for type in self.user_types_other)

    @property
    def jobs(self):
        pass

    @property
    def tasks(self):
        pass

    def send_invite_confirmations(self, role, company):
        # We have to force the signup emails because we did not tick enable_*_notifications
        # (As a courtesy measure, if the user didn't confirm, it won't receive further messages)
        AuthToken.make_token(
            self.user, sender_role=role, sender=company, authz_type=AuthToken.AUTHZ_INVITE,
        ).send_message(force_first_send=True)


class Subdivision(ValidateModelMixin, models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Job(ValidateModelMixin, models.Model):
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=20)
    state = USStateField()
    zip = USZipCodeField()
    lot_number = models.CharField(max_length=20, blank=True)
    subdivision = models.ForeignKey(
        Subdivision, related_name='jobs', null=True, blank=True, on_delete=models.SET_NULL
    )
    created_by = models.ForeignKey(
        Company, related_name='created_jobs', null=True, blank=True, on_delete=models.SET_NULL
    )
    owner = models.ForeignKey(Company, related_name='owned_jobs', null=True, blank=True, on_delete=models.SET_NULL)
    builder = models.ForeignKey(
        CompanyRole, limit_choices_to={'is_builder': True},
        related_name='jobs_as_builder', null=True, blank=True, on_delete=models.SET_NULL,
    )
    subcontractor = models.ForeignKey(
        CompanyRole, limit_choices_to={'is_crew_leader': True},
        related_name='jobs_as_subcontractor', null=True, blank=True, on_delete=models.SET_NULL,
    )
    superintendent = models.ForeignKey(
        CompanyRole, limit_choices_to={'is_superintendent': True}, related_name='jobs_as_superintendent',
        null=True, blank=True, on_delete=models.SET_NULL,
    )
    shared_to = models.ManyToManyField(Company, related_name='shared_jobs', blank=True)  # DEPRECATED
    date_added = models.DateField(default=date.today)
    is_archived = models.BooleanField(default=False)

    roles = models.ManyToManyField(CompanyRole, related_name='shared_jobs', blank=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.location

    @property
    def location(self):
        return ', '.join(str(part) for part in [self.street_address, '#' + self.lot_number, self.subdivision] if part)

    @property
    def owner_non_working_days_in_day_of_week(self):
        non_working_days = []
        if not self.owner.sunday:
            non_working_days.append(0)
        if not self.owner.monday:
            non_working_days.append(1)
        if not self.owner.tuesday:
            non_working_days.append(2)
        if not self.owner.wednesday:
            non_working_days.append(3)
        if not self.owner.thursday:
            non_working_days.append(4)
        if not self.owner.friday:
            non_working_days.append(5)
        if not self.owner.saturday:
            non_working_days.append(6)
        return non_working_days


class TaskCategory(ValidateModelMixin, models.Model):
    contractor = models.ForeignKey(
        Company, limit_choices_to={'type': Company.TYPE_CONTRACTOR}, related_name='task_categories',
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name


class TaskSubCategory(ValidateModelMixin, models.Model):
    category = models.ForeignKey(TaskCategory, related_name='subcategories')
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Task(ValidateModelMixin, models.Model):
    STATUS_TENTATIVE = 1
    STATUS_PENDING = 2
    STATUS_SCHEDULED = 3
    STATUS_OPTIONS = (
        (STATUS_TENTATIVE, 'Tentative'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_SCHEDULED, 'Scheduled'),
    )
    NOTIFICATION_REVIEW_GENERAL = 1
    NOTIFICATION_REVIEW_SCHEDULE = 2
    NOTIFICATION_TYPE_GENERAL = 1
    NOTIFICATION_TYPE_SCHEDULE = 2
    MESSAGE_REASON = {
        NOTIFICATION_TYPE_GENERAL: 5,
        NOTIFICATION_TYPE_SCHEDULE: 6
    }
    MESSAGE_SUBJECTS = {
        NOTIFICATION_TYPE_GENERAL: 'CrewBoss Task General Update Notification',
        NOTIFICATION_TYPE_SCHEDULE: 'CrewBoss Task Schedule Update Notification',
    }
    EMAIL_MESSAGE_BODIES = {
        NOTIFICATION_TYPE_GENERAL: (
            'Greetings from CrewBoss! Your task has been updated: {{ task.name }}.\n'
            '- Job: {{ task.job }}\n'
            '{% if task.category != None %}- Category: {{ task.category }}'
            '{% if task.subcategory != None %} / {{ task.subcategory }}{% endif %}\n{% endif %}'
        ),
        NOTIFICATION_TYPE_SCHEDULE: (
            'Greetings from CrewBoss! Your task\'s schedule has been updated: {{ task.name }}.\n'
            '- Job: {{ task.job }}\n'
            '{% if task.category != None %}- Category: {{ task.category }}'
            '{% if task.subcategory != None %} / {{ task.subcategory }}{% endif %}\n{% endif %}'
            '- Start Date: {{ task.start_date|date:"m/d/Y"|default:"" }}\n'
            '- End Date: {{ task.end_date|date:"m/d/Y"|default:"" }}\n'
            '- Start Time: {{ task.start_time|date:"H:i"|default:"" }}\n'
            '- End Time: {{ task.end_time|date:"H:i"|default:"" }}\n'
        )
    }
    EMAIL_MESSAGE_TEMPLATE_BODIES = {
        NOTIFICATION_REVIEW_GENERAL: 'notifications/task_review.html',
        NOTIFICATION_REVIEW_SCHEDULE: 'notifications/task_review.html'
    }
    TEXT_MESSAGE_BODIES = {
        NOTIFICATION_TYPE_GENERAL: EMAIL_MESSAGE_BODIES[NOTIFICATION_TYPE_GENERAL].replace('    - ', '- '),
        NOTIFICATION_TYPE_SCHEDULE: EMAIL_MESSAGE_BODIES[NOTIFICATION_TYPE_SCHEDULE].replace('    - ', '- ')
    }

    author = models.ForeignKey(User, related_name='tasks', null=True, blank=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(TaskCategory, related_name='tasks', null=True, blank=True, on_delete=models.SET_NULL)
    subcategory = models.ForeignKey(
        TaskSubCategory, related_name='tasks', null=True, blank=True, on_delete=models.SET_NULL
    )
    job = models.ForeignKey(Job, related_name='tasks')
    subcontractor = models.ForeignKey(
        CompanyRole, limit_choices_to={'is_crew_leader': True},
        related_name='tasks_as_crew_leader', null=True, blank=True, on_delete=models.SET_NULL,
    )
    assigned_to = models.ForeignKey(
        Company, related_name='assigned_tasks', null=True, blank=True, on_delete=models.SET_NULL
    )  # DEPRECATED
    superintendent = models.ForeignKey(
        CompanyRole, limit_choices_to={'is_superintendent': True}, related_name='tasks_as_superintendent',
        null=True, blank=True, on_delete=models.SET_NULL,
    )
    builder = models.ForeignKey(
        CompanyRole, limit_choices_to={'is_builder': True},
        related_name='tasks_as_builder', null=True, blank=True, on_delete=models.SET_NULL,
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)  # duration in working days
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_OPTIONS, default=STATUS_PENDING)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ('start_date', 'start_time',)

    def __str__(self):
        return self.name

    def get_duration(self):
        if self.duration:
            return self.duration
        days_apart = (self.end_date - self.start_date).days
        duration = days_apart + 1
        start_date = self.start_date
        for i in range(int(days_apart)):
            start_date = start_date + timedelta(days=1)
            if int(start_date.strftime('%w')) in self.non_working_days_in_day_of_week:
                duration = duration - 1
        return duration

    @property
    def non_working_days_in_day_of_week(self):
        return self.job.owner_non_working_days_in_day_of_week

    @property
    def between(self):
        if not self.start_time and not self.end_time:
            return 'Not set'
        if self.start_time and not self.end_time:
            return f'Starts at {self.start_time.strftime("%I:%M %p")}'
        if not self.start_time and self.end_time:
            return f'Ends at {self.end_time.strftime("%I:%M %p")}'
        return f'{self.start_time.strftime("%I:%M %p")} - {self.end_time.strftime("%I:%M %p")}'

    @property
    def all_notes(self):
        return Note.objects.filter(models.Q(task=self) | models.Q(job=self.job)).distinct()

    @property
    def all_contacts(self):
        return Contact.objects.filter(models.Q(task=self) | models.Q(job=self.job)).distinct()

    @property
    def contacts_with_notification(self):
        return Contact.objects.filter(
            models.Q(task=self) | models.Q(job=self.job),
            models.Q(enable_email_notifications=True) | models.Q(enable_text_notifications=True)).distinct()

    @property
    def has_queued_notification(self):
        return bool(NotificationQueue.fetch_queued_notification(self))

    @property
    def key_participants(self):
        participants = {}
        if self.subcontractor:
            participants['subcontractor'] = self.participants.filter(user=self.subcontractor.user).first()
        if self.superintendent:
            participants['superintendent'] = self.participants.filter(user=self.superintendent.user).first()
        if self.builder:
            participants['builder'] = self.participants.filter(user=self.builder.user).first()
        return participants

    def make_participants(self):
        new_participants = []
        if self.subcontractor:
            participation, created = self.participants.get_or_create(user=self.subcontractor.user, defaults={
                'response': Participation.RESPONSE_PENDING,
                'contact_flag': True,
                'invited_timestamp': timezone.now(),
            })
            if created:
                new_participants.append(participation)
        if self.superintendent:
            participation, created = self.participants.get_or_create(user=self.superintendent.user, defaults={
                'response': Participation.RESPONSE_PENDING,
                'contact_flag': True,
                'invited_timestamp': timezone.now(),
            })
            if created:
                new_participants.append(participation)
        if self.builder:
            participation, created = self.participants.get_or_create(user=self.builder.user, defaults={
                'response': Participation.RESPONSE_PENDING,
                'contact_flag': True,
                'invited_timestamp': timezone.now(),
            })
            if created:
                new_participants.append(participation)
        return new_participants

    def sync_status(self):
        key_responses = self.key_participants
        accepts = [
            True for participation in key_responses.values()
            if participation and participation.response == participation.RESPONSE_ACCEPTED
        ]
        has_rejects = any(
            True for participation in key_responses.values()
            if participation and participation.response == participation.RESPONSE_REJECTED
        )
        if key_responses and len(accepts) == len(key_responses):
            self.status = self.STATUS_SCHEDULED
        elif not key_responses.get('subcontractor') or has_rejects:
            self.status = self.STATUS_TENTATIVE
        else:
            self.status = self.STATUS_PENDING
        self.save()

    def participants_to_pending(self):
        for key, participant in self.key_participants.items():
            participant.response = Participation.RESPONSE_PENDING
            participant.save()

    def send_notification_to_contacts(self, notification_type):
        if notification_type == NotificationQueue.TYPE_INVITES_ONLY:
            return  # Don't notify contacts for invites

        context = Context({'task': self, 'notification_type': notification_type})
        for contact in self.contacts_with_notification:
            if contact.enable_text_notifications:
                Message.objects.create(
                    contact=contact,
                    timestamp=timezone.now(),
                    type=Message.TYPE_SMS,
                    subject=self.MESSAGE_SUBJECTS[notification_type],
                    body=Template(self.TEXT_MESSAGE_BODIES[notification_type]).render(context),
                    task=self,
                    reason=self.MESSAGE_REASON[notification_type],
                ).send_to_contact(context)
            if contact.enable_email_notifications:
                Message.objects.create(
                    contact=contact,
                    timestamp=timezone.now(),
                    type=Message.TYPE_EMAIL,
                    subject=self.MESSAGE_SUBJECTS[notification_type],
                    body=Template(self.EMAIL_MESSAGE_BODIES[notification_type]).render(Context(context)),
                    task=self,
                    reason=self.MESSAGE_REASON[notification_type],
                ).send_to_contact(context)

    def send_reminder_to_participants(self):
        for participant in self.participants.all():
            participant.send_reminder()


class Participation(ValidateModelMixin, models.Model):
    RESPONSE_ACCEPTED = 1
    RESPONSE_REJECTED = 2
    RESPONSE_PENDING = 3
    RESPONSE_NOT_APPLICABLE = 4
    RESPONSE_OPTIONS = (
        (RESPONSE_ACCEPTED, 'Accepted'),
        (RESPONSE_REJECTED, 'Rejected'),
        (RESPONSE_PENDING, 'Pending'),
        (RESPONSE_NOT_APPLICABLE, 'Not Applicable'),
    )

    response = models.PositiveSmallIntegerField(choices=RESPONSE_OPTIONS)
    contact_flag = models.BooleanField()
    task = models.ForeignKey(Task, related_name='participants')
    invited_timestamp = models.DateTimeField()
    response_timestamp = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='participations')

    class Meta:
        ordering = ('-task__job_id', 'task__start_date', 'task__start_time',)

    def clean(self):
        if self.contact_flag is None:
            raise ValidationError('Contact flag is required')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.task.sync_status()

    def send_token_message(self, sender_role, sender):
        AuthToken.make_token(
            self.user,
            authz_type=AuthToken.AUTHZ_TASK_ACKNOWLEDGE_REQUEST,
            participation=self,
            sender_role=sender_role,
            sender=sender,
        ).send_message()

    def send_changed_general_message(self, sender_role, sender):
        token = AuthToken.make_token(
            self.user,
            authz_type=AuthToken.AUTHZ_TASK_UPDATE_GENERAL,
            participation=self,
            sender_role=sender_role,
            sender=sender,
        )
        token.send_message()
        # if self.user.user_type in [User.CONTRACTOR_ADMIN, User.CREW_LEADER]:
        #     token.send_message_to_crew_staff()

    def send_changed_schedule_message(self, sender_role, sender):
        token = AuthToken.make_token(
            self.user,
            authz_type=AuthToken.AUTHZ_TASK_UPDATE_SCHEDULE,
            participation=self,
            sender_role=sender_role,
            sender=sender,
        )
        token.send_message()
        # if self.user.user_type in [User.CONTRACTOR_ADMIN, User.CREW_LEADER]:
        #     token.send_message_to_crew_staff()

    def send_remove_message(self):
        AuthToken.make_token(
            self.user,
            authz_type=AuthToken.AUTHZ_TASK_REMOVE,
            participation=self,
        ).send_message()

    def send_reminder(self):
        AuthToken.make_token(
            self.user,
            authz_type=AuthToken.AUTHZ_TASK_REMINDER,
            participation=self,
        ).send_message()

    def send_status_update_message(self, sender_role, sender):
        AuthToken.make_token(
            self.user,
            authz_type=AuthToken.AUTHZ_TASK_STATUS_UPDATE,
            participation=self,
            sender_role=sender_role,
            sender=sender,
        ).send_message()

    def send_reject_message(self, extra_context):
        AuthToken.make_token(
            self.user,
            authz_type=AuthToken.AUTHZ_TASK_REJECT,
            participation=self,
        ).send_message(extra_context=extra_context)

    def send_suggested_schedule_message(self, extra_context):
        AuthToken.make_token(
            self.user,
            authz_type=AuthToken.AUTHZ_TASK_SUGGEST_SCHEDULE,
            participation=self,
        ).send_message(extra_context=extra_context)


class Contact(ValidateModelMixin, models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    note = models.CharField(blank=True, null=True, max_length=255)
    email = models.EmailField(blank=True, null=True)
    mobile_number = StrictPhoneNumberField(blank=True, null=True)
    role = models.ForeignKey(CompanyRole, null=True, blank=True, related_name='contacts', on_delete=models.SET_NULL)
    job = models.ForeignKey(Job, null=True, blank=True, related_name='contacts', on_delete=models.SET_NULL)
    task = models.ForeignKey(Task, null=True, blank=True, related_name='contacts', on_delete=models.SET_NULL)
    created_timestamp = models.DateTimeField()
    modified_timestamp = models.DateTimeField()
    author = models.ForeignKey(User, related_name='contacts', null=True, blank=True, on_delete=models.SET_NULL)

    enable_text_notifications = models.BooleanField(default=False)
    enable_email_notifications = models.BooleanField(default=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.job and self.task:
            raise ValidationError('Cannot set both job and task')
        if not self.job and not self.task:
            raise ValidationError('Either job or task is required')

    @property
    def mobile_number_display(self):
        if self.mobile_number and self.mobile_number.country_code == 1:
            return self.mobile_number.as_national
        return self.mobile_number.as_international


class Note(ValidateModelMixin, models.Model):
    text = models.TextField(blank=True)
    text_es = models.TextField(blank=True)
    orig_is_en = models.BooleanField(default=True)
    job = models.ForeignKey(Job, null=True, blank=True, related_name='notes')
    task = models.ForeignKey(Task, null=True, blank=True, related_name='notes')
    created_timestamp = models.DateTimeField()
    modified_timestamp = models.DateTimeField()
    author = models.ForeignKey(User, related_name='notes', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.text

    def clean(self):
        super().clean()
        if self.job and self.task:
            raise ValidationError('Cannot set both job and task')
        if not self.job and not self.task:
            raise ValidationError('Either job or task is required')

    @property
    def type(self):
        if self.task:
            return 'Task'
        elif self.job:
            return 'Job'
        return ''


class Document(ValidateModelMixin, models.Model):
    filename = models.FileField(upload_to='documents')
    job = models.ForeignKey(Job, null=True, blank=True, related_name='documents', on_delete=models.SET_NULL)
    task = models.ForeignKey(Task, null=True, blank=True, related_name='documents', on_delete=models.SET_NULL)
    created_timestamp = models.DateTimeField()
    modified_timestamp = models.DateTimeField()
    author = models.ForeignKey(User, related_name='documents', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.filename.name if self.filename else ''

    def clean(self):
        super().clean()
        if self.job and self.task:
            raise ValidationError('Cannot set both job and task')
        if not self.job and not self.task:
            raise ValidationError('Either job or task is required')

    @property
    def file_type(self):
        file_type = os.path.splitext(str(self.filename.name))[1]
        file_type = file_type.upper().strip('.')
        return file_type

    @property
    def file_name(self):
        file_name = os.path.splitext(str(self.filename))[0][10:]
        return file_name


class DefaultReminders(ValidateModelMixin, models.Model):
    REMINDER_OPTIONS = (
        (1, '1 day before'),
        (2, '2 days before'),
        (3, '3 days before'),
        (4, '4 days before'),
        (5, '5 days before'),
        (6, '6 days before'),
        (7, '1 week before'),
        (14, '2 weeks before'),
        (21, '3 weeks before'),
    )

    company = models.ForeignKey(Company, related_name='default_reminders')
    reminder_days = models.IntegerField(choices=REMINDER_OPTIONS)
    reminder_sent = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('reminder_days',)
        unique_together = ('company', 'reminder_days')


class Reminder(ValidateModelMixin, models.Model):
    REMINDER_OPTIONS = (
        (1, '1 day before'),
        (2, '2 days before'),
        (3, '3 days before'),
        (4, '4 days before'),
        (5, '5 days before'),
        (6, '6 days before'),
        (7, '1 week before'),
        (14, '2 weeks before'),
        (21, '3 weeks before'),
    )

    task = models.ForeignKey(Task, related_name='reminders')
    reminder_days = models.IntegerField(choices=REMINDER_OPTIONS)
    reminder_sent = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('reminder_days',)
        unique_together = ('task', 'reminder_days')

    def __str__(self):
        return f'{self.task}: {self.get_reminder_days_display()} {self.task.start_date}'

    def is_due(self):
        return self.task.start_date - timedelta(days=self.reminder_days) <= timezone.now().date()


class NotificationQueueQuerySet(models.QuerySet):
    def queued_notifications(self):
        return self.filter(sent_timestamp__isnull=True)


class NotificationQueue(ValidateModelMixin, models.Model):
    TYPE_GENERAL = 1
    TYPE_SCHEDULE = 2
    TYPE_INVITES_ONLY = 3
    TYPE_OPTIONS = (
        (TYPE_GENERAL, 'General'),
        (TYPE_SCHEDULE, 'Schedule'),
        (TYPE_INVITES_ONLY, 'Invites Only'),
    )
    objects = NotificationQueueQuerySet.as_manager()

    task = models.ForeignKey(Task, null=True, blank=True, related_name='pending_messages')
    type = models.IntegerField(choices=TYPE_OPTIONS)
    sent_timestamp = models.DateTimeField(null=True, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    modified_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'{self.task}: {self.get_type_display()}'

    @classmethod
    def fetch_queued_notification(cls, task):
        return cls.objects.filter(task=task, sent_timestamp__isnull=True).first()

    @classmethod
    def queue_notification(cls, task, type):
        queued_notification = cls.fetch_queued_notification(task)
        if not queued_notification:
            return cls.objects.create(task=task, type=type)

        # Anything else eats Invites Only
        if queued_notification.type == cls.TYPE_INVITES_ONLY and type != cls.TYPE_INVITES_ONLY:
            queued_notification.type = type
            queued_notification.save()
        # Schedule eats General because the email message contains both
        elif queued_notification.type == cls.TYPE_GENERAL and type == cls.TYPE_SCHEDULE:
            queued_notification.type = type
            queued_notification.save()
        return queued_notification

    def send_messages(self, sender_role, sender):
        assert not self.sent_timestamp
        messages = {
            'successful': {
                'roles': {
                    'emails': [],
                    'mobile_numbers': [],
                },
                'contacts': {
                    'emails': [],
                    'mobile_numbers': [],
                }
            },
            'unsuccessful': {
                'roles': {
                    'emails': [],
                    'mobile_numbers': [],
                },
                'contacts': {
                    'emails': [],
                    'mobile_numbers': [],
                }
            },
            'has_error': False,
        }

        for participant in self.task.key_participants.values():
            try:
                has_sms_error = False
                has_smtp_error = False
                mobile_number_notif = f'{participant.user.get_full_name()}: {participant.user.mobile_number_display}'
                email_notif = f'{participant.user.get_full_name()}: {participant.user.email}'

                if self.participant_invited_after_last_send(participant):
                    if not self.task.is_completed:
                        participant.send_token_message(sender_role, sender)
                else:
                    if self.type == self.TYPE_GENERAL:
                        participant.send_changed_general_message(sender_role, sender)
                    if self.type == self.TYPE_SCHEDULE:
                        participant.send_changed_schedule_message(sender_role, sender)

            except TwilioClientException:
                has_sms_error = True
                messages['unsuccessful']['roles']['mobile_numbers'].append(mobile_number_notif)
                messages['has_error'] = True
            except SMTPException:
                has_smtp_error = True
                messages['unsuccessful']['roles']['emails'].append(mobile_number_notif)
                messages['has_error'] = True
            except AuthToken.BothNotificationFailedException:
                messages['unsuccessful']['roles']['mobile_numbers'].append(mobile_number_notif)
                messages['unsuccessful']['roles']['emails'].append(mobile_number_notif)
                messages['has_error'] = True
                has_sms_error = True
                has_smtp_error = True

            if not has_sms_error:
                messages['successful']['roles']['mobile_numbers'].append(mobile_number_notif)
            if not has_smtp_error:
                messages['successful']['roles']['emails'].append(email_notif)

        try:
            self.task.send_notification_to_contacts(self.type)
        except TwilioClientException:
            pass

        self.sent_timestamp = timezone.now()
        self.save()
        return messages

    def participant_invited_after_last_send(self, participant):
        last_sent_date = NotificationQueue.objects.filter(
            task=self.task, sent_timestamp__isnull=False
        ).aggregate(latest=models.Max('sent_timestamp'))['latest']

        return not last_sent_date or participant.invited_timestamp > last_sent_date


class TaskDetailSuggestion(ValidateModelMixin, models.Model):
    STATUS_PENDING = 1
    STATUS_ACCEPTED = 2
    STATUS_REJECTED = 3
    STATUS_OPTIONS = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    )
    responses = JSONField(null=True, blank=True)
    participation = models.ForeignKey('Participation', related_name='suggestions')  # suggester
    task = models.ForeignKey('Task', related_name='suggestions')
    status = models.PositiveSmallIntegerField(choices=STATUS_OPTIONS, default=STATUS_PENDING)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class Message(ValidateModelMixin, models.Model):
    TYPE_EMAIL = 1
    TYPE_SMS = 2
    TYPE_OPTIONS = (
        (TYPE_EMAIL, 'Email'),
        (TYPE_SMS, 'SMS'),
    )
    REASON_LOGIN = 1
    REASON_SIGNUP = 2
    REASON_PASSWORD_RESET = 3
    REASON_TASK_ACKNOWLEDGE_REQUEST = 4
    REASON_TASK_UPDATE_GENERAL = 5
    REASON_TASK_UPDATE_SCHEDULE = 6
    REASON_TASK_REMOVE = 7
    REASON_TASK_STATUS_UPDATE = 8
    REASON_TASK_REMINDER = 9
    REASON_INVITE = 10
    REASON_TASK_REJECT = 11
    REASON_TASK_SUGGEST_SCHEDULE = 12
    REASON_USER_LOCKED_OUT = 13
    REASON_OPTIONS = (
        (REASON_LOGIN, 'Login Authorization'),
        (REASON_SIGNUP, 'Signup Confirmation'),
        (REASON_INVITE, 'Invite Confirmation'),
        (REASON_PASSWORD_RESET, 'Password Reset Authorization'),
        (REASON_TASK_ACKNOWLEDGE_REQUEST, 'Task Acknowledge Authorization'),
        (REASON_TASK_UPDATE_GENERAL, 'Task General Update Notification'),
        (REASON_TASK_UPDATE_SCHEDULE, 'Task Schedule Update Notification'),
        (REASON_TASK_REMOVE, 'Task Removal Notification'),
        (REASON_TASK_STATUS_UPDATE, 'Task Participation Status Update Notification'),
        (REASON_TASK_REMINDER, 'Task Reminder'),
        (REASON_TASK_REJECT, 'Task Schedule Rejection Notification'),
        (REASON_USER_LOCKED_OUT, 'Task Schedule Suggestion Notification'),
    )
    timestamp = models.DateTimeField()
    type = models.IntegerField(choices=TYPE_OPTIONS)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sender = models.ForeignKey(Company, null=True, blank=True, related_name='sent_messages')
    job = models.ForeignKey(Job, null=True, blank=True, related_name='messages')
    task = models.ForeignKey(Task, null=True, blank=True, related_name='messages')
    contact = models.ForeignKey(Contact, null=True, blank=True, related_name='messages')
    user = models.ForeignKey(User, null=True, blank=True, related_name='messages')
    reason = models.IntegerField(choices=REASON_OPTIONS)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.body

    def send(self):
        if self.type == self.TYPE_EMAIL:
            self.send_email()
        if self.type == self.TYPE_SMS:
            self.send_sms()

    def send_email(self):
        recipients = []
        if settings.SEND_MESSAGES_TO_ADMIN and (self.task or self.job):
            job = self.job if self.job else self.task.job
            recipients = list(job.owner.roles.filter(is_admin=True).values_list('user__email', flat=True))
        elif self.user.email:
            recipients = [self.user.email]

        for recipient in recipients:
            send_mail(self.subject, self.body, settings.DEFAULT_FROM_EMAIL, [recipient])

    def send_sms(self):
        if self.sender:
            sender = self.sender
        elif self.job:
            sender = self.job.owner
        elif self.task and self.task.job:
            sender = self.task.job.owner
        else:
            sender = None

        if settings.SEND_MESSAGES_TO_ADMIN and (self.task or self.job):
            job = self.job if self.job else self.task.job
            recipients = list(job.owner.roles.filter(is_admin=True).values_list(
                'user__mobile_number', flat=True))
        else:
            if self.user.mobile_number:
                recipients = [self.user.mobile_number.as_e164]
            else:
                recipients = []

        for recipient in recipients:
            if recipient:
                with transaction.atomic():
                    if sender:
                        sender.transactions.create(
                            type=Transaction.TYPE_SMS, amount=-settings.SMS_FEE,
                            internal_fee=settings.INTERNAL_SMS_FEE, description=f'SMS sent to {recipient}',
                        )
                        sender.current_balance -= settings.SMS_FEE
                        sender.save()
                    # NOTE: excluding our dummy numbers (202) 555-xxxx, because Twilio will complain about them
                    if not self.user.mobile_number.as_e164.startswith('+1202555'):
                        twilio_client.send_sms(recipient, self.body)
                    else:
                        print('Fake sending SMS to {}: \n{}'.format(recipient, self.body))

    def send_to_contact(self, context):
        if self.type == self.TYPE_EMAIL:
            self.send_email_to_contact(context)
        if self.type == self.TYPE_SMS:
            self.send_sms_to_contact()

    def send_email_to_contact(self, context):
        context = {'SITE_URL': settings.SITE_URL, 'obj': context}
        recipients = [self.contact.role.user.email if self.contact.role else self.contact.email]
        for recipient in recipients:
            subject, from_email, recipient = self.subject, settings.DEFAULT_FROM_EMAIL, recipient
            html_content = loader.render_to_string(
                Task.EMAIL_MESSAGE_TEMPLATE_BODIES[context['obj']['notification_type']], context)
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(subject, text_content, from_email, [recipient])
            email.attach_alternative(html_content, "text/html")
            email.send()

    def send_sms_to_contact(self):
        recipients = [
            (self.contact.role.user.mobile_number.as_e164 if self.contact.role.user.mobile_number else None)
            if self.contact.role
            else (self.contact.mobile_number.as_e164 if self.contact.mobile_number else None)
        ]
        for recipient in recipients:
            if recipient:
                twilio_client.send_sms(recipient, self.body)


class Transaction(ValidateModelMixin, models.Model):
    TYPE_PAYMENT = 1
    TYPE_SMS = 2
    TYPE_OPTIONS = (
        (TYPE_PAYMENT, 'Payment'),
        (TYPE_SMS, 'SMS Message'),
    )

    company = models.ForeignKey(Company, related_name='transactions')
    date = models.DateTimeField(default=timezone.now)
    type = models.IntegerField(choices=TYPE_OPTIONS)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    internal_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return f'{self.date}: {self.company} {self.get_type_display()} - ${self.amount}'
