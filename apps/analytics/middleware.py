from __future__ import annotations

import logging

from .services import is_bot, record_pageview, should_track

logger = logging.getLogger("apps.analytics")


class AnalyticsMiddleware:
    """Record first-party page views for public pages only."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if (
                response.status_code == 200
                and getattr(request, "resolver_match", None) is not None
                and should_track(request, request.path)
            ):
                record_pageview(request)
        except Exception:  # pragma: no cover - never break a request for analytics
            logger.exception("Failed to record analytics page view")
        return response
