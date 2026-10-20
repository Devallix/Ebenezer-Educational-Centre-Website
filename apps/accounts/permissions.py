from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator

from django.conf import settings

ROLE_SUPER_ADMIN = settings.ROLE_SUPER_ADMIN
ROLE_WEBSITE_ADMIN = settings.ROLE_WEBSITE_ADMIN
ROLE_ENQUIRIES_OFFICER = settings.ROLE_ENQUIRIES_OFFICER
ROLE_CONTENT_EDITOR = settings.ROLE_CONTENT_EDITOR
ROLE_CHOICES = settings.ROLE_CHOICES

ALL_STAFF_ROLES = (
    ROLE_SUPER_ADMIN,
    ROLE_WEBSITE_ADMIN,
    ROLE_ENQUIRIES_OFFICER,
    ROLE_CONTENT_EDITOR,
)

# capability -> roles allowed (superusers always allowed)
CAPABILITIES = {
    "dashboard_access": set(ALL_STAFF_ROLES),
    "analytics_view": set(ALL_STAFF_ROLES),
    "messages_manage": {ROLE_SUPER_ADMIN, ROLE_WEBSITE_ADMIN, ROLE_ENQUIRIES_OFFICER},
    "content_manage": {ROLE_SUPER_ADMIN, ROLE_WEBSITE_ADMIN, ROLE_CONTENT_EDITOR},
    "settings_manage": {ROLE_SUPER_ADMIN, ROLE_WEBSITE_ADMIN},
    "appearance_manage": {ROLE_SUPER_ADMIN, ROLE_WEBSITE_ADMIN},
    "seo_manage": {ROLE_SUPER_ADMIN, ROLE_WEBSITE_ADMIN},
    "notifications_manage": {ROLE_SUPER_ADMIN, ROLE_WEBSITE_ADMIN},
    "users_manage": {ROLE_SUPER_ADMIN},
    "system_manage": {ROLE_SUPER_ADMIN},
}

ROLE_GROUPS = {
    ROLE_SUPER_ADMIN: "Super Administrators",
    ROLE_WEBSITE_ADMIN: "Website Administrators",
    ROLE_ENQUIRIES_OFFICER: "Enquiries Officers",
    ROLE_CONTENT_EDITOR: "Content Editors",
}

# Group name -> role code, used to translate stored group membership back into
# the role codes that CAPABILITIES is keyed on.
GROUP_TO_ROLE = {group: code for code, group in ROLE_GROUPS.items()}


def get_user_roles(user) -> set[str]:
    """Return the set of role CODES (e.g. ``"superadmin"``) for a user.

    Roles are stored as Django group memberships, so the group names are mapped
    back to the codes that :data:`CAPABILITIES` is keyed on.
    """
    if not getattr(user, "is_authenticated", False):
        return set()
    group_names = set(user.groups.values_list("name", flat=True))
    return {GROUP_TO_ROLE[name] for name in group_names if name in GROUP_TO_ROLE}


def user_can(user, capability: str) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    allowed = CAPABILITIES.get(capability, set())
    return bool(get_user_roles(user) & allowed)


def user_is_staff_member(user) -> bool:
    return user_can(user, "dashboard_access")


def capability_required(capability: str):
    """Decorator: require login and a specific dashboard capability."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if not user_can(request.user, capability):
                raise PermissionDenied("You do not have permission to do that.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class CapabilityRequiredMixin:
    """CBV mixin enforcing a dashboard capability."""

    capability = "dashboard_access"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not user_can(request.user, self.capability):
            raise PermissionDenied("You do not have permission to do that.")
        return super().dispatch(request, *args, **kwargs)
