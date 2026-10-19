from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.core.models import TimeStampedModel
from apps.core.validators import ImageValidator, VideoValidator


class GalleryAlbum(TimeStampedModel):
    CATEGORY_CHOICES = [
        ("classroom", "Classroom"),
        ("activities", "Activities"),
        ("events", "Events"),
        ("outdoor", "Outdoor Play"),
        ("facilities", "Facilities"),
        ("general", "General"),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default="general", db_index=True
    )
    cover_image = models.ImageField(
        upload_to="gallery/covers/", blank=True, null=True, validators=[ImageValidator()]
    )
    cover_video = models.FileField(
        upload_to="gallery/videos/", blank=True, null=True, validators=[VideoValidator()]
    )
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Gallery album"
        verbose_name_plural = "Gallery albums"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):
        if self.is_published and self.pk and self.image_count < 2:
            raise ValidationError(
                "A published album must contain at least two published images."
            )

    def get_absolute_url(self) -> str:
        return reverse("gallery:album_detail", kwargs={"slug": self.slug})

    @property
    def published_images(self):
        return self.images.filter(is_published=True).order_by("display_order", "id")

    @property
    def image_count(self) -> int:
        return self.images.filter(is_published=True).count()

    @property
    def cover_url(self) -> str:
        if self.cover_image:
            try:
                return self.cover_image.url
            except ValueError:
                pass
        first = self.published_images.first()
        if first and first.image:
            try:
                return first.image.url
            except ValueError:
                return ""
        return ""

    @property
    def video_url(self) -> str:
        if self.cover_video:
            try:
                return self.cover_video.url
            except ValueError:
                pass
        return ""

    @property
    def can_publish(self) -> bool:
        return self.image_count >= 2


class GalleryImage(TimeStampedModel):
    album = models.ForeignKey(
        GalleryAlbum, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="gallery/images/", blank=True, null=True, validators=[ImageValidator()]
    )
    video = models.FileField(
        upload_to="gallery/videos/", blank=True, null=True, validators=[VideoValidator()]
    )
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Describe the image. Defaults to the caption if left blank.",
    )
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Gallery image"
        verbose_name_plural = "Gallery images"
        indexes = [models.Index(fields=["album", "is_published", "display_order"])]

    def __str__(self) -> str:
        return self.caption or f"Image #{self.pk}"

    @property
    def effective_alt(self) -> str:
        return self.alt_text or self.caption or "Photograph from the school gallery"

    @property
    def url(self) -> str:
        try:
            return self.image.url
        except ValueError:
            return ""

    @property
    def video_url(self) -> str:
        if self.video:
            try:
                return self.video.url
            except ValueError:
                pass
        return ""

    @property
    def is_video(self) -> bool:
        return bool(self.video)

    @property
    def media_url(self) -> str:
        return self.video_url if self.is_video else self.url
