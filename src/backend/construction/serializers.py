import random
from datetime import timedelta
from string import ascii_letters, digits

from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers

from account.models import LoginAttempt, User

from . import models


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    mobile_number_display = serializers.CharField(read_only=True)
    active_plan_display = serializers.CharField(source='get_active_plan_display', read_only=True)
    active_plan_prefix = serializers.CharField(read_only=True)
    accepted = serializers.SerializerMethodField(read_only=True)
    # user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    # user_type = serializers.ChoiceField(choices=User.USER_TYPES)
    # company_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    # crew_leader_for_staff = serializers.PrimaryKeyRelatedField(
    #     queryset=models.User.objects.filter(crew_leader__isnull=False), required=False, allow_null=True)
    # crew_staff = serializers.SerializerMethodField(read_only=True)
    # role_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'mobile_number', 'first_name', 'last_name', 'is_active',
            'enable_text_notifications', 'enable_email_notifications',
            'full_name', 'mobile_number_display', 'active_plan', 'active_plan_display', 'active_plan_prefix',
            'expiry_date', 'has_autorenew', 'accepted'
        )

    def validate(self, data):
        if not data.get('email') and not data.get('mobile_number'):
            raise serializers.ValidationError('Need to have either email or mobile number')

    #     if not self.context.get('signup'):
    #         if self.context['request'].user.is_superuser:
    #             if data.get('user_type') == User.CREW_STAFF:
    #                 if 'crew_leader' not in data:
    #                     raise serializers.ValidationError(
    #                       'Subcontractor required when a superuser creates a crew staff'
    #                     )
    #             else:
    #                 if 'contractor' not in data:
    #                     raise serializers.ValidationError('Contractor required when a superuser creates another user')
    #
    #         if data.get('user_type') == User.BUILDER and not data.get('company_name'):
    #             raise serializers.ValidationError({'company_name': 'Company name is required for builders'})
    #     else:

        if self.context.get('signup'):
            if (
                data.get('mobile_number') and
                User.objects.filter(mobile_number=data['mobile_number'], is_active=True).exists()
            ):
                raise serializers.ValidationError('Active user with that number already exists')
        elif self.instance:
            if (
                data.get('mobile_number') and data.get('is_active') and
                User.objects.exclude(id=self.instance.id).filter(
                    mobile_number=data['mobile_number'], is_active=True
                ).exists()
            ):
                raise serializers.ValidationError('Active user with that number already exists')
        return super().validate(data)

    def save(self):
        if not self.instance:
            unusable_password = ''.join(random.choices(ascii_letters + digits, k=128))
            self.validated_data['password'] = unusable_password
        user = super().save()
        return user

    #     user_type = self.validated_data.pop('user_type')
    #     company_name = self.validated_data.pop('company_name')
    #     crew_leader_for_staff = self.validated_data.pop('crew_leader_for_staff', None)
    #
    #     if self.context.get('signup'):
    #         contractor = models.Contractor.objects.create(name=company_name)
    #         self.validated_data['is_active'] = False  # All new users start as inactive (cannot login)
    #     else:
    #         # Extract contractor if superuser, get own contractor if contractor admin
    #         current_user = self.context['request'].user
    #         if current_user.user_type == 'superuser':
    #             contractor_id = self.validated_data.pop('contractor')
    #             contractor = models.Contractor.objects.get(id=contractor_id)
    #         elif current_user.user_type == User.CONTRACTOR_ADMIN:
    #             contractor = current_user.crew_leader.contractor
    #         else:
    #             contractor = None
    #
    #     created = not(self.instance)
    #     if self.instance:
    #         old_user_type = self.instance.user_type
    #         if old_user_type != user_type:
    #             models.CrewLeader.objects.filter(user=self.instance).update(is_active=False)
    #             models.CrewStaff.objects.filter(user=self.instance).update(is_active=False)
    #             models.Superintendent.objects.filter(user=self.instance).update(is_active=False)
    #             models.Builder.objects.filter(user=self.instance).update(is_active=False)
    #     else:
    #         unusable_password = ''.join(random.choices(ascii_letters + digits, k=128))
    #         self.validated_data['password'] = unusable_password
    #
    #     user = super().save()
    #     if created:
    #         user.set_password(''.join(random.choices(ascii_letters + digits, k=128)))
    #         user.save()
    #
    #     if user_type == User.CONTRACTOR_ADMIN:
    #         models.CrewLeader.objects.update_or_create(
    #             user=user, contractor=contractor, is_admin=True, defaults={'is_active': True})
    #     elif user_type == User.CREW_LEADER:
    #         models.CrewLeader.objects.update_or_create(
    #             user=user, contractor=contractor, is_admin=False, defaults={'is_active': True})
    #     elif user_type == User.CREW_STAFF:
    #         crew_leader = crew_leader_for_staff.crew_leader
    #         models.CrewStaff.objects.update_or_create(
    #             user=user, defaults={'crew_leader': crew_leader, 'is_active': True})
    #     elif user_type == User.SUPERINTENDENT:
    #         models.Superintendent.objects.update_or_create(
    #             user=user, contractor=contractor, defaults={'is_active': True})
    #     elif user_type == User.BUILDER:
    #         models.Builder.objects.update_or_create(
    #             user=user, contractor=contractor, defaults={'name': company_name, 'is_active': True})
    #
    #     return user

    # def get_crew_staff(self, obj):
    #     if obj.user_type == 'contractor-admin' or obj.user_type == 'crew-leader':
    #         return NestedCrewStaffSerializer(obj.crew_leader.crew_staff.all(), many=True).data
    #     return []
    #
    # def get_role_id(self, obj):
    #     if obj.user_type == 'contractor-admin' or obj.user_type == 'crew-leader':
    #         return obj.crew_leader.id
    #     elif obj.user_type == 'superintendent':
    #         return obj.superintendent.id
    #     elif obj.user_type == 'builder':
    #         return obj.builder.id
    #     return None

    def get_accepted(self, obj):
        return obj.enable_email_notifications or obj.enable_text_notifications


class LoginAttemptSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoginAttempt
        fields = ('is_succesful', 'ip_address', 'date')


class CompanySerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    non_working_days_in_day_of_week = serializers.JSONField(read_only=True)

    class Meta:
        model = models.Company
        fields = "__all__"


class CompanyRoleSettingsSerializer(serializers.ModelSerializer):
    company_reminder_time = serializers.TimeField(source='company.reminder_time')
    enable_text_notifications = serializers.BooleanField(source='user.enable_text_notifications')
    enable_email_notifications = serializers.BooleanField(source='user.enable_email_notifications')

    class Meta:
        model = models.CompanyRole
        fields = (
            'id', 'default_calendar_filter', 'company_reminder_time', 'page_size',
            'enable_text_notifications', 'enable_email_notifications'
        )


class SimpleCompanyRoleSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = models.CompanyRole
        fields = ('id', 'company_name')


class CompanyRoleSerializer(serializers.ModelSerializer):
    user_types_display = serializers.CharField(read_only=True)
    user_types_other_display = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_type = serializers.CharField(source='company.get_type_display', read_only=True)
    company_state = serializers.CharField(source='company.state', read_only=True)
    company_reminder_time = serializers.TimeField(source='company.reminder_time', required=False)
    company_non_working_days_in_day_of_week = serializers.JSONField(source='company.non_working_days_in_day_of_week', read_only=True)
    user_enable_text_notifications = serializers.BooleanField(source='user.enable_text_notifications', required=False)
    user_enable_email_notifications = serializers.BooleanField(source='user.enable_email_notifications', required=False)

    class Meta:
        model = models.CompanyRole
        fields = "__all__"

    def validate(self, data):
        user_data = self.initial_data.get('user', {})
        user = self.instance.user if self.instance else None
        UserSerializer(instance=user, data=user_data).is_valid(raise_exception=True)

        return super().validate(data)

    def save(self):
        company_reminder_time = self.validated_data.pop('company', {}).pop('reminder_time', None)
        user_enable_text_notifications = self.initial_data.pop('enable_text_notifications', False)
        user_enable_email_notifications = self.initial_data.pop('enable_email_notifications', False)
        user = self.initial_data.pop('user', {})

        instance = super().save()

        if company_reminder_time:
            instance.company.reminder_time = company_reminder_time
            instance.company.save()
        if user_enable_text_notifications is not None:
            instance.user.enable_text_notifications = user_enable_text_notifications
        if user_enable_email_notifications is not None:
            instance.user.enable_email_notifications = user_enable_email_notifications
        if user:
            for field in User._meta.get_fields():
                if field.name in user:
                    setattr(instance.user, field.name, user[field.name])
        instance.user.save()
        return instance


# class NestedCrewStaffSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)
#
#     class Meta:
#         model = models.CrewStaff
#         fields = "__all__"


class SubdivisionSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = models.Subdivision
        fields = "__all__"


class NestedContactSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    role = CompanyRoleSerializer(read_only=True)
    contact_type = serializers.SerializerMethodField(read_only=True)
    mobile_number_display = serializers.CharField(read_only=True)

    class Meta:
        model = models.Contact
        fields = "__all__"

    def get_contact_type(self, obj):
        if obj.task:
            return 'Task'
        elif obj.job:
            return 'Job'


class NoteTimelineSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    note_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Note
        fields = "__all__"

    def get_note_type(self, obj):
        if obj.task:
            return 'Task'
        elif obj.job:
            return 'Job'


class NestedDocumentSerializer(serializers.ModelSerializer):
    file_type = serializers.CharField(read_only=True)
    file_name = serializers.CharField(read_only=True)

    class Meta:
        model = models.Document
        fields = "__all__"


class ReminderSerializer(serializers.ModelSerializer):
    reminder_days_display = serializers.CharField(source='get_reminder_days_display', read_only=True)

    class Meta:
        model = models.Reminder
        fields = "__all__"


class DefaultRemindersSerializer(serializers.ModelSerializer):
    reminder_days_display = serializers.CharField(source='get_reminder_days_display', read_only=True)

    class Meta:
        model = models.DefaultReminders
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    owner_non_working_days_in_day_of_week = serializers.JSONField(read_only=True)
    location = serializers.CharField(read_only=True)
    subdivision_name = serializers.CharField(source='subdivision.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    builder_name = serializers.CharField(source='builder.user.get_full_name', read_only=True)
    subcontractor_name = serializers.CharField(source='subcontractor.user.get_full_name', read_only=True)
    superintendent_name = serializers.CharField(source='superintendent.user.get_full_name', read_only=True)
    builder_data = CompanyRoleSerializer(source='builder', read_only=True)
    subcontractor_data = CompanyRoleSerializer(source='subcontractor', read_only=True)
    superintendent_data = CompanyRoleSerializer(source='superintendent', read_only=True)
    roles = CompanyRoleSerializer(many=True, read_only=True)
    contacts = NestedContactSerializer(many=True, read_only=True)
    notes = NoteTimelineSerializer(many=True, read_only=True)
    documents = NestedDocumentSerializer(many=True, read_only=True)

    note_text = serializers.CharField(required=False, allow_blank=True, write_only=True)
    custom_subdivision = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = models.Job
        fields = "__all__"

    def validate(self, data):
        if data.get('custom_subdivision') and data.get('subdivision'):
            raise serializers.ValidationError("Cannot set both subdivision and custom subdivision")
        if data.get('custom_subdivision') and not data.get('owner') and not self.instance:
            raise serializers.ValidationError("Cannot create new subdivision without an account holder")
        return data

    def save(self):
        if self.initial_data.get('existing'):
            self.instance = job = models.Job.objects.get(id=self.initial_data['existing'])
            job = super().save()
        else:
            note_text = self.validated_data.pop('note_text', '')

            custom_subdivision = self.validated_data.pop('custom_subdivision', '')
            if custom_subdivision:
                company = self.context['view'].request.user.roles.first().company
                self.validated_data['subdivision'] = models.Subdivision.objects.create(
                    company=company, name=custom_subdivision)

            job = super().save()

            if note_text:
                now = timezone.now()
                models.Note.objects.create(
                    text=note_text, job=job, created_timestamp=now, modified_timestamp=now,
                    author=self.context['view'].request.user,
                )

            if job.builder:
                job.roles.add(job.builder)
            if job.subcontractor:
                job.roles.add(job.subcontractor)
            if job.superintendent:
                job.roles.add(job.superintendent)
        job.roles.add(self.context['view'].request.role)
        return job


class TaskParticipationSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_type = serializers.CharField(source='user.get_user_type_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = models.Participation
        fields = "__all__"


class TaskCategorySerializer(serializers.ModelSerializer):
    pass

    class Meta:
        model = models.TaskCategory
        fields = "__all__"


class TaskSubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = models.TaskSubCategory
        fields = "__all__"


class TaskListSerializer(serializers.ModelSerializer):
    job_data = JobSerializer(source='job', read_only=True)
    job_is_archived = serializers.BooleanField(source='job.is_archived', read_only=True)
    subcontractor_name = serializers.CharField(source='subcontractor.user.get_full_name', read_only=True)
    superintendent_name = serializers.CharField(source='superintendent.user.get_full_name', read_only=True)
    builder_name = serializers.CharField(source='builder.user.get_full_name', read_only=True)
    job_address = serializers.CharField(source='job.street_address', read_only=True)
    lot_number = serializers.CharField(source='job.lot_number', read_only=True)
    participant_statuses = serializers.SerializerMethodField(read_only=True)
    has_queued_notification = serializers.BooleanField(read_only=True)
    duration = serializers.IntegerField(required=False)
    non_working_days_in_day_of_week = serializers.JSONField(read_only=True)

    class Meta:
        model = models.Task
        fields = "__all__"

    def get_participant_statuses(self, obj):
        return TaskSerializer().get_participant_statuses(obj)


class TaskSerializer(serializers.ModelSerializer):
    job_is_archived = serializers.BooleanField(source='job.is_archived', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    job_data = JobSerializer(source='job', read_only=True)
    subcontractor_data = CompanyRoleSerializer(source='subcontractor', read_only=True)
    superintendent_data = CompanyRoleSerializer(source='superintendent', read_only=True)
    builder_data = CompanyRoleSerializer(source='builder', read_only=True)
    subcontractor_name = serializers.CharField(source='subcontractor.user.get_full_name', read_only=True)
    superintendent_name = serializers.CharField(source='superintendent.user.get_full_name', read_only=True)
    builder_name = serializers.CharField(source='builder.user.get_full_name', read_only=True)
    job_location = serializers.CharField(source='job.location', read_only=True)
    job_address = serializers.CharField(source='job.street_address', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    participant_statuses = serializers.SerializerMethodField(read_only=True)
    duration = serializers.IntegerField(required=False)
    between = serializers.CharField(read_only=True)
    participants = TaskParticipationSerializer(many=True, read_only=True)
    contacts = NestedContactSerializer(many=True, read_only=True)
    all_contacts = NestedContactSerializer(many=True, read_only=True)
    notes = NoteTimelineSerializer(many=True, read_only=True)
    all_notes = NoteTimelineSerializer(many=True, read_only=True)
    documents = NestedDocumentSerializer(many=True, read_only=True)
    reminders = ReminderSerializer(many=True, read_only=True)
    has_queued_notification = serializers.BooleanField(read_only=True)
    author_display = serializers.SerializerMethodField()

    note_text = serializers.CharField(required=False, allow_blank=True, write_only=True)
    custom_category = serializers.CharField(required=False, allow_blank=True, write_only=True)
    custom_subcategory = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = models.Task
        fields = "__all__"

    def get_author_display(self, obj):
        if obj.author:
            return f'{obj.author.first_name} {obj.author.last_name}'
        return None

    def get_participant_statuses(self, obj):
        data = []

        b_data = {'label': 'B', 'status': 'default', 'participation_id': None}
        if obj.builder:
            participation = obj.participants.filter(user=obj.builder.user).first()
            if participation:
                b_data['status'] = slugify(participation.get_response_display())
                b_data['participation_id'] = participation.id
        data.append(b_data)

        cl_data = {'label': 'SC', 'status': 'default', 'participation_id': None}
        if obj.subcontractor:
            participation = obj.participants.filter(user=obj.subcontractor.user).first()
            if participation:
                cl_data['status'] = slugify(participation.get_response_display())
                cl_data['participation_id'] = participation.id
        data.append(cl_data)

        si_data = {'label': 'CR', 'status': 'default', 'participation_id': None}
        if obj.superintendent:
            participation = obj.participants.filter(user=obj.superintendent.user).first()
            if participation:
                si_data['status'] = slugify(participation.get_response_display())
                si_data['participation_id'] = participation.id
        data.append(si_data)

        return data

    def validate(self, data):
        if data.get('start_date'):
            non_working_days = []
            if data.get('job') and data['job'].owner:
                # handles task form
                non_working_days = data['job'].owner.non_working_days
            elif self.instance and self.instance.job.owner:
                # handles calendar events
                non_working_days = self.instance.job.owner.non_working_days

            if data['start_date'].strftime('%A') in non_working_days:
                raise serializers.ValidationError("Cannot set start date to a non working day")

            if data.get('end_date') and data['start_date'] > data['end_date']:
                raise serializers.ValidationError("Cannot set end date before start date")

        if data.get('custom_category') and data.get('category'):
            raise serializers.ValidationError("Cannot set both category and custom category")
        if data.get('custom_subcategory') and data.get('subcategory'):
            raise serializers.ValidationError("Cannot set both subcategory and custom subcategory")

        if data.get('subcategory') or data.get('custom_subcategory'):
            if not data.get('category') and not data.get('custom_category'):
                raise serializers.ValidationError("Cannot set subcategory without category")
        return data

    def save(self, **kwargs):
        if self.validated_data.get('start_date'):
            duration = None
            non_working_days = []
            if self.validated_data.get('job') and self.validated_data['job'].owner:
                # handles task form
                non_working_days = self.validated_data['job'].owner.non_working_days
            elif self.instance and self.instance.job.owner:
                # handles calendar events
                non_working_days = self.instance.job.owner.non_working_days

            if self.validated_data.get('duration'):
                # handles task form
                duration = self.validated_data['duration']
            elif self.instance and self.instance.duration:
                # handles calendar events
                duration = self.instance.duration

            if duration:
                # computation for end_date will start with start_date
                end_date = self.validated_data['start_date']
                # we don't add the first day
                duration = duration - 1
                for i in range(int(duration)):
                    end_date = end_date + timedelta(days=1)
                    while end_date.strftime('%A') in non_working_days:
                        end_date = end_date + timedelta(days=1)
                self.validated_data['end_date'] = end_date

        if 'author' in kwargs:
            self.validated_data['author'] = kwargs.pop('author')

        note_text = self.validated_data.pop('note_text', '')

        custom_category = self.validated_data.pop('custom_category', '')
        if custom_category:
            job = self.validated_data.get('job') or self.instance.job
            self.validated_data['category'] = models.TaskCategory.objects.create(
                contractor=job.owner, name=custom_category)
        custom_subcategory = self.validated_data.pop('custom_subcategory', '')
        if custom_subcategory:
            category = self.validated_data.get('category') or self.instance.category
            self.validated_data['subcategory'] = models.TaskSubCategory.objects.create(
                category=category, name=custom_subcategory)

        changes = self.collect_changes()

        task = super().save()
        new_participants = task.make_participants()

        # Add/update pending message
        if new_participants and not task.is_completed:
            models.NotificationQueue.queue_notification(task, models.NotificationQueue.TYPE_INVITES_ONLY)
        if changes['general']:
            models.NotificationQueue.queue_notification(task, models.NotificationQueue.TYPE_GENERAL)
        if changes['schedule']:
            task.participants_to_pending()
            task.refresh_from_db()
            models.NotificationQueue.queue_notification(task, models.NotificationQueue.TYPE_SCHEDULE)

        task.sync_status()

        # Send removal emails immediately
        for participant in changes['removed']:
            participant.send_remove_message()

        if note_text:
            now = timezone.now()
            models.Note.objects.create(
                text=note_text, task=task, created_timestamp=now, modified_timestamp=now,
                author=self.context['view'].request.user,
            )
        return task

    def collect_changes(self):
        changes = {
            'general': False,
            'schedule': False,
            'removed': [],
        }
        if not self.instance:
            return changes

        if (
            ('name' in self.validated_data and self.instance.name != self.validated_data['name']) or
            ('job' in self.validated_data and self.instance.job != self.validated_data['job']) or
            ('category' in self.validated_data and self.instance.category != self.validated_data['category']) or
            ('subcategory' in self.validated_data and self.instance.subcategory != self.validated_data['subcategory'])
        ):
            changes['general'] = True

        if (
            ('start_date' in self.validated_data and self.instance.start_date != self.validated_data['start_date']) or
            ('end_date' in self.validated_data and self.instance.end_date != self.validated_data['end_date']) or
            ('start_time' in self.validated_data and self.instance.start_time != self.validated_data['start_time']) or
            ('end_time' in self.validated_data and self.instance.end_time != self.validated_data['end_time'])
        ):
            changes['schedule'] = True

        if (
            'subcontractor' in self.validated_data and
            self.instance.subcontractor and
            self.instance.subcontractor != self.validated_data['subcontractor']
        ):
            changes['removed'].append(self.instance.participants.get(user=self.instance.subcontractor.user))
        if (
            'superintendent' in self.validated_data and
            self.instance.superintendent and
            self.instance.superintendent != self.validated_data['superintendent']
        ):
            changes['removed'].append(self.instance.participants.get(user=self.instance.superintendent.user))
        if (
            'builder' in self.validated_data and
            self.instance.builder and
            self.instance.builder != self.validated_data['builder']
        ):
            changes['removed'].append(self.instance.participants.get(user=self.instance.builder.user))

        return changes


class ParticipationSerializer(serializers.ModelSerializer):
    task_data = TaskSerializer(read_only=True)
    user_data = UserSerializer(read_only=True)

    class Meta:
        model = models.Participation
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    author_data = UserSerializer(source='author', read_only=True)
    task_data = TaskSerializer(source='task', read_only=True)
    job_data = JobSerializer(source='job', read_only=True)
    contact_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Contact
        fields = "__all__"

    def get_contact_type(self, obj):
        if obj.task:
            return 'Task'
        elif obj.job:
            return 'Job'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'initial_data'):
            self.initial_data = self.initial_data.copy()
            self.initial_data['author'] = self.context['request'].user.id


class NoteSerializer(serializers.ModelSerializer):
    author_data = UserSerializer(source='author', read_only=True)
    task_data = TaskSerializer(source='task', read_only=True)
    job_data = JobSerializer(source='job', read_only=True)
    note_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Note
        fields = "__all__"

    def get_note_type(self, obj):
        if obj.task:
            return 'Task'
        elif obj.job:
            return 'Job'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'initial_data'):
            self.initial_data = self.initial_data.copy()
            self.initial_data['author'] = self.context['request'].user.id


class DocumentSerializer(serializers.ModelSerializer):
    author_data = UserSerializer(read_only=True)
    task_data = TaskSerializer(read_only=True)
    job_data = JobSerializer(read_only=True)

    class Meta:
        model = models.Document
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'initial_data'):
            self.initial_data = self.initial_data.copy()
            self.initial_data['author'] = self.context['request'].user.id


# class CalendarTaskSerializer(serializers.ModelSerializer):
#     job_location = serializers.CharField(source='job.location', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#     participant_statuses = serializers.SerializerMethodField(read_only=True)
#     duration = serializers.IntegerField(required=False)
#     has_queued_notification = serializers.BooleanField(read_only=True)
#
#     class Meta:
#         model = models.Task
#         fields = "__all__"
#
#     def get_participant_statuses(self, obj):
#         data = []
#
#         b_data = {'label': 'B', 'status': 'default', 'participation_id': None}
#         if obj.builder:
#             participation = obj.participants.filter(user=obj.builder.user).first()
#             if participation:
#                 b_data['status'] = slugify(participation.get_response_display())
#                 b_data['participation_id'] = participation.id
#         data.append(b_data)
#
#         cl_data = {'label': 'SC', 'status': 'default', 'participation_id': None}
#         if obj.subcontractor:
#             participation = obj.participants.filter(user=obj.subcontractor.user).first()
#             if participation:
#                 cl_data['status'] = slugify(participation.get_response_display())
#                 cl_data['participation_id'] = participation.id
#         data.append(cl_data)
#
#         si_data = {'label': 'CR', 'status': 'default', 'participation_id': None}
#         if obj.superintendent:
#             participation = obj.participants.filter(user=obj.superintendent.user).first()
#             if participation:
#                 si_data['status'] = slugify(participation.get_response_display())
#                 si_data['participation_id'] = participation.id
#         data.append(si_data)
#
#         return data
#
#
# class CalendarParticipationSerializer(serializers.ModelSerializer):
#     task = CalendarTaskSerializer(read_only=True)
#
#     class Meta:
#         model = models.Participation
#         fields = "__all__"
#
#
# class CalendarUserListSerializer(serializers.ModelSerializer):
#     user_types_display = serializers.CharField(read_only=True)
#     builder_name = serializers.CharField(source='builder.user.get_full_name')
#     participations_weekly = serializers.SerializerMethodField(read_only=True)
#     role_id = serializers.SerializerMethodField(read_only=True)
#
#     class Meta:
#         model = models.CompanyRole
#         fields = (
#             'id', 'email', 'mobile_number', 'first_name', 'last_name', 'is_active', 'user_type', 'builder_name',
#             'participations_weekly', 'role_id', 'user_types_display')
#
#     def get_participations_weekly(self, obj):
#         start_date = self.context['start_date']
#         end_date = self.context['end_date']
#         task_search = self.context['task_search']
#         task_status = self.context['task_status']
#         role = self.context['role']
#
#         if obj.id:
#             if role == 'crew':
#                 tasks = models.Task.objects.filter(subcontractor__user=obj)
#             elif role == 'superintendent':
#                 tasks = models.Task.objects.filter(superintendent__user=obj)
#             elif role == 'builder':
#                 tasks = models.Task.objects.filter(builder__user=obj)
#         else:
#             contractor = self.context['request'].user.subcontractor.contractor
#             tasks = models.Task.objects.filter(job__contractor=contractor)
#             if role == 'crew':
#                 tasks = tasks.filter(subcontractor__isnull=True)
#             elif role == 'superintendent':
#                 tasks = tasks.filter(superintendent__isnull=True)
#             elif role == 'builder':
#                 tasks = tasks.filter(builder__isnull=True)
#
#         tasks = tasks.filter(end_date__gte=start_date, start_date__lte=end_date)
#         if task_search:
#             tasks = tasks.filter(
#                 Q(name__icontains=task_search) |
#                 Q(job__street_address__icontains=task_search) |
#                 Q(job__subdivision__name__icontains=task_search)
#             )
#         if task_status:
#             tasks = tasks.filter(status=task_status)
#
#         # HACK: Wraps tasks into participations because that's what the frontend is looking for
#         participations = [task.participants.first() or models.Participation(task=task) for task in tasks]
#         return CalendarParticipationSerializer(participations, many=True).data
#
#     def get_role_id(self, obj):
#         if obj.user_type == 'contractor-admin' or obj.user_type == 'crew-leader':
#             return obj.subcontractor.id
#         elif obj.user_type == 'superintendent':
#             return obj.superintendent.id
#         elif obj.user_type == 'builder':
#             return obj.builder.id
#         return None
#
#
# class CalendarJobListSerializer(serializers.ModelSerializer):
#     location = serializers.CharField(read_only=True)
#     subdivision_name = serializers.CharField(source='subdivision.name', read_only=True)
#     contractor_name = serializers.CharField(source='contractor.name', read_only=True)
#     superintendent_name = serializers.CharField(source='superintendent.user.get_full_name', read_only=True)
#     builder_name = serializers.CharField(source='builder.user.get_full_name', read_only=True)
#     created_by_name = serializers.CharField(source='created_by.name', read_only=True)
#     owner_name = serializers.CharField(source='owner.name', read_only=True)
#     tasks_weekly = serializers.SerializerMethodField(read_only=True)
#
#     class Meta:
#         model = models.Job
#         fields = "__all__"
#
#     def get_tasks_weekly(self, obj):
#         start_date = self.context['start_date']
#         end_date = self.context['end_date']
#         task_search = self.context['task_search']
#         task_status = self.context['task_status']
#
#         tasks = obj.tasks.filter(end_date__gte=start_date, start_date__lte=end_date)
#         if task_search:
#             tasks = tasks.filter(
#                 Q(name__icontains=task_search) |
#                 Q(job__street_address__icontains=task_search) |
#                 Q(job__subdivision__name__icontains=task_search)
#             )
#         if task_status:
#             tasks = tasks.filter(status=task_status)
#         return CalendarTaskSerializer(tasks, many=True).data


class NotificationQueueSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)
    type_name = serializers.CharField(source='get_type_display', read_only=True)
    key_participants = serializers.SerializerMethodField()

    class Meta:
        model = models.NotificationQueue
        fields = '__all__'

    def get_key_participants(self, obj):
        data = {}
        key_participants = obj.task.key_participants
        subcontractor_participation = key_participants.get('subcontractor')
        superintendent_participation = key_participants.get('superintendent')
        builder_participation = key_participants.get('builder')
        if subcontractor_participation:
            data['subcontractor'] = {
                'id': subcontractor_participation.id,
                'last_notification_timestamp': getattr(subcontractor_participation.user.messages.filter(
                    reason=models.Message.REASON_TASK_ACKNOWLEDGE_REQUEST, task=obj.task,
                ).first(), 'timestamp', None),
                'response': subcontractor_participation.response,
                'response_display': subcontractor_participation.get_response_display(),
                'invited_timestamp': subcontractor_participation.invited_timestamp,
                'response_timestamp': subcontractor_participation.response_timestamp,
                'participant_display': subcontractor_participation.user.get_full_name(),
            }
        if superintendent_participation:
            data['superintendent'] = {
                'id': superintendent_participation.id,
                'last_notification_timestamp': getattr(superintendent_participation.user.messages.filter(
                    reason=models.Message.REASON_TASK_ACKNOWLEDGE_REQUEST, task=obj.task,
                ).first(), 'timestamp', None),
                'response': superintendent_participation.response,
                'response_display': superintendent_participation.get_response_display(),
                'invited_timestamp': superintendent_participation.invited_timestamp,
                'response_timestamp': superintendent_participation.response_timestamp,
                'participant_display': superintendent_participation.user.get_full_name(),
            }
        if builder_participation:
            data['builder'] = {
                'id': builder_participation.id,
                'last_notification_timestamp': getattr(builder_participation.user.messages.filter(
                    reason=models.Message.REASON_TASK_ACKNOWLEDGE_REQUEST, task=obj.task,
                ).first(), 'timestamp', None),
                'response': builder_participation.response,
                'response_display': builder_participation.get_response_display(),
                'invited_timestamp': builder_participation.invited_timestamp,
                'response_timestamp': builder_participation.response_timestamp,
                'participant_display': builder_participation.user.get_full_name(),
            }

        return data


class TaskDetailSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskDetailSuggestion
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = models.Transaction
        fields = '__all__'
