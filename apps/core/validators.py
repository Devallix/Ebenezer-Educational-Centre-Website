from __future__ import annotations

import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:  # pragma: no cover
    Image = None
    UnidentifiedImageError = Exception

ALLOWED_RASTER = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_VECTOR = {".svg"}
ALLOWED_ICON = {".ico"}
ALLOWED_VIDEO = {".mp4", ".webm", ".ogg", ".mov"}

# Guard against decompression-bomb style images.
MAX_IMAGE_PIXELS = 40_000_000


@deconstructible
class ImageValidator:
    """Validate an uploaded file is really an image of an allowed type/size."""

    def __init__(self, allow_svg: bool = False, max_size: int | None = None):
        self.allow_svg = allow_svg
        self.max_size = max_size or getattr(settings, "MAX_UPLOAD_SIZE", 5 * 1024 * 1024)

    @property
    def allowed_extensions(self) -> set[str]:
        allowed = set(ALLOWED_RASTER) | set(ALLOWED_ICON)
        if self.allow_svg:
            allowed |= ALLOWED_VECTOR
        return allowed

    def __call__(self, file):
        name = getattr(file, "name", "") or ""
        ext = os.path.splitext(name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f"Unsupported file type '{ext or name}'. "
                f"Allowed: {', '.join(sorted(self.allowed_extensions))}."
            )
        size = getattr(file, "size", None)
        if size is not None and size > self.max_size:
            raise ValidationError(
                f"File too large ({size // 1024} KB). "
                f"Maximum allowed is {self.max_size // 1024} KB."
            )

        if ext in ALLOWED_VECTOR:
            self._validate_svg(file)
            return
        if ext == ".ico":
            # ICO validation is unreliable across Pillow builds; check the magic
            # bytes instead so we do not trust the extension alone.
            header = file.read(4)
            file.seek(0)
            if header[:4] not in (b"\x00\x00\x01\x00", b"\x00\x00\x02\x00"):
                raise ValidationError("This file is not a valid icon file.")
            return

        if Image is None:  # pragma: no cover - Pillow is a hard dependency
            return
        try:
            file.seek(0)
            with Image.open(file) as img:
                img.verify()
            file.seek(0)
            with Image.open(file) as img:
                width, height = img.size
                if width * height > MAX_IMAGE_PIXELS:
                    raise ValidationError("Image dimensions are unreasonably large.")
                if width < 1 or height < 1:
                    raise ValidationError("The uploaded image appears to be empty.")
        except ValidationError:
            raise
        except (UnidentifiedImageError, OSError, ValueError):
            raise ValidationError("This file is not a valid or readable image.")
        finally:
            file.seek(0)

    @staticmethod
    def _validate_svg(file):
        try:
            raw = file.read()
        finally:
            file.seek(0)
        if isinstance(raw, str):  # pragma: no cover
            raw = raw.encode("utf-8", "ignore")
        lowered = raw.lower()
        if b"<svg" not in lowered:
            raise ValidationError("This file is not a valid SVG image.")
        for dangerous in (b"<script", b"javascript:", b"onerror=", b"onload="):
            if dangerous in lowered:
                raise ValidationError("This SVG contains unsupported script content.")


@deconstructible
class VideoValidator:
    """Validate an uploaded file is really a video of an allowed type/size."""

    def __init__(self, max_size: int | None = None):
        self.max_size = max_size or getattr(settings, "MAX_UPLOAD_SIZE", 5 * 1024 * 1024)

    def __call__(self, file):
        name = getattr(file, "name", "") or ""
        ext = os.path.splitext(name)[1].lower()
        if ext not in ALLOWED_VIDEO:
            raise ValidationError(
                f"Unsupported file type '{ext or name}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_VIDEO))}."
            )
        size = getattr(file, "size", None)
        if size is not None and size > self.max_size:
            raise ValidationError(
                f"File too large ({size // 1024} KB). "
                f"Maximum allowed is {self.max_size // 1024} KB."
            )


def validate_image(value):
    ImageValidator()(value)


def validate_video(value):
    VideoValidator()(value)


def validate_logo(value):
    ImageValidator(allow_svg=True)(value)
