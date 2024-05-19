from django.conf import settings
from rest_framework.permissions import BasePermission


class PrivateTokenPermission(BasePermission):
    def has_permission(self, request, view):
        return settings.PRIVATE_API_TOKEN and request.query_params.get('token') == settings.PRIVATE_API_TOKEN
