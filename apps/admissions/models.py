from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class EnquiryBase(models.Model):
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AdmissionEnquiry(EnquiryBase):
    STATUS_NEW = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_FOLLOW_UP = "follow_up"
    STATUS_RESOLVED = "resolved"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_FOLLOW_UP, "Follow-up required"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    parent_name = models.CharField(max_length=150, db_index=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    child_first_name = models.CharField(max_length=100)
    preferred_class = models.ForeignKey(
        "academics.ClassLevel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="admission_enquiries",
    )
    preferred_period = models.CharField(
        max_length=120, blank=True, help_text="Preferred start period or date."
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW, db_index=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_enquiries",
    )
    internal_notes = models.TextField(
        blank=True, help_text="Private notes. Never shown on the public website."
    )
    follow_up_date = models.DateField(null=True, blank=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    consent_given = models.BooleanField(default=False)
    source_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Admission enquiry"
        verbose_name_plural = "Admission enquiries"
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["is_read", "status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(phone__gt="") | models.Q(email__gt=""),
                name="admission_requires_contact_method",
            )
        ]

    def __str__(self) -> str:
        return f"{self.parent_name} - {self.child_first_name}"

    def clean(self):
        if not (self.phone or "").strip() and not (self.email or "").strip():
            raise ValidationError(
                "Provide at least a phone number or an email address so we can reply."
            )

    @property
    def is_active(self) -> bool:
        return self.status != self.STATUS_ARCHIVED

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_RESOLVED and self.resolved_at is None:
            from django.utils import timezone

            self.resolved_at = timezone.now()
        elif self.status != self.STATUS_RESOLVED:
            self.resolved_at = None
        super().save(*args, **kwargs)


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
