from __future__ import annotations

from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import SingletonModel

hex_validator = RegexValidator(
    regex=r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$",
    message="Enter a valid hexadecimal colour value such as #9E0719.",
)


class SEOSettings(SingletonModel):
    CACHE_KEY = "settings:seo"

    site_title = models.CharField(
        max_length=150, default="Ebenezer Educational Centre | Jukwa, Cape Coast"
    )
    default_meta_description = models.TextField(
        blank=True,
        max_length=320,
        help_text="Fallback meta description for pages without their own.",
    )
    canonical_base_url = models.URLField(
        blank=True,
        help_text="Leave blank to use the SITE_URL environment variable.",
    )
    default_share_image = models.ImageField(
        upload_to="seo/", blank=True, null=True
    )
    allow_indexing = models.BooleanField(
        default=False,
        help_text="Allow search engines to index the public site.",
    )
    enable_sitemap = models.BooleanField(default=True)
    verification_google = models.CharField(max_length=200, blank=True)
    verification_bing = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SEO settings"
        verbose_name_plural = "SEO settings"

    def __str__(self) -> str:
        return "SEO settings"

    def canonical_base(self) -> str:
        from django.conf import settings

        return (self.canonical_base_url or settings.SITE_URL).rstrip("/")

    def robots_directive(self) -> str:
        return "index, follow" if self.allow_indexing else "noindex, nofollow"


class PageSEO(models.Model):
    KEY_HOME = "home"
    KEY_ABOUT = "about"
    KEY_CLASSES = "classes"
    KEY_PROGRAMMES = "programmes"
    KEY_GALLERY = "gallery"
    KEY_CONTACT = "contact"
    KEY_ADMISSION = "admission"
    KEY_CHOICES = [
        (KEY_HOME, "Home"),
        (KEY_ABOUT, "About"),
        (KEY_CLASSES, "Classes"),
        (KEY_PROGRAMMES, "Programmes"),
        (KEY_GALLERY, "Gallery"),
        (KEY_CONTACT, "Contact Us"),
        (KEY_ADMISSION, "Admission"),
    ]

    key = models.CharField(max_length=40, choices=KEY_CHOICES, unique=True)
    title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True, max_length=320)
    canonical_url = models.URLField(blank=True)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.TextField(blank=True, max_length=320)
    og_image = models.ImageField(upload_to="seo/", blank=True, null=True)
    index = models.BooleanField(default=True)
    follow = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]
        verbose_name = "Page SEO"
        verbose_name_plural = "Page SEO"

    def __str__(self) -> str:
        return self.get_key_display()

    @property
    def robots(self) -> str:
        return f"{'index' if self.index else 'noindex'}, {'follow' if self.follow else 'nofollow'}"
