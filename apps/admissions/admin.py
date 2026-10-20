from __future__ import annotations

from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "subject", "category", "is_read", "is_archived")
    list_filter = ("category", "is_read", "is_archived")
    search_fields = ("name", "email", "subject")
