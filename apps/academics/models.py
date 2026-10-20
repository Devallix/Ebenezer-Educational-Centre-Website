from __future__ import annotations

from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel
from apps.core.validators import ImageValidator


class ClassLevel(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    short_introduction = models.CharField(max_length=255, blank=True)
    overview = models.TextField(
        blank=True, help_text="Full description shown on the class detail page."
    )
    age_range = models.CharField(
        max_length=60,
        blank=True,
        help_text="Only shown publicly when 'Show age range' is enabled.",
    )
    show_age_range = models.BooleanField(
        default=False,
        help_text="Publish the age range once it has been confirmed by the school.",
    )
    developmental_focus = models.CharField(
        max_length=200, blank=True, help_text="Short summary of the focus for this class."
    )
    image = models.ImageField(
        upload_to="classes/", blank=True, null=True, validators=[ImageValidator()]
    )
    image_alt = models.CharField(
        max_length=200,
        blank=True,
        help_text="Describe the image for screen readers.",
    )
    hero_image = models.ImageField(
        upload_to="classes/", blank=True, null=True, validators=[ImageValidator()]
    )
    group_photo = models.ImageField(
        upload_to="classes/",
        blank=True,
        null=True,
        validators=[ImageValidator()],
        help_text="Approved class group photograph.",
    )
    group_photo_alt = models.CharField(max_length=200, blank=True)
    gallery_album = models.ForeignKey(
        "gallery.GalleryAlbum",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="class_levels",
    )
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def published_age_range(self) -> str:
        return self.age_range if self.show_age_range else ""

    @property
    def programmes(self):
        return (
            self.programme_links.select_related("learning_area")
            .filter(learning_area__is_published=True)
            .order_by("display_order", "learning_area__display_order")
        )


class LearningArea(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=60, blank=True, default="bi-book", help_text="Bootstrap Icons class."
    )
    image = models.ImageField(
        upload_to="programmes/", blank=True, null=True, validators=[ImageValidator()]
    )
    objectives = models.TextField(
        blank=True, help_text="One learning objective per line."
    )
    example_activities = models.TextField(
        blank=True, help_text="One example activity per line."
    )
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Learning area"
        verbose_name_plural = "Learning areas / programmes"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def objective_list(self) -> list[str]:
        return [line.strip() for line in self.objectives.splitlines() if line.strip()]

    @property
    def activity_list(self) -> list[str]:
        return [
            line.strip() for line in self.example_activities.splitlines() if line.strip()
        ]


class ClassProgramme(models.Model):
    """Links a learning area to a class, allowing per-class ordering and notes."""

    class_level = models.ForeignKey(
        ClassLevel, on_delete=models.CASCADE, related_name="programme_links"
    )
    learning_area = models.ForeignKey(
        LearningArea, on_delete=models.CASCADE, related_name="class_links"
    )
    notes = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_level", "learning_area"],
                name="unique_class_programme",
            )
        ]
        verbose_name = "Class programme"
        verbose_name_plural = "Class programmes"

    def __str__(self) -> str:
        return f"{self.learning_area} in {self.class_level}"
