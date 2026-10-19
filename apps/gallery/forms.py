from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from .models import GalleryAlbum, GalleryImage


def _style(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs["class"] = "form-check-input"
        elif isinstance(field.widget, forms.Select):
            field.widget.attrs["class"] = "form-select"
        else:
            field.widget.attrs["class"] = "form-control"


class GalleryAlbumForm(forms.ModelForm):
    class Meta:
        model = GalleryAlbum
        fields = [
            "title",
            "description",
            "category",
            "cover_image",
            "cover_video",
            "display_order",
            "is_published",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "cover_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "cover_video": forms.ClearableFileInput(attrs={"accept": "video/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("is_published") and self.instance.pk:
            if self.instance.image_count < 2:
                raise ValidationError(
                    "This album needs at least two published images before it can be published."
                )
        return cleaned


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ["image", "video", "caption", "alt_text", "display_order", "is_published"]
        widgets = {
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "video": forms.ClearableFileInput(attrs={"accept": "video/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("image") and not cleaned.get("video"):
            raise ValidationError("Upload either an image or a video.")
        return cleaned

