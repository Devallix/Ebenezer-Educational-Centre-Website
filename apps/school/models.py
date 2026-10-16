from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from apps.core.models import TimeStampedModel
from apps.core.validators import ImageValidator


class HeroSlide(TimeStampedModel):
    label = models.CharField(
        max_length=120,
        blank=True,
        default="WELCOME TO EBENEZER EDUCATIONAL CENTRE",
    )
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="hero/", blank=True, null=True, validators=[ImageValidator()]
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Describe the image for screen readers.",
    )
    primary_button_label = models.CharField(max_length=60, blank=True)
    primary_button_url = models.CharField(
        max_length=255, blank=True, help_text="Relative path such as /classes/ or full URL."
    )
    secondary_button_label = models.CharField(max_length=60, blank=True)
    secondary_button_url = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Hero slide"
        verbose_name_plural = "Hero slides"

    def __str__(self) -> str:
        return self.title

    @property
    def image_url(self) -> str:
        if self.image:
            try:
                return self.image.url
            except ValueError:
                return ""
        return ""


# Editable banner (page hero) shown at the top of each public page.
# Defaults are used to seed an editable row per page and as a fallback.
PAGE_HERO_DEFAULTS = {
    "about": {
        "title": "About Us",
        "subtitle": (
            "Discover who we are, what we believe and how we help children take "
            "their first confident steps in learning."
        ),
    },
    "classes": {
        "title": "Our Classes",
        "subtitle": (
            "We welcome children from Creche through to Primary 3, with a caring "
            "and age-appropriate programme at every level."
        ),
    },
    "programmes": {
        "title": "Programmes & Curriculum",
        "subtitle": (
            "Our learning areas help children build strong foundations through play, "
            "exploration and guided teaching."
        ),
    },
    "gallery": {
        "title": "Photo Gallery",
        "subtitle": (
            "A glimpse into everyday life at our school \u2014 learning, play and celebration."
        ),
    },
    "contact": {
        "title": "Contact Us",
        "subtitle": (
            "We would love to hear from you. Send us a message and our team will "
            "respond as soon as possible."
        ),
    },
    "admission": {
        "title": "Admission Enquiries",
        "subtitle": (
            "Interested in a place for your child? Send us an enquiry and our team "
            "will guide you through availability and the next steps."
        ),
    },
    "privacy": {
        "title": "Privacy Policy",
        "subtitle": "How we handle the information you share with us.",
    },
}


class PageHero(TimeStampedModel):
    PAGE_CHOICES = [
        ("about", "About Us"),
        ("classes", "Classes"),
        ("programmes", "Programmes"),
        ("gallery", "Gallery"),
        ("contact", "Contact Us"),
        ("admission", "Admission Enquiries"),
        ("privacy", "Privacy Policy"),
    ]

    key = models.CharField(max_length=40, unique=True, choices=PAGE_CHOICES)
    label = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional small text shown above the heading.",
    )
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="page-heroes/", blank=True, null=True, validators=[ImageValidator()]
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["key"]
        verbose_name = "Page hero"
        verbose_name_plural = "Page heroes"

    def __str__(self) -> str:
        return self.get_key_display()


class SchoolBenefit(TimeStampedModel):
    title = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.CharField(
        max_length=60,
        blank=True,
        default="bi-star",
        help_text="A Bootstrap Icons class name, e.g. bi-heart.",
    )
    display_order = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    is_published = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "School benefit"
        verbose_name_plural = "School benefits"

    def __str__(self) -> str:
        return self.title
