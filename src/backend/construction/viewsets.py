from datetime import timedelta

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from django_filters.rest_framework import (
    BooleanFilter, CharFilter, DateFilter, FilterSet, ModelChoiceFilter, MultipleChoiceFilter,
)
from google.cloud import translate
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.fields import DateField
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from account.models import AuthToken, LoginAttempt, User
from cbcommon.permissions import RulesPermissions
from cbcommon.views import CompanyRoleFilterMixin

from .consumers import CalendarConsumer
from . import models, schemas, serializers
from . import predicates


class LoginAttemptViewSet(viewsets.ModelViewSet):
    queryset = LoginAttempt.objects.all()
    serializer_class = serializers.LoginAttemptSerializer
    filter_fields = ('user',)
    ordering = ('id',)


class UserTypeFilterSet(FilterSet):
    ROLES = (
        ('builder', 'Builder'),
        ('crew', 'Subcontractor'),
        ('superintendent', 'Crew / Flex'),
    )
    role = MultipleChoiceFilter(method='filter_role', choices=ROLES, help_text=(
        'Filter by role in the task: crew, superintendent, builder. Can be used in conjunction: '
        '`?role=builder&role=crew` will include both builders and subcontractors.'
    ))
    order_by_user_type = CharFilter(method='sort_by_user_type', help_text=(
        'Custom sorting by user type. Pass "true" for this order: '
        '[superuser, contractor admin, subcontractor, superintendent, builder, inactive]; '
        '"false" to reverse that.'
    ))

    class Meta:
        model = User
        fields = ('role', 'order_by_user_type')

    def filter_role(self, queryset, name, value):
        q = Q()
        if 'crew' in value:
            q |= Q(roles__is_crew_leader=True)
        if 'superintendent' in value:
            q |= Q(roles__is_superintendent=True)
        if 'builder' in value:
            q |= Q(roles__is_builder=True)

        return queryset.filter(q)

    def sort_by_user_type(self, queryset, name, value):
        return queryset
        # if value == 'true':
        #     return queryset.order_by(
        #         '-is_superuser',
        #         F('crew_leader__is_admin').desc(nulls_last=True),
        #         '-crew_staff',
        #         '-superintendent',
        #         '-builder',
        #     )
        # if value == 'false':
        #     return queryset.order_by(
        #         'is_superuser',
        #         F('crew_leader__is_admin').asc(nulls_first=True),
        #         'crew_staff',
        #         'superintendent',
        #         'builder',
        #     )
        # return queryset


class UserViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_class = UserTypeFilterSet
    search_fields = ('first_name', 'last_name', 'email', 'mobile_number')
    ordering_fields = ('first_name', 'email', 'mobile_number', 'is_active')
    company_role_filter = {
        'admin': lambda role: (
            Q(roles__company__roles=role) |  # all roles under your companies
            Q(roles__connections=role)  # all invited builders
        ),
        'crew_leader': lambda role: (
            Q(roles__company__roles=role) |  # all roles under your companies
            Q(roles__connections=role)  # all invited builders
        ),
        'builder': lambda role: (
            Q(roles__company__roles=role) |  # all roles under your companies
            Q(roles__connections=role)  # all invited builders
        ),
        'superintendent': lambda role: Q(roles=role),
    }

    @action(detail=False, url_path='active-this-month')
    def active_this_month(self, request):
        queryset = User.objects.active_this_month()

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # @action(detail=False)
    # def calendar(self, request):
    #     week = month = start_date = end_date = None
    #
    #     # If 'week' is set, use it
    #     if request.query_params.get('week'):
    #         week = request.query_params['week']
    #         start_date = timezone.make_aware(datetime.strptime(week + '-1', '%G-%V-%w'), pytz.utc).date()  # Monday
    #         end_date = start_date + timedelta(days=6)  # next Sunday
    #
    #     # If 'month' is set, use it
    #     if request.query_params.get('month'):
    #         month = request.query_params['month']
    #         start_date = timezone.make_aware(datetime.strptime(month + '-01', '%Y-%m-%d'), pytz.utc).date()
    #         end_date = date(start_date.year + (start_date.month // 12), start_date.month + 1, 1) - timedelta(days=1)
    #
    #     # Arbitrary start/end date, also for day view if both are set to the same date
    #     if request.query_params.get('start_date'):
    #         start_date = datetime.strptime(request.query_params['start_date'], '%Y-%m-%d')
    #     if request.query_params.get('end_date'):
    #         end_date = datetime.strptime(request.query_params['end_date'], '%Y-%m-%d')
    #
    #     # Default is this week
    #     if not start_date and not end_date:
    #         today = timezone.now().date()
    #         start_date = today - timedelta(days=today.weekday())  # last Monday
    #         end_date = start_date + timedelta(days=6)  # next Sunday
    #         week = start_date.strftime('%Y-%V')
    #
    #     users = self.filter_queryset(self.get_queryset()).order_by('first_name', 'last_name')
    #     users = [User()] + list(users)
    #     serializer = serializers.CalendarUserListSerializer(users, many=True, context={
    #         'request': request,
    #         'start_date': start_date,
    #         'end_date': end_date,
    #         'task_search': request.query_params.get('task-search'),
    #         'task_status': request.query_params.get('task-status'),
    #         'role': request.query_params.get('role'),
    #     })
    #     response_data = {
    #         'start_date': start_date,
    #         'users': serializer.data,
    #     }
    #     if week:
    #         response_data.update({
    #             'week_number': start_date.isocalendar()[1],
    #             'prev': (start_date - timedelta(weeks=1)).strftime('%Y-%V'),
    #             'next': (start_date + timedelta(weeks=1)).strftime('%Y-%V'),
    #         })
    #     if month:
    #         response_data.update({
    #             'month': month,
    #             'prev': ((start_date - timedelta(days=1)).replace(day=1)).strftime('%Y-%m'),
    #             'next': (date(start_date.year + (start_date.month // 12), start_date.month + 1, 1)).strftime('%Y-%m'),
    #         })
    #     return Response(response_data)


class CompanyViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    company_role_filter = {
        'admin': lambda role: Q(roles=role) | Q(roles__connections=role),
        'crew_leader': lambda role: Q(roles=role) | Q(roles__connections=role),
        'builder': lambda role: Q(roles=role) | Q(roles__connections=role),
        'superintendent': lambda role: Q(roles=role) | Q(roles__connections=role),
    }
    permission_classes = (RulesPermissions,)
    permission_rules = {
        'update': predicates.is_admin_of_company,
        'partial_update': predicates.is_admin_of_company,
    }
    search_fields = ('name', 'city', 'state')
    filter_fields = ('type',)

    @action(detail=False)
    def match(self, request):
        if request.role.company.type == models.Company.TYPE_CONTRACTOR:
            company_type = models.Company.TYPE_SUBCONTRACTOR
        elif request.role.company.type == models.Company.TYPE_SUBCONTRACTOR:
            company_type = models.Company.TYPE_CONTRACTOR

        queryset = models.Company.objects.all()
        clause = Q(roles__connections=request.role)
        if request.query_params.get('first_name') and request.query_params.get('last_name'):
            queryset = queryset.annotate(
                first_name_d=TrigramSimilarity('roles__user__first_name', request.query_params['first_name']),
                last_name_d=TrigramSimilarity('roles__user__last_name', request.query_params['last_name']),
            )
            clause |= Q(first_name_d__gte=0.5, last_name_d__gte=0.5)
        if request.query_params.get('email'):
            clause |= Q(roles__user__email__iexact=request.query_params['email'])
        if request.query_params.get('mobile_number'):
            clause |= Q(roles__user__mobile_number=request.query_params['mobile_number'])
        queryset = self.filter_queryset(queryset.filter(clause, type=company_type).distinct('name', 'city', 'state'))
        return Response([
            {'id': company.id, 'name': company.name, 'address': company.city_state_zip, 'state': company.state}
            for company in queryset
        ])

    @action(
        detail=False,
        url_path='create-company-with-role',
        methods=['post'],
    )
    def create_company_with_role(self, request):
        if not request.role.is_admin:
            return Response(
                {'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user.roles.create(
            is_active=True,
            is_employed=True,
            is_admin=True,
            company=serializer.instance,
        )

        data = {
            'roles': serializers.CompanyRoleSerializer(instance=user.roles.all(), many=True).data
        }
        return Response(data, status=status.HTTP_201_CREATED)


class CompanyRoleFilterSet(FilterSet):
    ROLES = (
        ('builder', 'Builder'),
        ('subcontractor', 'Subcontractor'),
        ('superintendent', 'Crew / Flex'),
    )
    role = MultipleChoiceFilter(method='filter_role', choices=ROLES, help_text=(
        'Filter by role in the task: subcontractor, superintendent, builder. Can be used in conjunction: '
        '`?role=builder&role=subcontractor` will include both builders and subcontractors.'
    ))
    order_by_user_type = CharFilter(method='sort_by_user_type', help_text=(
        'Custom sorting by user type. Pass "true" for this order: '
        '[superuser, contractor admin, subcontractor, superintendent, builder, inactive]; '
        '"false" to reverse that.'
    ))
    only_invited = BooleanFilter(method='filter_only_invited')
    job = ModelChoiceFilter(queryset=models.Job.objects.all(), method='filter_job')
    company = ModelChoiceFilter(queryset=models.Company.objects.all(), method='filter_company')
    exclude_job = ModelChoiceFilter(queryset=models.Job.objects.all(), method='filter_exclude_job')

    class Meta:
        model = models.CompanyRole
        fields = ('role', 'order_by_user_type', 'job', 'only_invited')

    def filter_role(self, queryset, name, value):
        q = Q()
        if 'subcontractor' in value:
            q |= Q(is_crew_leader=True)
        if 'superintendent' in value:
            q |= Q(is_superintendent=True)
        if 'builder' in value:
            q |= Q(is_builder=True)

        return queryset.filter(q)

    def sort_by_user_type(self, queryset, name, value):
        if value == 'true':
            return queryset.order_by(
                '-user__is_superuser',
                '-is_admin',
                '-is_builder',
                '-is_crew_leader',
                '-is_superintendent',
            )
        if value == 'false':
            return queryset.order_by(
                'user__is_superuser',
                'is_admin',
                'is_builder',
                'is_crew_leader',
                'is_superintendent',
            )
        return queryset

    def filter_only_invited(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(company__roles=self.request.role) |
                Q(connections=self.request.role) |
                Q(connections__company__roles=self.request.role)
            )
        return queryset

    def filter_job(self, queryset, name, value):
        return queryset.filter(shared_jobs=value)

    def filter_company(self, queryset, name, value):
        return queryset.filter(
            Q(company=value) | Q(company__roles=self.request.role)
        ).distinct()

    def filter_exclude_job(self, queryset, name, value):
        return queryset.exclude(shared_jobs=value)


class CompanyRoleViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.CompanyRole.objects.all()
    serializer_class = serializers.CompanyRoleSerializer
    ordering_fields = (
        'id', 'company__name', 'user__first_name', 'user__email', 'user__mobile_number',
    )
    filter_class = CompanyRoleFilterSet
    company_role_filter = {
        'admin': lambda role: (
            Q(id=role.id) |
            Q(connections__company__roles=role) |
            Q(connections=role) |
            Q(Q(company=role.company) | Q(connections__company__roles=role), shared_jobs__roles=role)
        ),
        'crew_leader': lambda role: (
            Q(id=role.id) |
            Q(connections__company__roles=role) |
            Q(connections=role) |
            Q(Q(company=role.company) | Q(connections__company__roles=role), shared_jobs__roles=role)
        ),
        'builder': lambda role: (
            Q(id=role.id) |
            Q(connections__company__roles=role) |
            Q(connections=role) |
            Q(Q(company=role.company) | Q(connections__company__roles=role), shared_jobs__roles=role)
        ),
        'superintendent': lambda role: (
            Q(id=role.id) |
            Q(connections__company__roles=role) |
            Q(connections=role) |
            Q(company=role.company)
        ),
    }
    search_fields = ('company__name', 'user__first_name', 'user__last_name', 'user__email', 'user__mobile_number')
    permission_classes = (RulesPermissions,)
    permission_rules = {
        'update': predicates.is_admin,
        'partial_update': predicates.is_admin,
    }

    @action(detail=False, url_path='active-role', methods=['get'])
    def active_role(self, request):
        return Response({'active_role': serializers.CompanyRoleSerializer(instance=request.user.active_role).data})

    @action(detail=True, url_path='switch-company', methods=['patch'])
    def switch_company(self, request, pk):
        # switches user.active_role
        request.user.active_role_id = pk
        request.user.save()
        request.user.refresh_from_db()
        data = serializers.CompanyRoleSerializer(instance=request.user.active_role).data
        return Response({'active_role': data})

    @action(detail=False)
    def user_settings(self, request):
        data = serializers.CompanyRoleSettingsSerializer(request.role).data
        data['current_user_id'] = request.user.id
        return Response(data)

    @action(detail=False)
    def mine(self, request):
        queryset = self.filter_queryset(self.queryset.filter(user=request.user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SubdivisionViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Subdivision.objects.all()
    serializer_class = serializers.SubdivisionSerializer
    company_role_filter = {'admin': lambda role: Q(company__roles=role)}


class TaskCategoryViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.TaskCategory.objects.all()
    serializer_class = serializers.TaskCategorySerializer
    company_role_filter = {
        'admin': lambda role: Q(contractor__roles=role),
        'crew_leader': lambda role: Q(contractor__roles=role),
        'builder': lambda role: Q(contractor__roles=role),
        'superintendent': lambda role: Q(contractor__roles=role),
    }
    ordering_fields = ('name',)
    ordering = ('name',)


class TaskSubCategoryViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.TaskSubCategory.objects.all()
    serializer_class = serializers.TaskSubCategorySerializer
    filter_fields = ('category',)
    company_role_filter = {
        'admin': lambda role: Q(category__contractor__roles=role),
        'crew_leader': lambda role: Q(category__contractor__roles=role),
        'builder': lambda role: Q(category__contractor__roles=role),
        'superintendent': lambda role: Q(category__contractor__roles=role),
    }
    ordering_fields = ('name',)
    ordering = ('name',)


class JobViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Job.objects.all()
    serializer_class = serializers.JobSerializer
    permission_classes = (RulesPermissions,)
    permission_rules = {
        'update': predicates.is_job_owner_or_creator,
        'partial_update': predicates.is_job_owner_or_creator,
        'destroy': predicates.is_job_owner_or_creator,
        'create': predicates.is_admin,
    }
    filter_fields = ('owner', 'is_archived', 'roles')
    search_fields = (
        'street_address', 'subdivision__name', 'lot_number', 'owner__name',
        'builder__user__first_name', 'builder__user__last_name',
        'subcontractor__user__first_name', 'subcontractor__user__last_name',
        'superintendent__user__first_name', 'superintendent__user__last_name',
        'roles__user__first_name', 'roles__user__last_name',
    )
    ordering_fields = (
        'date_added', 'street_address', 'owner__name', 'subdivision__name', 'lot_number',
        'builder__user__first_name', 'subcontractor__user__first_name', 'superintendent__user__first_name',
    )
    company_role_filter = {
        'admin': (
            lambda role: Q(created_by__roles=role) | Q(owner__roles=role) | Q(roles=role)
        ),
        'crew_leader': lambda role: Q(owner__roles=role) | Q(roles=role),
        'builder': lambda role: Q(owner__roles=role) | Q(roles=role),
        'superintendent': lambda role: Q(roles=role),
    }

    @action(detail=True, methods=['put'], url_path='share-role')
    def share_role(self, request, pk):
        job = self.get_object()
        job.roles.add(request.data['role'])
        return Response()

    @action(detail=True, methods=['put'], url_path='unshare-role')
    def unshare_role(self, request, pk):
        job = self.get_object()
        job.roles.remove(request.data['role'])
        return Response()

    @action(detail=True, methods=['put'])
    def archive(self, request, pk):
        if not request.role.is_admin:
            return Response(
                {'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_400_BAD_REQUEST
            )
        job = self.get_object()
        job.is_archived = True
        job.save()
        return Response({'success': True})

    @action(detail=True, methods=['put'])
    def unarchive(self, request, pk):
        if not request.role.is_admin:
            return Response(
                {'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_400_BAD_REQUEST
            )
        job = self.get_object()
        job.is_archived = False
        job.save()
        return Response({'success': True})


class TaskFilterSet(FilterSet):
    status = CharFilter(
        method='filter_status',
        help_text=('Custom filter for status with the addition of is_completed')
    )
    date = DateFilter(
        method='filter_date',
        help_text=('Custom filter for task date')
    )
    job_is_archived = BooleanFilter(
        method='filter_archived',
        help_text=('Custom filter for archived Task under a Job')
    )
    role = ModelChoiceFilter(queryset=models.CompanyRole.objects.all(), method='filter_role')
    start = DateFilter(method='filter_start')
    end = DateFilter(method='filter_end')

    class Meta:
        model = models.Task
        fields = ('job', 'status', 'is_completed', 'date', 'job_is_archived', 'role', 'start', 'end')

    def filter_status(self, queryset, name, value):
        if value in [str(option[0]) for option in models.Task.STATUS_OPTIONS]:
            return queryset.filter(status=value, is_completed=False)
        elif value == 'is_completed':
            return queryset.filter(is_completed=True)

        return queryset

    def filter_archived(self, queryset, name, value):
        if not value:
            return queryset.filter(job__is_archived=False)

    def filter_date(self, queryset, name, value):
        return queryset.filter(start_date__lte=value, end_date__gte=value)

    def filter_role(self, queryset, name, value):
        return queryset.filter(Q(subcontractor=value) | Q(superintendent=value) | Q(builder=value))

    def filter_start(self, queryset, name, value):
        return queryset.filter(end_date__gte=value)

    def filter_end(self, queryset, name, value):
        return queryset.filter(start_date__lte=value)



class TaskViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    search_fields = (
        'subcontractor__user__first_name', 'subcontractor__user__last_name',
        'superintendent__user__first_name', 'superintendent__user__last_name',
        'builder__user__first_name', 'builder__user__last_name',
        'job__street_address', 'job__subdivision__name', 'job__lot_number', 'name',
    )
    filter_class = TaskFilterSet
    ordering_fields = (
        'id', 'name', 'job__street_address', 'start_date', 'end_date', 'subcontractor__user__first_name',
        'builder__user__first_name', 'superintendent__user__first_name',
    )
    filter_class = TaskFilterSet
    company_role_filter = {
        'admin': lambda role: (
            Q(job__roles=role) | Q(job__owner__roles=role) |
            Q(subcontractor=role) | Q(builder=role) | Q(superintendent=role) | Q(author=role.user)
        ),
        'crew_leader': lambda role: (
            (
                Q(job__roles=role) | Q(job__owner__roles=role) |
                Q(subcontractor=role) | Q(author=role.user)
            ) if role.can_see_full_job else (Q(subcontractor=role) | Q(author=role.user))
        ),
        'builder': lambda role: (
            (
                Q(job__roles=role) | Q(job__owner__roles=role) |
                Q(builder=role) | Q(author=role.user)
            ) if role.can_see_full_job else (Q(builder=role) | Q(author=role.user))
        ),
        'superintendent': lambda role: (
            (
                Q(job__roles=role) | Q(job__owner__roles=role) |
                Q(superintendent=role) | Q(author=role.user)
            ) if role.can_see_full_job else (Q(superintendent=role) | Q(author=role.user))
        ),
    }
    schema = schemas.CalendarAutoSchema()
    permission_classes = (RulesPermissions,)
    permission_rules = {
        'update': predicates.is_admin_of_owning_contractor,
        'partial_update': predicates.is_admin_of_owning_contractor,
        'create': predicates.is_admin_of_owning_contractor,
        'destroy': predicates.is_admin_or_creator,
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.TaskListSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        task = serializer.save(author=self.request.user)
        if task.job.owner:
            for reminder in task.job.owner.default_reminders.all():
                models.Reminder.objects.create(
                    task=task,
                    reminder_days=reminder.reminder_days,
                )

        CalendarConsumer.reload_calendar(
            contractor_id=task.job.owner.id, user_id=self.request.user.id
        )
        return task

    def perform_update(self, serializer):
        task = serializer.save()
        user_id = self.request.user.id if self.action == 'partial_update' else None
        CalendarConsumer.reload_calendar(
            contractor_id=task.job.owner.id, user_id=user_id
        )
        return task

    def perform_destroy(self, instance):
        instance.delete()
        CalendarConsumer.reload_calendar(
            contractor_id=instance.job.owner.id, user_id=self.request.user.id
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='detailed',
        ordering_fields=(
            'id', 'name', 'job__street_address', 'start_date', 'end_date', 'subcontractor__user__first_name',
            'builder__user__first_name', 'superintendent__user__first_name', 'category__name',
            'subcategory__name', 'job__subdivision__name', 'job__lot_number', 'job__city', 'job__state', 'job__zip'
        ),
        search_fields=(
            'subcontractor__user__first_name', 'subcontractor__user__last_name',
            'superintendent__user__first_name', 'superintendent__user__last_name',
            'builder__user__first_name', 'builder__user__last_name',
            'job__street_address', 'job__subdivision__name', 'name',
            'category__name', 'subcategory__name', 'job__lot_number', 'job__city', 'job__state', 'job__zip'
        )
    )
    def detailed_list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        if start:
            start = parse_date(start)
            if start:
                queryset = queryset.filter(end_date__gte=start)
        if end:
            end = parse_date(end)
            if end:
                queryset = queryset.filter(start_date__lte=end)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], search_fields=('name',))
    def names(self, request):
        queryset = models.Task.objects.filter(job__owner=request.role.company)
        names = list(
            self.filter_queryset(queryset).values_list('name', flat=True).order_by('name').distinct('name')
        )
        return Response(names)

    @action(detail=False, methods=['post'], url_path='create-and-send-notifications')
    def create_and_send_notifications(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = self.perform_create(serializer)
        response = self._send_notification(task)
        return response

    @action(detail=True, methods=['put'], url_path='update-and-send-notifications')
    def update_and_send_notifications(self, request, pk, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        task = self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        response = self._send_notification(task)
        return response

    def _send_notification(self, task, role=None):
        role = role if role else self.request.role
        notification = models.NotificationQueue.fetch_queued_notification(task)

        response_data = {
            'id': task.id,
        }
        if notification:
            notification_messages = notification.send_messages(
                sender_role=role, sender=role.company
            )
            response_data['notification_messages'] = notification_messages

        return Response(response_data)

    @action(detail=True, methods=['put'], url_path='send-notification')
    def send_notification(self, request, pk):
        task = self.get_object()
        response = self._send_notification(task)
        return response

    @action(detail=True, methods=['put'])
    def complete(self, request, pk):
        task = self.get_object()
        if not predicates.is_admin_of_owning_contractor(request.user, task):
            return Response(
                {'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_400_BAD_REQUEST
            )
        task.is_completed = True
        task.save()
        return Response({'success': True})

    @action(detail=False, permission_classes=(permissions.AllowAny,), renderer_classes=(TemplateHTMLRenderer,))
    def accept(self, request):
        try:
            token = AuthToken.check_token(request.query_params.get('token'), [
                AuthToken.AUTHZ_TASK_ACKNOWLEDGE_REQUEST,
                AuthToken.AUTHZ_TASK_UPDATE_GENERAL,
                AuthToken.AUTHZ_TASK_UPDATE_SCHEDULE,
                AuthToken.AUTHZ_TASK_REMOVE,
                AuthToken.AUTHZ_TASK_STATUS_UPDATE,
            ])
        except AuthToken.InvalidTokenException:
            return Response({'success': False, 'error': 'Invalid token!'}, template_name='protected-task.html')

        if token.participation.task.is_completed:
            return Response(
                {'success': False, 'error': 'Cannot change status of a completed task!'},
                template_name='protected-task.html',
            )

        token.participation.response = token.participation.RESPONSE_ACCEPTED
        token.participation.response_timestamp = timezone.now()
        token.participation.save()

        CalendarConsumer.reload_calendar(
            contractor_id=token.participation.task.job.owner.id, user_id=None)

        return Response(
            {'success': True, 'participation': token.participation, 'message': 'Participation accepted!'},
            template_name='protected-task.html',
        )

    @action(detail=False, permission_classes=(permissions.AllowAny,), renderer_classes=(TemplateHTMLRenderer,))
    def reject(self, request):
        try:
            token = AuthToken.check_token(request.query_params.get('token'), [
                AuthToken.AUTHZ_TASK_ACKNOWLEDGE_REQUEST,
                AuthToken.AUTHZ_TASK_UPDATE_GENERAL,
                AuthToken.AUTHZ_TASK_UPDATE_SCHEDULE,
                AuthToken.AUTHZ_TASK_REMOVE,
                AuthToken.AUTHZ_TASK_STATUS_UPDATE,
            ])
        except AuthToken.InvalidTokenException:
            return Response({'success': False, 'error': 'Invalid token!'}, template_name='protected-task.html')

        if token.participation.task.is_completed:
            return Response(
                {'success': False, 'error': 'Cannot change status of a completed task!'},
                template_name='protected-task.html',
            )

        if token.participation.response != models.Participation.RESPONSE_REJECTED:
            key_participants = token.participation.task.key_participants
            rejector = None
            for role, participation in key_participants.items():
                if participation.id == token.participation.id:
                    role_display = role.replace('_', ' ').title()
                    rejector = {'name': str(token.participation.user), 'role_display': role_display}
            for participation in key_participants.values():
                if participation.id != token.participation.id:
                    participation.send_reject_message(extra_context={'rejector': rejector})

        token.participation.response = token.participation.RESPONSE_REJECTED
        token.participation.response_timestamp = timezone.now()
        token.participation.save()

        CalendarConsumer.reload_calendar(
            contractor_id=token.participation.task.job.owner.id, user_id=None)

        return Response(
            {'success': True, 'participation': token.participation, 'message': 'Participation rejected!'},
            template_name='protected-task.html',
        )

    @action(detail=False, permission_classes=(permissions.AllowAny,), renderer_classes=(TemplateHTMLRenderer,))
    def review(self, request):
        try:
            token = AuthToken.check_token(request.query_params.get('token'), [
                AuthToken.AUTHZ_TASK_ACKNOWLEDGE_REQUEST,
                AuthToken.AUTHZ_TASK_UPDATE_GENERAL,
                AuthToken.AUTHZ_TASK_UPDATE_SCHEDULE,
                AuthToken.AUTHZ_TASK_REMOVE,
                AuthToken.AUTHZ_TASK_STATUS_UPDATE,
                AuthToken.AUTHZ_TASK_REJECT,
            ])
        except AuthToken.InvalidTokenException:
            return Response({'success': False, 'error': 'Invalid token!'}, template_name='protected-task.html')

        hide_action = False
        if token.authz_type == AuthToken.AUTHZ_TASK_REJECT:
            hide_action = True

        return Response({
            'success': True, 'participation': token.participation, 'review': True, 'hide_action': hide_action
        }, template_name='protected-task.html')

    @action(detail=False, url_path='compute-end-date')
    def compute_end_date(self, request):
        one_day = timedelta(days=1)

        company = models.Company.objects.get(id=request.query_params['company_id'])
        non_working_days = company.non_working_days
        duration_in_days = request.query_params['duration_in_days']
        #  initial value of end_date will be the start_date itself
        end_date = DateField().to_internal_value(request.query_params['start_date'])
        # we don't add the first day
        days_to_add = int(duration_in_days) - 1
        for i in range(days_to_add):
            end_date = end_date + one_day
            while end_date.strftime('%A') in non_working_days:
                end_date = end_date + one_day

        return Response(end_date.strftime('%Y-%m-%d'))

    @action(detail=False, url_path='compute-duration-in-days')
    def compute_duration_in_days(self, request):
        one_day = timedelta(days=1)
        company = models.Company.objects.get(id=request.query_params['company_id'])
        non_working_days = company.non_working_days
        start_date = DateField().to_internal_value(request.query_params['start_date'])
        end_date = DateField().to_internal_value(request.query_params['end_date'])
        days_apart = (end_date - start_date).days

        # we will start with days_apart and subtract the number of non_working_days inside the range
        # we need to add the day it self in the duration
        duration_in_days = days_apart + 1
        for i in range(int(days_apart)):
            start_date = start_date + one_day
            if start_date.strftime('%A') in non_working_days:
                duration_in_days = duration_in_days - 1

        return Response(duration_in_days)

    @action(detail=False, permission_classes=(permissions.AllowAny,), methods=['post'])
    def suggest(self, request):
        try:
            token = AuthToken.check_token(
                request.data['token'],
                [AuthToken.AUTHZ_TASK_ACKNOWLEDGE_REQUEST, AuthToken.AUTHZ_TASK_UPDATE_SCHEDULE]
            )
        except AuthToken.InvalidTokenException:
            return Response({'success': False, 'error': 'Invalid token!'}, template_name='protected-task.html')

        task = token.participation.task
        start_date = request.data['start_date']
        end_date = request.data['end_date']
        data = {'start_date': start_date, 'end_date': end_date}
        serializer = self.get_serializer(task, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        participation = task.participants.get(user=token.user)
        participation.response = models.Participation.RESPONSE_ACCEPTED
        participation.save()
        self._send_notification(task, token.user.active_role)
        redirect_url = '/api/v1/task/suggestion-success/?token={}'.format(token.token)
        return Response(data={'success': True, 'redirect_url': redirect_url}, status=status.HTTP_201_CREATED)

    @action(
        detail=False, permission_classes=(permissions.AllowAny,), renderer_classes=(TemplateHTMLRenderer,),
        url_path='suggestion-success',
    )
    def suggestion_success(self, request):
        try:
            token = AuthToken.check_token(request.query_params.get('token'), [
                AuthToken.AUTHZ_TASK_ACKNOWLEDGE_REQUEST,
                AuthToken.AUTHZ_TASK_UPDATE_GENERAL,
                AuthToken.AUTHZ_TASK_UPDATE_SCHEDULE,
                AuthToken.AUTHZ_TASK_REMOVE,
                AuthToken.AUTHZ_TASK_STATUS_UPDATE,
            ])
        except AuthToken.InvalidTokenException:
            return Response({'success': False, 'error': 'Invalid token!'}, template_name='protected-task.html')

        if token.participation.task.is_completed:
            return Response(
                {'success': False, 'error': 'Cannot change status of a completed task!'},
                template_name='protected-task.html',
            )

        return Response(
            {'success': True, 'participation': token.participation, 'message': 'Suggestion sent!'},
            template_name='protected-task.html',
        )

    @action(
        detail=False, permission_classes=(permissions.AllowAny,), renderer_classes=(TemplateHTMLRenderer,),
        url_path='accept-suggestion',
    )
    def accept_suggestion(self, request):
        try:
            suggestion = models.TaskDetailSuggestion.objects.get(id=request.query_params['sid'])
        except (KeyError, models.TaskDetailSuggestion.DoesNotExist):
            return Response(
                {'success': False, 'error': 'Invalid token!'}, template_name='protected-task-suggestion.html'
            )

        try:
            token = AuthToken.check_token(request.query_params.get('token'), [AuthToken.AUTHZ_TASK_SUGGEST_SCHEDULE])
        except AuthToken.InvalidTokenException:
            return Response(
                {'success': False, 'error': 'Invalid token!'}, template_name='protected-task-suggestion.html'
            )

        if token.participation.task.is_completed:
            return Response(
                {'success': False, 'error': 'Cannot change status of a completed task!'},
                template_name='protected-task-suggestion.html',
            )

        responses_key = ''
        key_participants = token.participation.task.key_participants
        for role, participation in key_participants.items():
            if participation.id == token.participation.id:
                responses_key = role
                break
        suggestion.responses[responses_key]['response'] = models.TaskDetailSuggestion.STATUS_ACCEPTED
        suggestion.save()
        suggestion.refresh_from_db()

        if (suggestion.responses.get('subcontractor') and
            suggestion.responses.get('builder') and
            suggestion.responses.get('superintendent')
        ):
            if (
                suggestion.responses['subcontractor']['response'] == models.TaskDetailSuggestion.STATUS_ACCEPTED and
                suggestion.responses['builder']['response'] == models.TaskDetailSuggestion.STATUS_ACCEPTED and
                suggestion.responses['superintendent']['response'] == models.TaskDetailSuggestion.STATUS_ACCEPTED
            ):
                suggestion.status = models.TaskDetailSuggestion.STATUS_ACCEPTED
                suggestion.save()
                token.participation.task.start_date = suggestion.start_date
                token.participation.task.end_date = suggestion.end_date
                token.participation.task.save()
                key_participants['subcontractor'].response = models.Participation.RESPONSE_ACCEPTED
                key_participants['subcontractor'].save()
                key_participants['superintendent'].response = models.Participation.RESPONSE_ACCEPTED
                key_participants['superintendent'].save()
                key_participants['builder'].response = models.Participation.RESPONSE_ACCEPTED
                key_participants['builder'].save()

        return Response(
            {
                'success': True,
                'participation': token.participation,
                'message': 'Suggestion accepted!',
                'suggestion': suggestion,
            },
            template_name='protected-task-suggestion.html',
        )

    @action(
        detail=False, permission_classes=(permissions.AllowAny,), renderer_classes=(TemplateHTMLRenderer,),
        url_path='reject-suggestion',
    )
    def reject_suggestion(self, request):
        try:
            suggestion = models.TaskDetailSuggestion.objects.get(id=request.query_params['sid'])
        except (KeyError, models.TaskDetailSuggestion.DoesNotExist):
            return Response(
                {'success': False, 'error': 'Invalid token!'}, template_name='protected-task-suggestion.html'
            )

        try:
            token = AuthToken.check_token(request.query_params.get('token'), [AuthToken.AUTHZ_TASK_SUGGEST_SCHEDULE])
        except AuthToken.InvalidTokenException:
            return Response(
                {'success': False, 'error': 'Invalid token!'}, template_name='protected-task-suggestion.html'
            )

        if token.participation.task.is_completed:
            return Response(
                {'success': False, 'error': 'Cannot change status of a completed task!'},
                template_name='protected-task-suggestion.html',
            )

        responses_key = ''
        key_participants = token.participation.task.key_participants
        for role, participation in key_participants.items():
            if participation.id == token.participation.id:
                responses_key = role
                break
        suggestion.responses[responses_key]['response'] = models.TaskDetailSuggestion.STATUS_REJECTED
        suggestion.save()
        suggestion.refresh_from_db()

        return Response(
            {
                'success': True,
                'participation': token.participation,
                'message': 'Suggestion rejected!',
                'suggestion': suggestion,
            },
            template_name='protected-task-suggestion.html',
        )

    @action(
        detail=False, permission_classes=(permissions.AllowAny,), renderer_classes=(TemplateHTMLRenderer,),
        url_path='review-suggestion',
    )
    def review_suggestion(self, request):
        try:
            suggestion = models.TaskDetailSuggestion.objects.get(id=request.query_params['sid'])
        except (KeyError, models.TaskDetailSuggestion.DoesNotExist):
            return Response(
                {'success': False, 'error': 'Invalid token!'}, template_name='protected-task-suggestion.html'
            )

        try:
            token = AuthToken.check_token(request.query_params.get('token'), [AuthToken.AUTHZ_TASK_SUGGEST_SCHEDULE])
        except AuthToken.InvalidTokenException:
            return Response(
                {'success': False, 'error': 'Invalid token!'}, template_name='protected-task-suggestion.html'
            )

        if token.participation.task.is_completed:
            return Response(
                {'success': False, 'error': 'Cannot change status of a completed task!'},
                template_name='protected-task-suggestion.html',
            )

        return Response(
            {
                'success': True,
                'review': True,
                'participation': token.participation,
                'suggestion': suggestion,
            },
            template_name='protected-task-suggestion.html',
        )


class ParticipationViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Participation.objects.all()
    serializer_class = serializers.ParticipationSerializer
    company_role_filter = {
        'admin': lambda role: Q(task__job__owner__roles=role) | Q(task__job__created_by__roles=role),
    }

    def perform_update(self, serializer):
        response = self.request.data.get('response')
        extra_data = {}
        if response:
            extra_data['response_timestamp'] = timezone.now()
        participant = serializer.save(**extra_data)
        CalendarConsumer.reload_calendar(
            contractor_id=participant.task.job.owner.id, user_id=self.request.user.id)
        if participant.user != self.request.user:
            participant.send_status_update_message(sender_role=self.request.role, sender=self.request.role.company)

    @action(detail=True, methods=['post'], url_path='send-acknowledgement')
    def send_acknowledgement(self, request, pk):
        instance = self.get_object()
        instance.send_token_message(sender_role=request.role, sender=request.role.company)
        return Response()


class ContactViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    company_role_filter = {
        'admin': lambda role: (
            Q(job__owner__roles=role) |
            Q(task__job__owner__roles=role)
        ),
    }

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class NoteViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    company_role_filter = {
        'admin': lambda role: (
            Q(job__owner__roles=role) |
            Q(task__job__owner__roles=role)
        ),
    }

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['post'])
    def translate(self, request):
        translate_client = translate.Client()
        text = u'{}'.format(request.data['text'])

        if 'to_es' in request.data['language']:
            target = 'es'
        else:
            target = 'en'

        translation = translate_client.translate(text, target_language=target)
        return Response({'success': True, 'translated_text': translation['translatedText']})


class DocumentViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer
    company_role_filter = {
        'admin': lambda role: (
            Q(job__owner__roles=role) |
            Q(task__job__owner__roles=role)
        ),
    }

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ReminderViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Reminder.objects.all()
    serializer_class = serializers.ReminderSerializer
    company_role_filter = {
        'admin': lambda role: Q(task__job__owner__roles=role),
    }


class DefaultRemindersViewSet(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.DefaultReminders.objects.all()
    serializer_class = serializers.DefaultRemindersSerializer
    company_role_filter = {
        'admin': lambda role: Q(company__roles=role),
    }


class NotificationQueueFilterSet(FilterSet):
    is_queued = BooleanFilter(field_name='sent_timestamp', lookup_expr='isnull')

    class Meta:
        model = models.NotificationQueue
        fields = ('is_queued', 'type', )


class NotificationQueueViewset(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.NotificationQueue.objects.all()
    serializer_class = serializers.NotificationQueueSerializer
    filter_class = NotificationQueueFilterSet
    search_fields = ('task__name', )
    company_role_filter = {
        'admin': lambda role: Q(task__job__owner__roles=role),
        'crew_leader': lambda role: Q(task__subcontractor=role) | Q(task__builder=role),
        'builder': lambda role: Q(task__subcontractor=role) | Q(task__builder=role),
        'superintendent': lambda role: Q(task__superintendent=role),
    }

    @action(detail=False, url_path="queued-count")
    def notification_count(self, request):
        return Response({'notification_count': self.get_queryset().queued_notifications().count()})


class TransactionViewset(CompanyRoleFilterMixin, viewsets.ModelViewSet):
    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    filter_fields = ('company',)
    company_role_filter = {
        'admin': lambda role: Q(company__roles=role),
    }
