from __future__ import annotations

from django.db import models


class SiteAnalyticsEvent(models.Model):
    EVENT_PAGEVIEW = "pageview"
    EVENT_ADMISSION = "admission_submit"
    EVENT_CONTACT = "contact_submit"
    EVENT_CHOICES = [
        (EVENT_PAGEVIEW, "Page view"),
        (EVENT_ADMISSION, "Admission enquiry submitted"),
        (EVENT_CONTACT, "Contact message submitted"),
    ]

    DEVICE_DESKTOP = "desktop"
    DEVICE_MOBILE = "mobile"
    DEVICE_TABLET = "tablet"
    DEVICE_UNKNOWN = "unknown"
    DEVICE_CHOICES = [
        (DEVICE_DESKTOP, "Desktop"),
        (DEVICE_MOBILE, "Mobile"),
        (DEVICE_TABLET, "Tablet"),
        (DEVICE_UNKNOWN, "Unknown"),
    ]

    path = models.CharField(max_length=255, db_index=True)
    event_type = models.CharField(
        max_length=30, choices=EVENT_CHOICES, default=EVENT_PAGEVIEW, db_index=True
    )
    referrer_domain = models.CharField(max_length=255, blank=True)
    device_category = models.CharField(
        max_length=20, choices=DEVICE_CHOICES, default=DEVICE_UNKNOWN, db_index=True
    )
    visitor_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="Privacy-preserving hash of an anonymous session identifier.",
    )
    campaign_source = models.CharField(max_length=120, blank=True)
    campaign_medium = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Analytics event"
        verbose_name_plural = "Analytics events"
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["path", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_event_type_display()}: {self.path}"
