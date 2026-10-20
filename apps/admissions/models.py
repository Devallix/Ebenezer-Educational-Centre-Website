from __future__ import annotations

from django.db import models


class EnquiryBase(models.Model):
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContactMessage(EnquiryBase):
    CATEGORY_CHOICES = [
        ("general", "General enquiry"),
        ("admission", "Admission question"),
        ("academics", "Academic programme"),
        ("visit", "Schedule a visit"),
        ("careers", "Careers / employment"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=150, db_index=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default="general", db_index=True
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    consent_given = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False, db_index=True)
    source_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact message"
        verbose_name_plural = "Contact messages"

    def __str__(self) -> str:
        return f"{self.name}: {self.subject}"
