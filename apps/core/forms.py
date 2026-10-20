from __future__ import annotations

import re

from django import forms
from django.utils.text import slugify

from .models import NotificationSettings, SchoolSettings, ThemeSettings

HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


class ColourInput(forms.TextInput):
    input_type = "color"

    def __init__(self, attrs=None):
        default = {"class": "form-control form-control-color", "type": "color"}
        if attrs:
            default.update(attrs)
        super().__init__(default)


class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model = SchoolSettings
        fields = [
            "school_name",
            "short_description",
            "tagline",
            "full_description",
            "address",
            "town",
            "region",
            "country",
            "phone_primary",
            "phone_secondary",
            "email_primary",
            "email_secondary",
            "opening_hours",
            "vision",
            "mission",
            "proprietress_name",
            "proprietress_title",
            "proprietress_message",
            "headmistress_image",
            "logo",
            "logo_light",
            "favicon",
            "home_welcome_image",
            "home_welcome_video",
            "about_story_image",
            "about_story_video",
            "map_url",
            "directions_url",
        ]
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 2}),
            "full_description": forms.Textarea(attrs={"rows": 4}),
            "vision": forms.Textarea(attrs={"rows": 3}),
            "mission": forms.Textarea(attrs={"rows": 3}),
            "proprietress_message": forms.Textarea(attrs={"rows": 5}),
            "home_welcome_video": forms.ClearableFileInput(attrs={"accept": "video/*"}),
            "about_story_video": forms.ClearableFileInput(attrs={"accept": "video/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs["class"] = (existing + " form-control").strip()
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs["class"] = (existing + " form-control").strip()
                if field.widget.attrs.get("accept") is None:
                    field.widget.attrs["accept"] = "image/*"
            else:
                field.widget.attrs["class"] = (existing + " form-control").strip()


class FooterSettingsForm(forms.ModelForm):
    class Meta:
        model = SchoolSettings
        fields = [
            "footer_intro",
            "footer_copyright",
            "facebook_url",
            "instagram_url",
            "twitter_url",
            "tiktok_url",
            "youtube_url",
            "linkedin_url",
            "whatsapp_number",
        ]
        widgets = {
            "footer_intro": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class ThemeSettingsForm(forms.ModelForm):
    COLOUR_FIELDS = [
        "primary_color",
        "secondary_color",
        "accent_color",
        "background_color",
        "surface_color",
        "text_color",
        "muted_color",
        "border_color",
        "sidebar_bg",
        "sidebar_text",
        "sidebar_active",
    ]

    class Meta:
        model = ThemeSettings
        fields = list(ThemeSettings.DEFAULTS.keys())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.COLOUR_FIELDS:
            self.fields[name].widget = ColourInput({"data-colour": "1"})
            self.fields[name].validators = []

    def clean(self):
        cleaned = super().clean()
        for name in self.COLOUR_FIELDS:
            value = cleaned.get(name)
            if value and not HEX_RE.match(value.strip()):
                self.add_error(
                    name, "Enter a valid hex colour such as #9E0719."
                )
            elif value:
                cleaned[name] = value.strip().upper()
        return cleaned


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = [
            "recipient_emails",
            "notify_contact",
            "sender_name",
            "sender_email",
            "contact_subject",
        ]
        widgets = {
            "recipient_emails": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "admin@example.com, head@example.com",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            if name == "sender_email":
                field.widget.attrs["placeholder"] = "notifications@yourschool.gh"

    def clean_recipient_emails(self):
        import re

        raw = self.cleaned_data.get("recipient_emails", "")
        addresses = [a.strip() for a in raw.replace(";", ",").split(",") if a.strip()]
        email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        invalid = [a for a in addresses if not email_re.match(a)]
        if invalid:
            raise forms.ValidationError(
                "These addresses look invalid: " + ", ".join(invalid)
            )
        return ", ".join(addresses)


def slugify_field(value: str) -> str:
    return slugify(value)
