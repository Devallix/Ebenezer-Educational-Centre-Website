from __future__ import annotations

import logging

from .models import AuditLog

logger = logging.getLogger("apps.core")


def _client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        candidate = forwarded.split(",")[0].strip()
        if candidate:
            return candidate
    return request.META.get("REMOTE_ADDR")


def log_action(request, action, instance=None, description="", model_name=None):
    """Record a significant administrative action for auditing."""
    user = getattr(request, "user", None)
    if user is not None and not getattr(user, "is_authenticated", False):
        user = None
    entry = AuditLog(
        user=user,
        action=action,
        model_name=model_name
        or (instance.__class__.__name__ if instance is not None else ""),
        object_id=str(getattr(instance, "pk", "") or ""),
        description=description[:255],
        ip_address=_client_ip(request),
    )
    try:
        entry.save()
    except Exception:  # pragma: no cover - auditing must never break a request
        logger.exception("Failed to write audit log entry")
    return entry
