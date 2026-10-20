from __future__ import annotations

from collections import OrderedDict
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import SiteAnalyticsEvent

RANGE_PRESETS = {
    "7": 7,
    "30": 30,
    "90": 90,
}


def parse_range(request):
    """Return (start, end, label, days) for the requested analytics window."""
    now = timezone.now()
    range_key = (request.GET.get("range") or "30").strip()
    start_param = request.GET.get("start")
    end_param = request.GET.get("end")

    if range_key == "custom" and start_param and end_param:
        try:
            start_date = timezone.datetime.fromisoformat(start_param).date()
            end_date = timezone.datetime.fromisoformat(end_param).date()
        except ValueError:
            range_key = "30"
        else:
            if start_date > end_date:
                start_date, end_date = end_date, start_date
            start = timezone.make_aware(
                timezone.datetime.combine(start_date, timezone.datetime.min.time())
            )
            end = timezone.make_aware(
                timezone.datetime.combine(end_date, timezone.datetime.max.time())
            )
            label = f"{start_date.isoformat()} to {end_date.isoformat()}"
            return start, end, label, (end_date - start_date).days + 1

    days = RANGE_PRESETS.get(range_key, 30)
    end = now
    start = now - timedelta(days=days - 1)
    start = timezone.make_aware(
        timezone.datetime.combine(start.date(), timezone.datetime.min.time())
    )
    labels = {"7": "Last 7 days", "30": "Last 30 days", "90": "Last 90 days"}
    return start, end, labels.get(range_key, "Last 30 days"), days


def base_events(start, end):
    return SiteAnalyticsEvent.objects.filter(
        created_at__gte=start, created_at__lte=end,
        event_type=SiteAnalyticsEvent.EVENT_PAGEVIEW,
    )


def total_pageviews(start, end) -> int:
    return base_events(start, end).count()


def unique_visitors(start, end) -> int:
    return (
        base_events(start, end)
        .exclude(visitor_hash="")
        .values("visitor_hash")
        .distinct()
        .count()
    )


def views_by_day(start, end):
    rows = (
        base_events(start, end)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )
    data = OrderedDict()
    cursor = start.date()
    last = end.date()
    while cursor <= last:
        data[cursor] = 0
        cursor += timedelta(days=1)
    for row in rows:
        if row["day"] in data:
            data[row["day"]] = row["total"]
    return list(data.keys()), list(data.values())


def top_pages(start, end, limit=10):
    return list(
        base_events(start, end)
        .values("path")
        .annotate(total=Count("id"))
        .order_by("-total")[:limit]
    )


def _path_count(start, end, prefixes):
    from django.db.models import Q

    query = Q()
    for prefix in prefixes:
        query |= Q(path__startswith=prefix)
    return base_events(start, end).filter(query).count()


def section_totals(start, end) -> dict[str, int]:
    return {
        "gallery": _path_count(start, end, ["/gallery/"]),
        "contact": _path_count(start, end, ["/contact/"]),
    }


def device_breakdown(start, end):
    rows = (
        base_events(start, end)
        .values("device_category")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    labels = dict(SiteAnalyticsEvent.DEVICE_CHOICES)
    return [(labels.get(r["device_category"], r["device_category"]), r["total"]) for r in rows]


def referrer_sources(start, end, limit=8):
    rows = (
        base_events(start, end)
        .exclude(referrer_domain="")
        .values("referrer_domain")
        .annotate(total=Count("id"))
        .order_by("-total")[:limit]
    )
    return [(r["referrer_domain"], r["total"]) for r in rows]


def conversion_counts(start, end) -> dict[str, int]:
    rows = (
        SiteAnalyticsEvent.objects.filter(created_at__gte=start, created_at__lte=end)
        .exclude(event_type=SiteAnalyticsEvent.EVENT_PAGEVIEW)
        .values("event_type")
        .annotate(total=Count("id"))
    )
    mapping = {r["event_type"]: r["total"] for r in rows}
    return {
        "contact_submits": mapping.get(SiteAnalyticsEvent.EVENT_CONTACT, 0),
    }
