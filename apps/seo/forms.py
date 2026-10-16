from __future__ import annotations

from django import forms

from .models import PageSEO, SEOSettings


def _style(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs["class"] = "form-check-input"
        elif isinstance(field.widget, forms.Select):
            field.widget.attrs["class"] = "form-select"
        else:
            field.widget.attrs["class"] = "form-control"


class SEOSettingsForm(forms.ModelForm):
    class Meta:
        model = SEOSettings
        fields = [
            "site_title",
            "default_meta_description",
            "canonical_base_url",
            "default_share_image",
            "allow_indexing",
            "enable_sitemap",
            "verification_google",
            "verification_bing",
        ]
        widgets = {
            "default_meta_description": forms.Textarea(attrs={"rows": 3}),
            "default_share_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)
        self.fields["allow_indexing"].help_text = (
            "Enable only after the site is live. Local development is never indexed."
        )


class PageSEOForm(forms.ModelForm):
    class Meta:
        model = PageSEO
        fields = [
            "title",
            "meta_description",
            "canonical_url",
            "og_title",
            "og_description",
            "og_image",
            "index",
            "follow",
        ]
        widgets = {
            "meta_description": forms.Textarea(attrs={"rows": 2, "maxlength": 320}),
            "og_description": forms.Textarea(attrs={"rows": 2, "maxlength": 320}),
            "og_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)
