from __future__ import annotations

from django.contrib import admin

from .models import AdmissionEnquiry, ContactMessage


@admin.register(AdmissionEnquiry)
class AdmissionEnquiryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "parent_name", "child_first_name", "preferred_class", "status", "is_read")
    list_filter = ("status", "is_read")
    search_fields = ("parent_name", "child_first_name", "phone", "email")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "subject", "category", "is_read", "is_archived")
    list_filter = ("category", "is_read", "is_archived")
    search_fields = ("name", "email", "subject")
