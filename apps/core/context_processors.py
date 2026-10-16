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

    nav_classes = []
    try:
        from apps.academics.models import ClassLevel

        nav_classes = list(
            ClassLevel.objects.filter(is_published=True).order_by("display_order", "name")
        )
    except Exception:  # pragma: no cover - during migrations
        nav_classes = []

    return {
        "school": school,
        "theme": theme,
        "theme_vars": theme.as_dict(),
        "nav_classes": nav_classes,
        "site_url": settings.SITE_URL,
        "current_year": date.today().year,
    }


def dashboard_context(request):
    """Lightweight context used by the dashboard shell (notifications badge)."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}
    unread_admissions = 0
    unread_messages = 0
    try:
        from apps.admissions.models import AdmissionEnquiry, ContactMessage

        unread_admissions = AdmissionEnquiry.objects.filter(
            is_read=False, is_archived=False
        ).count()
        unread_messages = ContactMessage.objects.filter(
            is_read=False, is_archived=False
        ).count()
    except Exception:  # pragma: no cover
        pass
    return {
        "unread_admissions": unread_admissions,
        "unread_messages": unread_messages,
        "unread_total": unread_admissions + unread_messages,
        "notification_settings": NotificationSettings.get_solo(),
    }
