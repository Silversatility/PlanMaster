from django.forms import EmailField
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.postgres.search import TrigramSimilarity
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import redirect
from geolite2 import geolite2
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from construction.models import Company, CompanyRole
from construction.serializers import (
    UserSerializer,
    CompanyRoleSerializer,
    CompanyRoleSettingsSerializer,
    SimpleCompanyRoleSerializer
)
from private.permissions import PrivateTokenPermission

from .models import AuthToken, LoginAttempt, User

VUEX_STATE_IS_LOST_ON_REFRESH = True  # Fix when CREW-111 has been resolved


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def is_valid_email_address(self, email):
        try:
            EmailField().clean(email)
            return True
        except Exception:
            return False

    def post(self, request):
        if not VUEX_STATE_IS_LOST_ON_REFRESH:
            if request.user.is_authenticated:
                return Response({'success': False, 'error': 'Already logged in'}, status=status.HTTP_409_CONFLICT)

        email_or_mobile_number = request.data.get('email_or_mobile_number')
        password = request.data.get('password')

        ip_address = request.data.get('ip_address')
        if ip_address:
            location = geolite2.reader().get(ip_address)
            geolite2.close()
            location_str = '{}, {}'.format(location['subdivisions'][0]['names']['en'], location['country']['names']['en'])
        else:
            location_str = ''

        if User.objects.filter(
                Q(email__iexact=email_or_mobile_number) |
                Q(mobile_number=email_or_mobile_number)).exists():
            user = User.objects.filter(
                    Q(email__iexact=email_or_mobile_number) |
                    Q(mobile_number=email_or_mobile_number)).first()
            last_hour = timezone.now() - timezone.timedelta(hours=1)
            login_attempts = user.login_attempts.filter(is_succesful=False, date__gte=last_hour).count()
            if login_attempts >= 10:
                if login_attempts == 10:
                    user.send_locked_out_user()

                LoginAttempt.objects.create(
                    user=user, is_succesful=False, ip_address=ip_address, location=location_str, date=timezone.now()
                )
                return Response({
                    'success': False,
                    'error': 'Account locked! This lock will be lifted after 1 hour.',
                    'is_locked_out': True,
                }, status=status.HTTP_423_LOCKED)
            else:
                is_successful = user.check_password(password)
                LoginAttempt.objects.create(
                    user=user,
                    is_succesful=is_successful,
                    ip_address=ip_address,
                    location=location_str,
                    date=timezone.now(),
                )

        if email_or_mobile_number and self.is_valid_email_address(email_or_mobile_number):
            user = authenticate(request, email=email_or_mobile_number, password=password)
        else:
            user = authenticate(request, mobile_number=email_or_mobile_number, password=password)

        if user is None:
            return Response({'success': False, 'error': 'Incorrect crendentials'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        if not user.active_role and user.roles.exists():
            user.active_role = user.roles.first()
            user.save()
            user.refresh_from_db()

        return Response({
            'success': True,
            'session_key': request.session.session_key,
            'user': UserSerializer(instance=user).data,
            'settings': CompanyRoleSettingsSerializer(instance=user.active_role).data,
            'active_role': CompanyRoleSerializer(instance=user.active_role).data,
            'roles': SimpleCompanyRoleSerializer(instance=user.roles.all(), many=True).data,
        })


class LogoutView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'success': False, 'error': 'Already logged out'}, status=status.HTTP_409_CONFLICT)

        logout(request)
        return Response({'success': True})


class ForgotPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        reset_form = PasswordResetForm(data=request.data)
        if not reset_form.is_valid():
            raise ValidationError(reset_form.errors)

        for user in reset_form.get_users(reset_form.cleaned_data["email"]):
            user.send_password_resets()
        return Response({'success': True})


class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        try:
            token = AuthToken.check_token(request.query_params.get('token'), [
                AuthToken.AUTHZ_PASSWORD_RESET, AuthToken.AUTHZ_USER_LOCKED_OUT
            ])
        except AuthToken.InvalidTokenException:
            return Response({'success': False, 'error': 'Invalid token!'}, template_name='protected-reset.html')

        return Response({'success': True, 'user': token.user, 'done': False}, template_name='protected-reset.html')

    def post(self, request):
        try:
            token = AuthToken.check_token(request.query_params.get('token'), [
                AuthToken.AUTHZ_PASSWORD_RESET, AuthToken.AUTHZ_USER_LOCKED_OUT
            ])
        except AuthToken.InvalidTokenException:
            return Response({'success': False, 'error': 'Invalid token!'}, template_name='protected-reset.html')

        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')
        if password and password == password_confirm:
            token.user.set_password(password)
            token.user.save()
            token.delete()  # so no one else can use it
            return Response(
                {'success': True, 'user': token.user, 'message': 'Password successfully changed!', 'done': True},
                template_name='protected-reset.html',
            )

        return Response(
            {'success': True, 'user': token.user, 'error': 'Invalid password!', 'done': False},
            template_name='protected-reset.html',
        )


class SignupView(APIView):
    """\
        Allows integration with other sites and tools to create user accounts or invite users to participate in the
        CrewBoss network.
    """
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data, context={'signup': True})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if request.data.get('company_type') == 'Subcontractor' or request.data.get('company_type') == ['Subcontractor']:
            company_type = Company.TYPE_SUBCONTRACTOR
        else:
            company_type = Company.TYPE_CONTRACTOR
        company = Company.objects.create(
            name=request.data.get('company_name').replace('\\', '') or user.get_full_name(),
            state=request.data.get('company_state').replace('\\', '') or '',
            type=company_type,
        )
        company.roles.create(
            user=user,
            is_admin=True,
            is_builder=company.type == Company.TYPE_CONTRACTOR,
            is_crew_leader=company.type == Company.TYPE_SUBCONTRACTOR,
        )
        user.send_signup_confirmations()

        return redirect('https://crewbossconnect.com/beta-testing/?success')


class ReinviteRoleView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        if not request.role.is_admin:
            return Response(
                {'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            role = CompanyRole.objects.get(id=request.data.get('id'))
        except CompanyRole.DoesNotExist:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

        role.send_invite_confirmations(role=request.role, company=request.role.company)
        return Response({'success': True})


class InviteRoleView(APIView):

    def post(self, request):
        if not request.role.is_admin:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_data = request.data['user']

        company_exists = False
        if request.data.get('company_id'):
            try:
                company = Company.objects.get(id=request.data['company_id'])
                company_type = company.type
                company_exists = True
            except Company.DoesNotExist:
                pass

        user_exists = False
        if company_exists:
            queryset = User.objects.all()
            clause = Q()
            if user_data.get('first_name') and user_data.get('last_name'):
                queryset = queryset.annotate(
                    first_name_d=TrigramSimilarity('first_name', user_data['first_name']),
                    last_name_d=TrigramSimilarity('last_name', user_data['last_name']),
                )
                clause |= Q(first_name_d__gte=0.5, last_name_d__gte=0.5)
            if user_data.get('email'):
                clause |= Q(email__iexact=user_data['email'])
            if user_data.get('mobile_number'):
                clause |= Q(mobile_number=user_data['mobile_number'])

            user = queryset.filter(
                clause, roles__company=company, is_active=True
            ).distinct('id').first()
            user_exists = bool(user)

        if company_exists and not user_exists and not company.roles.filter(connections=request.role).exists():
            return Response(
                {'detail': 'You can only invite existing companies if you are connected to their users, '
                    'or if you have the right email address or mobile number.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user_exists:
            serializer = UserSerializer(data=user_data, context={'signup': True})
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

        current_company = request.role.company
        if request.data.get('is_employed', True):
            role = CompanyRole.objects.get_or_create(user=user, company=current_company)[0]
            role.is_admin = request.data.get('is_admin', False)
            role.is_builder = request.data.get('is_builder', False)
            role.is_crew_leader = request.data.get('is_crew_leader', False)
            role.is_superintendent = request.data.get('is_superintendent', False)
            role.is_contact = request.data.get('is_contact', False)
            role.is_employed = True
            role.company = current_company
            role.save()
        else:
            if not company_exists:
                if request.role.company.type == Company.TYPE_CONTRACTOR:
                    company_type = Company.TYPE_SUBCONTRACTOR
                elif request.role.company.type == Company.TYPE_SUBCONTRACTOR:
                    company_type = Company.TYPE_CONTRACTOR
                company = Company.objects.create(
                    name=request.data.get('company_name') or user.get_full_name(),
                    state=request.data.get('company_state') or '',
                    type=company_type,
                )
            role = CompanyRole.objects.get_or_create(user=user, company=company)[0]
            role.is_admin = True
            role.is_crew_leader = company_type == Company.TYPE_SUBCONTRACTOR
            role.is_builder = company_type == Company.TYPE_CONTRACTOR
            role.is_employed = True
            role.save()
            role.connections.add(request.role)
        role.send_invite_confirmations(role=request.role, company=request.role.company)

        return Response(CompanyRoleSerializer(role).data, status=status.HTTP_201_CREATED)


class SignupValidateView(APIView):
    permission_classes = (PrivateTokenPermission,)

    def post(self, request):
        serializer = UserSerializer(data=request.data, context={'signup': True})
        if serializer.is_valid():
            return Response({'valid': True})
        return Response({'valid': False, **serializer.errors})


class SignupConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        try:
            token = AuthToken.check_token(request.query_params.get('token'), [
                AuthToken.AUTHZ_SIGNUP, AuthToken.AUTHZ_INVITE,
            ])
        except AuthToken.InvalidTokenException:
            return Response({'success': False, 'error': 'Invalid token!'}, template_name='protected-signup.html')

        message = self.perform_confirm(token)
        return Response(
            {
                'success': True,
                'user': token.user,
                'role': token.user.roles.first(),
                'message': message,
                # 'done': token.user.password_already_set,
            },
            template_name='protected-signup.html',
        )

    def post(self, request):
        try:
            token = AuthToken.check_token(request.query_params.get('token'), [
                AuthToken.AUTHZ_SIGNUP, AuthToken.AUTHZ_INVITE,
            ])
        except AuthToken.InvalidTokenException:
            return Response({'success': False, 'error': 'Invalid token!'}, template_name='protected-signup.html')

        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')
        if password and password == password_confirm:
            token.user.set_password(password)
            token.user.password_already_set = True

            if request.data.get('first_name'):
                token.user.first_name = request.data['first_name']
            if request.data.get('last_name'):
                token.user.last_name = request.data['last_name']
            token.user.save()

            if request.data.get('company_name'):
                role = token.user.roles.first()
                role.company = Company.objects.create(
                    name=request.data['company_name'], type=request.data['company_type'],
                )
                role.save()

            return Response(
                {
                    'success': True,
                    'user': token.user,
                    'message': 'Password successfully changed!',
                    'done': token.user.password_already_set,
                },
                template_name='protected-signup.html',
            )

        return Response(
            {
                'success': True,
                'user': token.user,
                'message': 'Invalid password!',
                'done': token.user.password_already_set,
            },
            template_name='protected-signup.html',
        )


class EmailConfirmView(SignupConfirmView):
    def perform_confirm(self, token):
        already_confirmed = token.user.enable_email_notifications
        token.user.is_active = True
        token.user.enable_email_notifications = True
        token.user.save()
        return None if already_confirmed else 'Email address confirmed!'


class TextConfirmView(SignupConfirmView):
    def perform_confirm(self, token):
        already_confirmed = token.user.enable_text_notifications
        token.user.is_active = True
        token.user.enable_text_notifications = True
        token.user.save()
        return None if already_confirmed else 'Mobile number confirmed!'
