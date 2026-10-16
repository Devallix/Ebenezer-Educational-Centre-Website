from __future__ import annotations

from django import template
from django.conf import settings

from apps.accounts.permissions import get_user_roles, user_can

register = template.Library()


@register.filter(name="can")
def can(user, capability: str) -> bool:
    return user_can(user, capability)


@register.filter(name="has_role")
def has_role(user, role_code: str) -> bool:
    return role_code in get_user_roles(user)


@register.simple_tag
def role_label(code: str) -> str:
    return dict(settings.ROLE_CHOICES).get(code, code)
