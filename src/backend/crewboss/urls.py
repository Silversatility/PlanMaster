"""crewboss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.views.static import serve
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

from account import views as account_views
from billing import views as billing_views
from construction import viewsets as construction_viewsets
from private import views as private_views


router = DefaultRouter()
router.register(r'login-attempt', construction_viewsets.LoginAttemptViewSet, base_name='login_attempt')
router.register(r'user', construction_viewsets.UserViewSet, base_name='user')
router.register(r'task_category', construction_viewsets.TaskCategoryViewSet, base_name='task_category')
router.register(r'task_subcategory', construction_viewsets.TaskSubCategoryViewSet, base_name='task_subcategory')
router.register(r'task', construction_viewsets.TaskViewSet, base_name='task')
router.register(r'job', construction_viewsets.JobViewSet, base_name='job')
router.register(r'company', construction_viewsets.CompanyViewSet, base_name='company')
router.register(r'company-role', construction_viewsets.CompanyRoleViewSet, base_name='company-role')
router.register(r'subdivision', construction_viewsets.SubdivisionViewSet, base_name='subdivision')
router.register(r'participation', construction_viewsets.ParticipationViewSet, base_name='participation')
router.register(r'contact', construction_viewsets.ContactViewSet, base_name='contact')
router.register(r'note', construction_viewsets.NoteViewSet, base_name='note')
router.register(r'document', construction_viewsets.DocumentViewSet, base_name='document')
router.register(r'reminder', construction_viewsets.ReminderViewSet, base_name='reminder')
router.register(r'default-reminders', construction_viewsets.DefaultRemindersViewSet, base_name='default-reminders')
router.register(r'notification-queue', construction_viewsets.NotificationQueueViewset, base_name='notification-queue')
router.register(r'transaction', construction_viewsets.TransactionViewset, base_name='transaction')

urlpatterns = [
    url(r'^dist/index.html$', RedirectView.as_view(url='/'), name='old-base'),
    url(r'^$', serve, {'path': 'index.html', 'document_root': settings.FRONTEND_DIR + '/dist/'}, name="index"),
    url(r'', include('django.contrib.auth.urls')),
    url(r'^ht/', include('health_check.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/', include('loginas.urls')),
    url(
        r'^private/delete-expired-tokens/$',
        private_views.DeleteExpiredTokensView.as_view(),
        name='private_delete_expired_tokens',
    ),
    url(r'^private/send-task-reminders/$', private_views.SendTaskReminders.as_view(), name='send_task_reminders'),
    url(r'^private/make-backup/$', private_views.MakeBackupView.as_view(), name='private_make_backup'),
    url(r'^api-docs/v1/', include_docs_urls(title='CrewBoss API')),
    url(r'^api/v1/login/$', account_views.LoginView.as_view(), name='account_login'),
    url(r'^api/v1/logout/$', account_views.LogoutView.as_view(), name='account_logout'),
    url(r'^api/v1/iforgot/$', account_views.ForgotPasswordView.as_view(), name='account_forgot_password'),
    url(r'^api/v1/reset-confirm/$', account_views.ResetPasswordView.as_view(), name='account_reset_password'),
    url(r'^api/v1/signup/$', account_views.SignupView.as_view(), name='account_signup'),
    url(r'^api/v1/invite/$', account_views.InviteRoleView.as_view(), name='role_invite'),
    url(r'^api/v1/reinvite/$', account_views.ReinviteRoleView.as_view(), name='role_reinvite'),
    url(r'^api/v1/signup-validate/$', account_views.SignupValidateView.as_view(), name='account_signup_validate'),
    url(r'^api/v1/email-confirm/$', account_views.EmailConfirmView.as_view(), name='account_email_confirm'),
    url(r'^api/v1/text-confirm/$', account_views.TextConfirmView.as_view(), name='account_text_confirm'),
    url(r'^api/v1/create-stripe-customer/$', billing_views.StripeCustomerCreateView.as_view(), name='stripe_customer_create'),
    url(r'^api/v1/subscribe-customer/$', billing_views.SubscribeCustomerView.as_view(), name='subscribe_customer'),
    url(r'^api/v1/cancel-subscription/$', billing_views.CancelSubscriptionView.as_view(), name='cancel_subscription'),
    url(r'^api/v1/charge-failed/$', billing_views.ChargeFailedView.as_view(), name='charge_failed'),
    url(r'^api/v1/charge-succeeded/$', billing_views.ChargeSucceededView.as_view(), name='charge_succeeded'),
    url(r'^api/v1/apply-promo-code/$', billing_views.ApplyPromoCodeView.as_view(), name='apply_promo_code'),
    url(r'^api/v1/', include(router.urls)),
]

urlpatterns += static('/dist/', document_root=settings.FRONTEND_DIR + '/dist/')
urlpatterns += static('/assets/', document_root=settings.FRONTEND_DIR + '/dist/assets/')
urlpatterns += static('/media/', document_root=settings.MEDIA_ROOT)
urlpatterns += static('/', document_root=settings.FRONTEND_DIR + '/dist/')
