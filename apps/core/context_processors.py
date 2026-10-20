from __future__ import annotations

from datetime import date

from django.conf import settings

from .models import NotificationSettings, SchoolSettings, ThemeSettings


def site_context(request):
    """Expose school/theme configuration to every template.

    Results are cheap: the settings singletons are cached in memory.
    """
    school = SchoolSettings.get_solo()
    theme = ThemeSettings.get_solo()

    return {
        "school": school,
        "theme": theme,
        "theme_vars": theme.as_dict(),
        "site_url": settings.SITE_URL,
        "current_year": date.today().year,
    }


def dashboard_context(request):
    """Lightweight context used by the dashboard shell (notifications badge)."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}
    unread_messages = 0
    try:
        from apps.admissions.models import ContactMessage

        unread_messages = ContactMessage.objects.filter(
            is_read=False, is_archived=False
        ).count()
    except Exception:  # pragma: no cover
        pass
    return {
        "unread_messages": unread_messages,
        "unread_total": unread_messages,
        "notification_settings": NotificationSettings.get_solo(),
    }
