from __future__ import annotations

from django.conf import settings
from django.core.cache import cache
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    """A model with exactly one row, cached for cheap repeated access."""

    CACHE_KEY = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        self.clear_cache()

    def delete(self, *args, **kwargs):  # pragma: no cover - guard misuse
        raise RuntimeError("Singleton settings rows may not be deleted.")

    @classmethod
    def _cache_key(cls) -> str:
        return cls.CACHE_KEY or f"singleton:{cls._meta.label}"

    @classmethod
    def get_solo(cls):
        key = cls._cache_key()
        obj = cache.get(key)
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set(key, obj, None)
        return obj

    @classmethod
    def clear_cache(cls):
        cache.delete(cls._cache_key())


class SchoolSettings(SingletonModel):
    CACHE_KEY = "settings:school"

    school_name = models.CharField(max_length=150, default="Ebenezer Educational Centre")
    short_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Used in the footer and social sharing cards.",
    )
    tagline = models.CharField(
        max_length=200,
        blank=True,
        help_text="Short tagline shown below the school name in the navbar.",
    )
    full_description = models.TextField(
        blank=True,
        help_text="Longer introduction used on the homepage and About page.",
    )

    address = models.CharField(max_length=255, blank=True, default="Jukwa, Cape Coast")
    town = models.CharField(max_length=100, blank=True, default="Jukwa")
    region = models.CharField(max_length=100, blank=True, default="Central Region")
    country = models.CharField(max_length=100, blank=True, default="Ghana")

    phone_primary = models.CharField(max_length=40, blank=True)
    phone_secondary = models.CharField(max_length=40, blank=True)
    email_primary = models.EmailField(blank=True)
    email_secondary = models.EmailField(blank=True)
    opening_hours = models.CharField(
        max_length=200, blank=True, default="Monday - Friday, 7:00am - 4:00pm"
    )

    vision = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    proprietress_name = models.CharField(max_length=150, blank=True)
    proprietress_title = models.CharField(
        max_length=150, blank=True, default="Proprietress"
    )
    proprietress_message = models.TextField(blank=True)
    headmistress_image = models.ImageField(
        upload_to="branding/",
        blank=True,
        null=True,
        help_text="Optional photo of the school headmistress.",
    )

    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    logo_light = models.ImageField(
        upload_to="branding/",
        blank=True,
        null=True,
        help_text="Optional logo variant for dark backgrounds.",
    )
    favicon = models.ImageField(upload_to="branding/", blank=True, null=True)
    default_image = models.ImageField(
        upload_to="branding/", blank=True, null=True
    )

    map_url = models.URLField(
        blank=True,
        max_length=1000,
        help_text="Google Maps embed URL (Share → Embed a map in Google Maps), not a short sharing link. Leave blank to hide the map.",
    )
    directions_url = models.URLField(blank=True)

    footer_intro = models.TextField(blank=True)
    footer_copyright = models.CharField(max_length=255, blank=True)

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=40, blank=True)

    privacy_policy = models.TextField(
        blank=True, help_text="Privacy policy content shown on the privacy page."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School settings"
        verbose_name_plural = "School settings"

    def __str__(self) -> str:
        return self.school_name

    @property
    def full_address(self) -> str:
        parts = [self.address, self.town, self.region, self.country]
        return ", ".join(part for part in parts if part)

    @property
    def social_links(self) -> list[dict]:
        links = [
            ("Facebook", "bi-facebook", self.facebook_url),
            ("Instagram", "bi-instagram", self.instagram_url),
            ("X (Twitter)", "bi-twitter-x", self.twitter_url),
            ("TikTok", "bi-tiktok", self.tiktok_url),
            ("YouTube", "bi-youtube", self.youtube_url),
            ("LinkedIn", "bi-linkedin", self.linkedin_url),
        ]
        if self.whatsapp_number:
            digits = "".join(ch for ch in self.whatsapp_number if ch.isdigit())
            if digits:
                links.append(
                    ("WhatsApp", "bi-whatsapp", f"https://wa.me/{digits}")
                )
        return [{"label": label, "icon": icon, "url": url} for label, icon, url in links if url]


class ThemeSettings(SingletonModel):
    CACHE_KEY = "settings:theme"

    DEFAULTS = {
        "primary_color": "#9E0719",
        "secondary_color": "#BD0116",
        "accent_color": "#D5720A",
        "background_color": "#FFFBF7",
        "surface_color": "#FFFFFF",
        "text_color": "#241417",
        "muted_color": "#7A6B6E",
        "border_color": "#EADFD8",
        "sidebar_bg": "#6E0411",
        "sidebar_text": "#F7E9E4",
        "sidebar_active": "#D5720A",
    }

    primary_color = models.CharField(max_length=7, default="#9E0719")
    secondary_color = models.CharField(max_length=7, default="#BD0116")
    accent_color = models.CharField(max_length=7, default="#D5720A")
    background_color = models.CharField(max_length=7, default="#FFFBF7")
    surface_color = models.CharField(max_length=7, default="#FFFFFF")
    text_color = models.CharField(max_length=7, default="#241417")
    muted_color = models.CharField(max_length=7, default="#7A6B6E")
    border_color = models.CharField(max_length=7, default="#EADFD8")
    sidebar_bg = models.CharField(max_length=7, default="#6E0411")
    sidebar_text = models.CharField(max_length=7, default="#F7E9E4")
    sidebar_active = models.CharField(max_length=7, default="#D5720A")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Theme settings"
        verbose_name_plural = "Theme settings"

    def __str__(self) -> str:
        return "Theme settings"

    def as_dict(self) -> dict[str, str]:
        return {
            key: getattr(self, key, value) or value
            for key, value in self.DEFAULTS.items()
        }

    def reset_to_defaults(self):
        for key, value in self.DEFAULTS.items():
            setattr(self, key, value)
        self.save()


class NotificationSettings(SingletonModel):
    CACHE_KEY = "settings:notifications"

    recipient_emails = models.TextField(
        blank=True,
        help_text="Comma-separated list of staff addresses that receive alerts.",
    )
    notify_admissions = models.BooleanField(default=True)
    notify_contact = models.BooleanField(default=True)
    send_parent_confirmation = models.BooleanField(
        default=False,
        help_text="Send an acknowledgement email to the parent after an enquiry.",
    )
    sender_name = models.CharField(
        max_length=150, blank=True, default="Ebenezer Educational Centre"
    )
    sender_email = models.EmailField(
        blank=True, help_text="Leave blank to use the DEFAULT_FROM_EMAIL setting."
    )
    admission_subject = models.CharField(
        max_length=200, blank=True, default="New admission enquiry"
    )
    contact_subject = models.CharField(
        max_length=200, blank=True, default="New website message"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notification settings"
        verbose_name_plural = "Notification settings"

    def __str__(self) -> str:
        return "Notification settings"

    @property
    def recipients(self) -> list[str]:
        addresses = [
            addr.strip() for addr in self.recipient_emails.replace(";", ",").split(",")
        ]
        addresses = [addr for addr in addresses if addr]
        if not addresses and settings.SCHOOL_NOTIFICATION_EMAIL:
            addresses = [
                addr.strip()
                for addr in settings.SCHOOL_NOTIFICATION_EMAIL.split(",")
                if addr.strip()
            ]
        return addresses


class NotificationLog(models.Model):
    """Records outbound notification emails and any delivery failures."""

    KIND_STAFF = "staff"
    KIND_PARENT = "parent"
    KIND_CHOICES = [(KIND_STAFF, "Staff notification"), (KIND_PARENT, "Parent confirmation")]

    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [(STATUS_SENT, "Sent"), (STATUS_FAILED, "Failed")]

    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    recipients = models.CharField(max_length=500, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    related_model = models.CharField(max_length=120, blank=True)
    related_object_id = models.CharField(max_length=64, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification log"
        verbose_name_plural = "Notification log"

    def __str__(self) -> str:
        return f"{self.get_kind_display()} - {self.status}"


class AuditLog(models.Model):
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"
    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_OTHER = "other"
    ACTION_CHOICES = [
        (ACTION_CREATE, "Created"),
        (ACTION_UPDATE, "Updated"),
        (ACTION_DELETE, "Deleted"),
        (ACTION_LOGIN, "Logged in"),
        (ACTION_LOGOUT, "Logged out"),
        (ACTION_OTHER, "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_entries",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default=ACTION_OTHER)
    model_name = models.CharField(max_length=120, blank=True)
    object_id = models.CharField(max_length=64, blank=True)
    description = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Audit log entry"
        verbose_name_plural = "Audit log"

    def __str__(self) -> str:
        who = self.user.get_username() if self.user else "system"
        return f"{who} {self.get_action_display()} {self.model_name}".strip()
