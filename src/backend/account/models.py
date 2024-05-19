import random
from datetime import timedelta
from string import ascii_letters, digits

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import models
from django.template import loader, Context, Template
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from smtplib import SMTPException

from cbcommon.twilio_client import TwilioClientException
from cbcommon.model_utils import ValidateModelMixin, StrictPhoneNumberField


class UserManager(BaseUserManager):
    """
    Copy of django.contrib.auth.models.UserManager but without username and
    with mobile number
    """
    use_in_migrations = True

    def _create_user(self, email=None, mobile_number=None, password=None, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """

        if not password:
            raise ValueError(_('Password is required'))

        email = self.normalize_email(email)
        user = self.model(email=email, mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, mobile_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, mobile_number, password, **extra_fields)

    def create_superuser(self, email=None, mobile_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(email, mobile_number, password, **extra_fields)

    def active_this_month(self):
        from construction.models import Participation
        timezone_now = timezone.now()
        year_now = timezone_now.year
        month_now = timezone_now.month

        q1 = models.Q(
            participations__task__start_date__year=year_now,
            participations__task__start_date__month=month_now
        )
        q2 = models.Q(
            participations__task__end_date__year=year_now,
            participations__task__end_date__month=month_now
        )
        q3 = models.Q(
            participations__task__start_date__lte=timezone_now,
            participations__task__end_date__gte=timezone_now
        )
        return self.get_queryset().filter(q1 | q2 | q3) \
            .exclude(participations__response=Participation.RESPONSE_PENDING)


class User(ValidateModelMixin, AbstractBaseUser, PermissionsMixin):
    """
    Copy of django.contrib.auth.models.AbstractUser but without username and
    with mobile_number
    """

    ACTIVE_PLAN = (
        ('contractor_annual', 'Contractor (Annual)'),
        ('contractor_monthly', 'Contractor (Monthly)'),
        ('builder_annual', 'Builder (Annual)'),
        ('builder_monthly', 'Builder (Monthly)'),
    )

    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=True,
        null=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    # NOTE: mobile_number is NOT unique, make sure only one is active so login works
    mobile_number = StrictPhoneNumberField(
        _('mobile number'),
        blank=True,
        null=True,
        error_messages={
            'unique': _("A user with that mobile number already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    active_role = models.OneToOneField(
        'construction.CompanyRole',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='role_user'
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    enable_text_notifications = models.BooleanField(default=False)
    enable_email_notifications = models.BooleanField(default=False)
    password_already_set = models.BooleanField(default=False)
    stripe_customer = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription = models.CharField(max_length=255, blank=True, null=True)
    has_active_subscription = models.BooleanField(default=False)
    active_plan = models.CharField(max_length=255, blank=True, null=True, choices=ACTIVE_PLAN)
    has_autorenew = models.BooleanField(default=True)
    expiry_date = models.DateField(blank=True, null=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile_number']

    class Meta:
        ordering = ('-pk',)

    def __str__(self):
        return self.get_full_name()

    def clean(self):
        self.email = self.__class__.objects.normalize_email(self.email) or None
        self.mobile_number = self.mobile_number or None

        if not self.email and not self.mobile_number:
            raise ValidationError(_('Need to have either email or mobile number'))

        # Enforce case-insensitive uniqueness on emails
        if (
            self.email and self.is_active and
            User.objects.exclude(id=self.id).filter(email__iexact=self.email).exists()
        ):
            raise ValidationError(_('User with that email already exists'))

        # Enforce uniqueness on active mobile numbers
        if (
            self.mobile_number and self.is_active and
            User.objects.exclude(id=self.id).filter(mobile_number=self.mobile_number, is_active=True).exists()
        ):
            raise ValidationError(_('Active user with that number already exists'))

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def mobile_number_display(self):
        if self.mobile_number:
            if self.mobile_number.country_code == 1:
                return self.mobile_number.as_national
            return self.mobile_number.as_international
        return ''

    @property
    def active_plan_prefix(self):
        if self.active_plan:
            return self.active_plan.split('_')[0]
        return ''

    # @property
    # def company_name(self):
    #     try:
    #         if self.builder.is_active:
    #             return self.builder.name
    #     except ObjectDoesNotExist:
    #         pass
    #     return None

    # @property
    # def crew_leader_for_staff(self):
    #     try:
    #         return self.crew_staff.crew_leader.user.id
    #     except ObjectDoesNotExist:
    #         pass
    #     return None
    #
    # @property
    # def contractor(self):
    #     if self.user_type in [self.CONTRACTOR_ADMIN, self.CREW_LEADER]:
    #         return self.crew_leader.contractor
    #     if self.user_type == self.CREW_STAFF:
    #         return self.crew_staff.crew_leader.contractor
    #     if self.user_type == self.SUPERINTENDENT:
    #         return self.superintendent.contractor
    #     if self.user_type == self.BUILDER:
    #         return self.builder.contractor
    #     return None

    def send_locked_out_user(self):
        AuthToken.make_token(
            self, authz_type=AuthToken.AUTHZ_USER_LOCKED_OUT
        ).send_message(force_first_send=True)

    def send_signup_confirmations(self):
        # We have to force the signup emails because did not tick enable_*_notifications
        # (As a courtesy measure, if the user didn't confirm, it won't receive further messages)
        AuthToken.make_token(self, authz_type=AuthToken.AUTHZ_SIGNUP).send_message(force_first_send=True)

    def send_password_resets(self):
        AuthToken.make_token(
            self, authz_type=AuthToken.AUTHZ_PASSWORD_RESET, sender=self.companies.first(),
        ).send_message(force_first_send=True)


class AuthToken(ValidateModelMixin, models.Model):
    """
    A limited-time token, sent through email or SMS and used for login or
    password reset.
    """
    AUTHZ_LOGIN = 1
    AUTHZ_SIGNUP = 2
    AUTHZ_PASSWORD_RESET = 3
    AUTHZ_TASK_ACKNOWLEDGE_REQUEST = 4
    AUTHZ_TASK_UPDATE_GENERAL = 5
    AUTHZ_TASK_UPDATE_SCHEDULE = 6
    AUTHZ_TASK_REMOVE = 7
    AUTHZ_TASK_STATUS_UPDATE = 8
    AUTHZ_TASK_REMINDER = 9
    AUTHZ_INVITE = 10
    AUTHZ_TASK_REJECT = 11
    AUTHZ_TASK_SUGGEST_SCHEDULE = 12
    AUTHZ_USER_LOCKED_OUT = 13
    AUTHZ_OPTIONS = (
        (AUTHZ_LOGIN, 'Login Authorization'),
        (AUTHZ_SIGNUP, 'Signup Confirmation'),
        (AUTHZ_INVITE, 'Invite Confirmation'),
        (AUTHZ_PASSWORD_RESET, 'Password Reset Authorization'),
        (AUTHZ_TASK_ACKNOWLEDGE_REQUEST, 'Task Acknowledge Authorization'),
        (AUTHZ_TASK_UPDATE_GENERAL, 'Task General Update Notification'),
        (AUTHZ_TASK_UPDATE_SCHEDULE, 'Task Schedule Update Notification'),
        (AUTHZ_TASK_REMOVE, 'Task Removal Notification'),
        (AUTHZ_TASK_STATUS_UPDATE, 'Task Participation Status Update Notification'),
        (AUTHZ_TASK_REMINDER, 'Task Starting Soon Reminder'),
        (AUTHZ_TASK_REJECT, 'Task Schedule Rejection Notification'),
        (AUTHZ_TASK_SUGGEST_SCHEDULE, 'Task Schedule Suggestion Notification'),
        (AUTHZ_USER_LOCKED_OUT, 'User Locked Out Notification'),
    )
    EXPIRY_DURATIONS = {
        AUTHZ_LOGIN: timedelta(hours=1),
        AUTHZ_SIGNUP: timedelta(days=7),
        AUTHZ_INVITE: timedelta(days=7),
        AUTHZ_PASSWORD_RESET: timedelta(hours=1),
        AUTHZ_TASK_ACKNOWLEDGE_REQUEST: timedelta(hours=1),
        AUTHZ_TASK_UPDATE_GENERAL: timedelta(hours=1),
        AUTHZ_TASK_UPDATE_SCHEDULE: timedelta(hours=1),
        AUTHZ_TASK_REMOVE: timedelta(hours=1),
        AUTHZ_TASK_STATUS_UPDATE: timedelta(hours=1),
        AUTHZ_TASK_REMINDER: timedelta(hours=1),
        AUTHZ_TASK_REJECT: timedelta(hours=1),
        AUTHZ_TASK_SUGGEST_SCHEDULE: timedelta(hours=1),
        AUTHZ_USER_LOCKED_OUT: timedelta(hours=1),
    }
    MESSAGE_SUBJECTS = {
        AUTHZ_LOGIN: 'CrewBoss Login Request',
        AUTHZ_SIGNUP: 'CrewBoss Signup Confirmation',
        AUTHZ_INVITE: 'CrewBoss Invite Confirmation',
        AUTHZ_PASSWORD_RESET: 'CrewBoss Password Reset',
        AUTHZ_TASK_ACKNOWLEDGE_REQUEST: 'CrewBoss Task Acknowledge Request',
        AUTHZ_TASK_UPDATE_GENERAL: 'CrewBoss Task General Update Notification',
        AUTHZ_TASK_UPDATE_SCHEDULE: 'CrewBoss Task Schedule Update Notification',
        AUTHZ_TASK_REMOVE: 'CrewBoss Task Removal Notification',
        AUTHZ_TASK_STATUS_UPDATE: 'CrewBoss Participation Status Update Notification',
        AUTHZ_TASK_REMINDER: 'CrewBoss Task Starting Soon Reminder',
        AUTHZ_TASK_REJECT: 'CrewBoss Task Schedule Pending Notification',
        AUTHZ_TASK_SUGGEST_SCHEDULE: 'CrewBoss Task Schedule Suggestion Notification',
        AUTHZ_USER_LOCKED_OUT: 'CrewBoss User Locked Out Notification',
    }
    EMAIL_MESSAGE_TEMPLATE_BODIES = {
        AUTHZ_LOGIN: 'notifications/authz_login.html',
        AUTHZ_SIGNUP: 'notifications/authz_signup.html',
        AUTHZ_INVITE: 'notifications/authz_invite.html',
        AUTHZ_PASSWORD_RESET: 'notifications/authz_reset_password.html',
        AUTHZ_TASK_ACKNOWLEDGE_REQUEST: 'notifications/task_acknowledge_request.html',
        AUTHZ_TASK_UPDATE_GENERAL: 'notifications/task_update_general.html',
        AUTHZ_TASK_UPDATE_SCHEDULE: 'notifications/task_update_schedule.html',
        AUTHZ_TASK_REMOVE: 'notifications/task_remove.html',
        AUTHZ_TASK_STATUS_UPDATE: 'notifications/task_status_update.html',
        AUTHZ_TASK_REMINDER: 'notifications/task_reminder.html',
        AUTHZ_TASK_REJECT: 'notifications/task_reject.html',
        AUTHZ_TASK_SUGGEST_SCHEDULE: 'notifications/task_suggest_schedule.html',
        AUTHZ_USER_LOCKED_OUT: 'notifications/authz_user_locked_out.html',
    }
    EMAIL_MESSAGE_BODIES = {
        AUTHZ_LOGIN: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'Your login link is: '
            '{{ SITE_URL }}api/v1/login-confirm/?token={{ token.token }}'
        ),
        AUTHZ_SIGNUP: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'You are now becoming part of the CrewBoss Network.\n'
            'Click here to confirm your account and email address: \n'
            '{{ SITE_URL }}api/v1/email-confirm/?token={{ token.token }}'
        ),
        AUTHZ_INVITE: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'You have been invited {% if token.sender %}by '
            '{% if token.sender_role %}{{ token.sender_role.user.get_full_name }} of {% endif %}'
            '{{ token.sender }} {% endif %}'
            'to manage your construction jobs in our program.\n'
            'Click here to confirm your account and email address: \n'
            '{{ SITE_URL }}api/v1/email-confirm/?token={{ token.token }}'
        ),
        AUTHZ_PASSWORD_RESET: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'Click here to reset your password: '
            '{{ SITE_URL }}api/v1/reset-confirm/?token={{ token.token }}'
        ),
        AUTHZ_TASK_ACKNOWLEDGE_REQUEST: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'You have been invited {% if token.sender %}by '
            '{% if token.sender_role %}{{ token.sender_role.user.get_full_name }} of {% endif %}'
            '{{ token.sender }} {% endif %}'
            'to manage the task: {{ token.participation.task.name }}.\n'
            '- Job: {{ token.participation.task.job }}\n'
            '- Subdivision: {{ token.participation.task.job.subdivision.name|default:"" }}\n'
            '- Lot Number: #{{ token.participation.task.job.lot_number|default:"" }}\n'
            '{% if token.participation.task.category != None %}- Category: {{ token.participation.task.category }}'
            '{% if token.participation.task.subcategory != None %} / ' '{{ token.participation.task.subcategory }}'
            '{% endif %}\n{% endif %}'
            '- Start Date: {{ token.participation.task.start_date|date:"m/d/Y"|default:"" }}\n'
            '- End Date: {{ token.participation.task.end_date|date:"m/d/Y"|default:"" }}\n'
            '- Start Time: {{ token.participation.task.start_time|date:"H:i"|default:"" }}\n'
            '- End Time: {{ token.participation.task.end_time|date:"H:i"|default:"" }}\n'
            'Would you like to:\n'
            '- Accept{% if token.participation.response == token.participation.RESPONSE_ACCEPTED %} '
            '(Selected){% endif %}: {{ SITE_URL }}api/v1/task/accept/?token={{ token.token }}\n'
            '- Reject{% if token.participation.response == token.participation.RESPONSE_REJECTED %} '
            '(Selected){% endif %}: {{ SITE_URL }}api/v1/task/reject/?token={{ token.token }}\n'
            '- Reschedule: {{ SITE_URL }}api/v1/task/review/?token={{ token.token }}'
        ),
        AUTHZ_TASK_UPDATE_GENERAL: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'Your task has been updated{% if token.sender %} by '
            '{% if token.sender_role %}{{ token.sender_role.user.get_full_name }} of {% endif %}'
            '{{ token.sender }}{% endif %}: {{ token.participation.task.name }}.\n'
            '- Job: {{ token.participation.task.job }}\n'
            '{% if token.participation.task.category != None %}- Category: {{ token.participation.task.category }}'
            '{% if token.participation.task.subcategory != None %} / {{ token.participation.task.subcategory }}'
            '{% endif %}\n{% endif %}'
            'Would you like to:\n'
            '- Accept{% if token.participation.response == token.participation.RESPONSE_ACCEPTED %} '
            '(Selected){% endif %}: {{ SITE_URL }}api/v1/task/accept/?token={{ token.token }}\n'
            '- Reject{% if token.participation.response == token.participation.RESPONSE_REJECTED %} '
            '(Selected){% endif %}: {{ SITE_URL }}api/v1/task/reject/?token={{ token.token }}\n'
            '- Reschedule: {{ SITE_URL }}api/v1/task/review/?token={{ token.token }}'
        ),
        AUTHZ_TASK_UPDATE_SCHEDULE: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'Your task\'s schedule has been updated{% if token.sender %} by '
            '{% if token.sender_role %}{{ token.sender_role.user.get_full_name }} of {% endif %}'
            '{{ token.sender }}{% endif %}: {{ token.participation.task.name }}.\n'
            '- Job: {{ token.participation.task.job }}\n'
            '{% if token.participation.task.category != None %}- Category: {{ token.participation.task.category }}'
            '{% if token.participation.task.subcategory != None %} / {{ token.participation.task.subcategory }}'
            '{% endif %}\n{% endif %}'
            '- Start Date: {{ token.participation.task.start_date|date:"m/d/Y"|default:"" }}\n'
            '- End Date: {{ token.participation.task.end_date|date:"m/d/Y"|default:"" }}\n'
            '- Start Time: {{ token.participation.task.start_time|date:"H:i"|default:"" }}\n'
            '- End Time: {{ token.participation.task.end_time|date:"H:i"|default:"" }}\n'
            'Would you like to:\n'
            '- Accept{% if token.participation.response == token.participation.RESPONSE_ACCEPTED %} '
            '(Selected){% endif %}: {{ SITE_URL }}api/v1/task/accept/?token={{ token.token }}\n'
            '- Reject{% if token.participation.response == token.participation.RESPONSE_REJECTED %} '
            '(Selected){% endif %}: {{ SITE_URL }}api/v1/task/reject/?token={{ token.token }}\n'
            '- Reschedule: {{ SITE_URL }}api/v1/task/review/?token={{ token.token }}\n'
        ),
        AUTHZ_TASK_REMOVE: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'You are no longer assigned to the task: {{ token.participation.task.name }}.\n'
            '- Job: {{ token.participation.task.job }}\n'
            '{% if token.participation.task.category != None %}- Category: {{ token.participation.task.category }}'
            '{% if token.participation.task.subcategory != None %} / {{ token.participation.task.subcategory }}'
            '{% endif %}\n{% endif %}'
            '- Start Date: {{ token.participation.task.start_date|date:"m/d/Y"|default:"" }}\n'
            '- End Date: {{ token.participation.task.end_date|date:"m/d/Y"|default:"" }}\n'
            'Would you like to:\n'
            '- Reschedule: {{ SITE_URL }}api/v1/task/review/?token={{ token.token }}'
        ),
        AUTHZ_TASK_STATUS_UPDATE: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'Your participation with {{ token.participation.task.name }} '
            'has been updated to {{ token.participation.get_response_display }}{% if token.sender %} by '
            '{% if token.sender_role %}{{ token.sender_role.user.get_full_name }} of {% endif %}'
            '{{ token.sender }}{% endif %}.\n'
            '- Job: {{ token.participation.task.job }}\n'
            '{% if token.participation.task.category != None %}- Category: {{ token.participation.task.category }}'
            '{% if token.participation.task.subcategory != None %} / {{ token.participation.task.subcategory }}'
            '{% endif %}\n{% endif %}'
            '- Start Date: {{ token.participation.task.start_date|date:"m/d/Y"|default:"" }}\n'
            '- End Date: {{ token.participation.task.end_date|date:"m/d/Y"|default:"" }}\n'
            '- Start Time: {{ token.participation.task.start_time|date:"H:i"|default:"" }}\n'
            '- End Time: {{ token.participation.task.end_time|date:"H:i"|default:"" }}\n'
            'Would you like to:\n'
            '- Review: {{ SITE_URL }}api/v1/task/review/?token={{ token.token }}'
        ),
        AUTHZ_TASK_REMINDER: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'Your task: {{ token.participation.task.name }} is starting soon!.\n'
            '- Job: {{ token.participation.task.job }}\n'
            '{% if token.participation.task.category != None %}- Category: {{ token.participation.task.category }}'
            '{% if token.participation.task.subcategory != None %} / {{ token.participation.task.subcategory }}'
            '{% endif %}\n{% endif %}'
            '- Start Date: {{ token.participation.task.start_date|date:"m/d/Y"|default:"" }}\n'
            '- End Date: {{ token.participation.task.end_date|date:"m/d/Y"|default:"" }}\n'
            'Would you like to:\n'
            '- Review: {{ SITE_URL }}api/v1/task/review/?token={{ token.token }}'
        ),
        AUTHZ_TASK_REJECT: (
            'Greetings from CrewBoss, {{ token.user.first_name }}! '
            'Your task\'s schedule has been put to pending: {{ token.participation.task.name }}.\n'
            'Because {{ extra_context.rejector.role_display }}: {{ extra_context.rejector.name }} '
            'rejected the schedule.\n'
            'A new date will be pending.\n'
            '- Job: {{ token.participation.task.job }}\n'
            '{% if token.participation.task.category != None %}- Category: {{ token.participation.task.category }}'
            '{% if token.participation.task.subcategory != None %} / {{ token.participation.task.subcategory }}'
            '{% endif %}\n{% endif %}'
            '- Start Date: {{ token.participation.task.start_date|date:"m/d/Y"|default:"" }}\n'
            '- End Date: {{ token.participation.task.end_date|date:"m/d/Y"|default:"" }}\n'
            '- Start Time: {{ token.participation.task.start_time|date:"H:i"|default:"" }}\n'
            '- End Time: {{ token.participation.task.end_time|date:"H:i"|default:"" }}\n'
            'Would you like to:\n'
            '- Review: {{ SITE_URL }}api/v1/task/review/?token={{ token.token }}\n'
        ),
        AUTHZ_TASK_SUGGEST_SCHEDULE: (
            'Greetings from CrewBoss, {{ token.user.first_name }}!\n'
            '{{ extra_context.suggester_role }}: {{ extra_context.suggestion.participation.user }} '
            'suggested a new schedule for your task {{ token.participation.task.name}}.\n'
            '- Job: {{ token.participation.task.job }}\n'
            '{% if token.participation.task.category != None %}- Category: {{ token.participation.task.category }}'
            '{% if token.participation.task.subcategory != None %} / {{ token.participation.task.subcategory }}'
            '{% endif %}\n{% endif %}'
            '- Start Time: {{ token.participation.task.start_time|date:"H:i"|default:"" }}\n'
            '- End Time: {{ token.participation.task.end_time|date:"H:i"|default:"" }}\n'
            'Original Schedule:\n'
            '- Start Date: {{ token.participation.task.start_date|date:"m/d/Y"|default:"" }}\n'
            '- End Date: {{ token.participation.task.end_date|date:"m/d/Y"|default:"" }}\n'
            'Suggested Schedule:\n'
            '- Start Date: {{ extra_context.suggestion.start_date|date:"m/d/Y"|default:"" }}\n'
            '- End Date: {{ extra_context.suggestion.end_date|date:"m/d/Y"|default:"" }}\n'
            'Would you like to:\n'
            '- Accept{% if token.participation.response == token.participation.RESPONSE_ACCEPTED %} '
            '(Selected){% endif %}: {{ SITE_URL }}api/v1/task/accept-suggestion/?token={{ token.token }}'
            '&sid={{ extra_context.suggestion.id }}\n'
            '- Reject{% if token.participation.response == token.participation.RESPONSE_REJECTED %} '
            '(Selected){% endif %}: {{ SITE_URL }}api/v1/task/reject-suggestion/?token={{ token.token }}'
            '&sid={{ extra_context.suggestion.id }}\n'
            '- Review: {{ SITE_URL }}api/v1/task/review-suggestion/?token={{ token.token }}'
            '&sid={{ extra_context.suggestion.id }}\n'
        ),
        AUTHZ_USER_LOCKED_OUT: (
            'Greetings from CrewBoss, {{ token.user.first_name }}!\n'
            'Someone is trying to log in to your account from {{token.user.login_attempts.first.ip_address}} '
            '({{token.user.login_attempts.first.location}}).\n'
            'Your account has been locked for one hour to prevent further attempts.\n'
            'No one will be able to log in to your account in this period, '
            'but you can secure your account by changing your password.'
        ),
    }

    TEXT_MESSAGE_BODIES = dict(EMAIL_MESSAGE_BODIES)
    TEXT_MESSAGE_BODIES[AUTHZ_SIGNUP] = (
        'Greetings from CrewBoss, {{ token.user.first_name }}! '
        'Click here to confirm your account and mobile number: '
        '{{ SITE_URL }}api/v1/text-confirm/?token={{ token.token }}'
    )
    TEXT_MESSAGE_BODIES[AUTHZ_INVITE] = (
        'Greetings from CrewBoss, {{ token.user.first_name }}! '
        'Click here to confirm your account and mobile number: '
        '{{ SITE_URL }}api/v1/text-confirm/?token={{ token.token }}'
    )
    for type in [AUTHZ_TASK_ACKNOWLEDGE_REQUEST, AUTHZ_TASK_UPDATE_GENERAL, AUTHZ_TASK_UPDATE_SCHEDULE]:
        TEXT_MESSAGE_BODIES[type] = TEXT_MESSAGE_BODIES[type].replace('    - ', '- ')

    user = models.ForeignKey(User, related_name='tokens')
    token = models.CharField(max_length=1024)
    timestamp_created = models.DateTimeField()
    timestamp_expires = models.DateTimeField()
    authz_type = models.PositiveSmallIntegerField(choices=AUTHZ_OPTIONS)
    participation = models.ForeignKey('construction.Participation', related_name='auth_tokens', null=True, blank=True)
    sender = models.ForeignKey('construction.Company', related_name='auth_tokens', null=True, blank=True)
    sender_role = models.ForeignKey('construction.CompanyRole', related_name='auth_tokens', null=True, blank=True)

    class Meta:
        ordering = ('-pk',)

    class InvalidTokenException(Exception):
        pass

    class BothNotificationFailedException(Exception):
        pass

    @classmethod
    def check_token(cls, token, authz_type):
        authz_types = authz_type if isinstance(authz_type, (list, tuple)) else [authz_type]
        try:
            return cls.objects.get(token=token, timestamp_expires__gte=timezone.now(), authz_type__in=authz_types)
        except cls.DoesNotExist:
            raise cls.InvalidTokenException()

    @classmethod
    def make_token(cls, user, sender=None, sender_role=None, authz_type=AUTHZ_PASSWORD_RESET, participation=None):
        now = timezone.now()

        token = ''.join(random.choices(ascii_letters + digits, k=settings.AUTH_TOKEN_TOKEN_LENGTH))
        while cls.objects.filter(token=token).exists():
            token = ''.join(random.choices(ascii_letters + digits, k=settings.AUTH_TOKEN_TOKEN_LENGTH))

        return cls.objects.create(
            sender=sender,
            sender_role=sender_role,
            user=user,
            token=token,
            timestamp_created=now,
            timestamp_expires=now + cls.EXPIRY_DURATIONS[authz_type],
            authz_type=authz_type,
            participation=participation,
        )

    def send_message(self, force_first_send=False, extra_context=None):
        from construction.models import Message
        context = {'SITE_URL': settings.SITE_URL, 'token': self, 'extra_context': extra_context}
        has_sms_error = False
        has_smtp_error = False
        try:
            if self.user.enable_text_notifications or force_first_send:
                Message.objects.create(
                    timestamp=timezone.now(),
                    type=Message.TYPE_SMS,
                    subject=self.MESSAGE_SUBJECTS[self.authz_type],
                    body=Template(self.TEXT_MESSAGE_BODIES[self.authz_type]).render(Context(context)),
                    task=self.participation.task if self.participation else None,
                    user=self.user,
                    reason=self.authz_type,
                    sender=self.sender,
                ).send()
        except TwilioClientException:
            has_sms_error = True
        try:
            if self.user.enable_email_notifications or force_first_send:
                message = Message.objects.create(
                            timestamp=timezone.now(),
                            type=Message.TYPE_EMAIL,
                            subject=self.MESSAGE_SUBJECTS[self.authz_type],
                            body=Template(self.EMAIL_MESSAGE_BODIES[self.authz_type]).render(Context(context)),
                            task=self.participation.task if self.participation else None,
                            user=self.user,
                            reason=self.authz_type,
                            sender=self.sender,
                          )
                subject, from_email, to = message.subject, settings.DEFAULT_FROM_EMAIL, message.user.email
                html_content = loader.render_to_string(self.EMAIL_MESSAGE_TEMPLATE_BODIES[self.authz_type], context)
                text_content = strip_tags(html_content)
                email = EmailMultiAlternatives(subject, text_content, from_email, [to])
                email.attach_alternative(html_content, "text/html")
                email.send()
        except Exception:
            has_smtp_error = True

        if not has_smtp_error and has_sms_error:
            raise TwilioClientException()
        if has_smtp_error and not has_sms_error:
            raise SMTPException()
        if has_smtp_error and has_sms_error:
            raise self.BothNotificationFailedException()

    # def send_message_to_crew_staff(self):
    #     from construction.models import Message
    #     if settings.SEND_MESSAGES_TO_ADMIN:
    #         return
    #     context = Context({'SITE_URL': settings.SITE_URL, 'token': self})
    #     for crew_staff in self.user.crew_leader.crew_staff.all():
    #         Message.objects.create(
    #             timestamp=timezone.now(),
    #             type=Message.TYPE_SMS,
    #             subject=self.MESSAGE_SUBJECTS[self.authz_type],
    #             body=re.sub(
    #                 r'Would you like to:[\s\S]+',
    #                 '',
    #                 Template(self.TEXT_MESSAGE_BODIES[self.authz_type]).render(context)
    #             ),
    #             task=self.participation.task if self.participation else None,
    #             user=crew_staff.user,
    #             reason=self.authz_type,
    #         ).send()
    #         Message.objects.create(
    #             timestamp=timezone.now(),
    #             type=Message.TYPE_EMAIL,
    #             subject=self.MESSAGE_SUBJECTS[self.authz_type],
    #             body=re.sub(
    #                 r'Would you like to:[\s\S]+',
    #                 '',
    #                 Template(self.EMAIL_MESSAGE_BODIES[self.authz_type]).render(context)
    #             ),
    #             task=self.participation.task if self.participation else None,
    #             user=crew_staff.user,
    #             reason=self.authz_type,
    #         ).send()


class LoginAttempt(models.Model):
    """
    Records login of user wether failed or succeed
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_attempts')
    is_succesful = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return '{} | {}'.format(self.user, 'Success' if self.is_succesful else 'Failed')
