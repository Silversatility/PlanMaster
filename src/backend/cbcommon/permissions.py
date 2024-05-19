from rules.predicates import is_authenticated, is_superuser
from rest_framework.permissions import BasePermission


class RulesPermissions(BasePermission):
    def has_permission(self, request, view):
        if not is_authenticated(request.user):
            return False

        if not hasattr(view, 'permission_rules') or view.action not in view.permission_rules:
            return True  # allow unconfigured views

        if view.action in ('retrieve', 'update', 'partial_update', 'delete') or view.kwargs:
            return True  # let has_object_permission deal with it

        rule = view.permission_rules[view.action]
        return (is_authenticated & (is_superuser | rule)).test(request.user)

    def has_object_permission(self, request, view, obj):
        if not is_authenticated(request.user):
            return False

        if not hasattr(view, 'permission_rules') or view.action not in view.permission_rules:
            return True  # allow unconfigured views

        rule = view.permission_rules[view.action]
        return (is_authenticated & (is_superuser | rule)).test(request.user, obj)
