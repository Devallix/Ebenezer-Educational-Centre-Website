from __future__ import annotations

import hashlib
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .models import SiteAnalyticsEvent

BOT_KEYWORDS = (
    "bot",
    "crawler",
    "spider",
    "crawl",
    "slurp",
    "bingpreview",
    "facebookexternalhit",
    "whatsapp",
    "telegrambot",
    "headless",
    "python-requests",
    "curl",
    "wget",
    "monitor",
    "uptime",
)

EXCLUDED_PREFIXES = (
    "/static/",
    "/media/",
    "/favicon",
    "/robots.txt",
    "/sitemap",
    "/health",
    "/dashboard/",
    "/accounts/",
    "/admin/",
)


def is_bot(user_agent: str) -> bool:
    ua = (user_agent or "").lower()
    return any(keyword in ua for keyword in BOT_KEYWORDS)


def detect_device(user_agent: str) -> str:
    ua = (user_agent or "").lower()
    if not ua:
        return SiteAnalyticsEvent.DEVICE_UNKNOWN
    if "ipad" in ua or ("tablet" in ua and "mobile" not in ua) or "kindle" in ua:
        return SiteAnalyticsEvent.DEVICE_TABLET
    if "mobi" in ua or "android" in ua or "iphone" in ua or "ipod" in ua:
        return SiteAnalyticsEvent.DEVICE_MOBILE
    if "windows" in ua or "macintosh" in ua or "linux" in ua or "x11" in ua:
        return SiteAnalyticsEvent.DEVICE_DESKTOP
    return SiteAnalyticsEvent.DEVICE_UNKNOWN


def referrer_domain(referrer: str) -> str:
    if not referrer:
        return ""
    try:
        host = urlparse(referrer).netloc.lower()
    except ValueError:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host[:255]


def visitor_hash(request) -> str:
    session = getattr(request, "session", None)
    if session is None:
        return ""
    if not session.session_key:
        session.save()
    salt = settings.SECRET_KEY[:16]
    raw = f"{session.session_key}:{salt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def should_track(request, path: str) -> bool:
    if request.method != "GET":
        return False
    if request.path.startswith(EXCLUDED_PREFIXES):
        return False
    if is_bot(request.META.get("HTTP_USER_AGENT", "")):
        return False
    return True


def record_pageview(request, path: str | None = None) -> None:
    path = path or request.path
    SiteAnalyticsEvent.objects.create(
        path=path[:255],
        event_type=SiteAnalyticsEvent.EVENT_PAGEVIEW,
        referrer_domain=referrer_domain(request.META.get("HTTP_REFERER", "")),
        device_category=detect_device(request.META.get("HTTP_USER_AGENT", "")),
        visitor_hash=visitor_hash(request),
        campaign_source=(request.GET.get("utm_source") or "")[:120],
        campaign_medium=(request.GET.get("utm_medium") or "")[:120],
    )


def record_event(request, event_type: str, path: str | None = None) -> None:
    """Record a conversion-style event (e.g. a contact submission)."""
    path = path or request.path
    SiteAnalyticsEvent.objects.create(
        path=path[:255],
        event_type=event_type,
        referrer_domain=referrer_domain(request.META.get("HTTP_REFERER", "")),
        device_category=detect_device(request.META.get("HTTP_USER_AGENT", "")),
        visitor_hash=visitor_hash(request),
    )


def purge_old_events() -> int:
    """Delete analytics events older than the configured retention window."""
    days = getattr(settings, "ANALYTICS_RETENTION_DAYS", 180)
    if not days or days <= 0:
        return 0
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = SiteAnalyticsEvent.objects.filter(created_at__lt=cutoff).delete()
    return deleted


def clear_cache_keys():
    cache.delete("analytics:overview")
