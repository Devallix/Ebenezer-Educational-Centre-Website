from __future__ import annotations

from django import forms

from .models import HeroSlide, PageHero, SchoolBenefit


class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = [
            "label",
            "title",
            "subtitle",
            "image",
            "alt_text",
            "primary_button_label",
            "primary_button_url",
            "secondary_button_label",
            "secondary_button_url",
            "display_order",
            "is_active",
        ]
        widgets = {
            "subtitle": forms.Textarea(attrs={"rows": 3}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = (existing + " form-control").strip()
        self.fields["primary_button_url"].help_text = (
            "Relative path such as /contact/ or /#classes, or a full URL."
        )

    def clean_primary_button_url(self):
        return (self.cleaned_data.get("primary_button_url") or "").strip()

    def clean_secondary_button_url(self):
        return (self.cleaned_data.get("secondary_button_url") or "").strip()

    def clean(self):
        cleaned = super().clean()
        primary_label = cleaned.get("primary_button_label")
        if primary_label and not cleaned.get("primary_button_url"):
            cleaned["primary_button_url"] = "/contact/"
        return cleaned


class PageHeroForm(forms.ModelForm):
    class Meta:
        model = PageHero
        fields = ["label", "title", "subtitle", "image", "is_active"]
        widgets = {
            "subtitle": forms.Textarea(attrs={"rows": 3}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["label"].required = False
        self.fields["image"].help_text = "Optional background image for the banner."
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class SchoolBenefitForm(forms.ModelForm):
    class Meta:
        model = SchoolBenefit
        fields = ["title", "description", "icon", "display_order", "is_published"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
        self.fields["icon"].help_text = (
            "Bootstrap Icons class, e.g. bi-heart, bi-book, bi-stars."
        )
