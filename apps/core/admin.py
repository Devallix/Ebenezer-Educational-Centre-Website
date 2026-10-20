from __future__ import annotations

from django.contrib import admin

from .models import (
    AuditLog,
    NotificationLog,
    NotificationSettings,
    SchoolSettings,
    ThemeSettings,
)


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ("school_name", "town", "region", "updated_at")


@admin.register(ThemeSettings)
class ThemeSettingsAdmin(admin.ModelAdmin):
    list_display = ("primary_color", "secondary_color", "accent_color", "updated_at")


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ("sender_name", "notify_contact")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("kind", "status", "subject", "created_at")
    list_filter = ("kind", "status")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "model_name", "description")
    list_filter = ("action", "model_name")
    search_fields = ("description", "object_id")
