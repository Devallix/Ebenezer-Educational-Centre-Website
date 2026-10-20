from __future__ import annotations

from django import forms

from .models import ClassLevel, ClassProgramme, LearningArea


def _style_fields(form, select_class="form-select"):
    for name, field in form.fields.items():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs["class"] = "form-check-input"
        elif isinstance(widget, forms.SelectMultiple):
            widget.attrs["class"] = "form-select"
        elif isinstance(widget, forms.Select):
            widget.attrs["class"] = select_class
        else:
            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = (existing + " form-control").strip()


class ClassLevelForm(forms.ModelForm):
    class Meta:
        model = ClassLevel
        fields = [
            "name",
            "short_introduction",
            "image",
            "image_alt",
            "display_order",
            "is_published",
        ]
        widgets = {
            "short_introduction": forms.Textarea(attrs={"rows": 2}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class LearningAreaForm(forms.ModelForm):
    classes = forms.ModelMultipleChoiceField(
        queryset=ClassLevel.objects.all().order_by("display_order", "name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 8}),
        help_text="Select the classes that offer this programme.",
    )

    class Meta:
        model = LearningArea
        fields = [
            "name",
            "description",
            "icon",
            "image",
            "objectives",
            "example_activities",
            "classes",
            "display_order",
            "is_published",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "objectives": forms.Textarea(attrs={"rows": 4}),
            "example_activities": forms.Textarea(attrs={"rows": 4}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)
        self.fields["objectives"].help_text = "One learning objective per line."
        self.fields["example_activities"].help_text = "One example activity per line."
        if self.instance and self.instance.pk:
            self.fields["classes"].initial = ClassLevel.objects.filter(
                programme_links__learning_area=self.instance
            )

    def save(self, commit=True):
        area = super().save(commit=commit)
        if commit:
            self._sync_classes(area)
        return area

    def _sync_classes(self, area):
        classes = self.cleaned_data.get("classes") or []
        selected_ids = {c.pk for c in classes}
        ClassProgramme.objects.filter(learning_area=area).exclude(
            class_level_id__in=selected_ids
        ).delete()
        for order, class_level in enumerate(
            sorted(classes, key=lambda c: (c.display_order, c.name))
        ):
            ClassProgramme.objects.update_or_create(
                learning_area=area,
                class_level=class_level,
                defaults={"display_order": order},
            )
