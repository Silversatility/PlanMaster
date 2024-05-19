from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
from reversion.middleware import RevisionMiddleware


class BypassRevisionMiddleware(RevisionMiddleware):
    atomic = False

    def request_creates_revision(self, request):
        silent = request.META.get("HTTP_X_NOREVISION", "false")
        return super().request_creates_revision(request) and \
            silent != "true"


def maintenance_mode(get_response):
    def middleware(request):
        if settings.MAINTENANCE_MODE and not request.path.startswith('/dist/assets/'):
            if request.user.is_authenticated:
                logout(request)
            return render(request, 'maintenance-mode.html', status=503)
        return get_response(request)

    return middleware


class RequestRoleMiddleware(MiddlewareMixin):
    def _get_or_set_user_active_role(self, request):
        active_role = None
        if not request.user.is_authenticated:
            return active_role
        if request.user.active_role:
            active_role = request.user.active_role
            return active_role
        if request.user.roles.exists():
            active_role = request.user.roles.first()
            request.user.active_role = active_role
            request.user.save()
            return active_role
        return active_role

    def process_request(self, request):
        request.role = self._get_or_set_user_active_role(request)
