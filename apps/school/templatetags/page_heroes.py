from __future__ import annotations

from django import template

from apps.school.models import PageHero

register = template.Library()


@register.simple_tag
def get_page_hero(key):
    """Return the editable PageHero for a page key, or None.

    Templates fall back to sensible defaults when no row exists yet, so the
    public site always renders correctly even before an admin edits a hero.
    """
    try:
        return PageHero.objects.filter(key=key, is_active=True).first()
    except Exception:
        return None
