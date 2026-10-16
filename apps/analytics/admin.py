from __future__ import annotations

from django.contrib import admin

from .models import SiteAnalyticsEvent


@admin.register(SiteAnalyticsEvent)
class SiteAnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "event_type", "path", "device_category")
    list_filter = ("event_type", "device_category")
    search_fields = ("path", "referrer_domain")
    date_hierarchy = "created_at"
