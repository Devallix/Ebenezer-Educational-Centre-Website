from __future__ import annotations

from django import forms

from .models import ClassLevel, ClassProgramme, ClassTeacherAssignment, LearningArea, Teacher


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
            "overview",
            "age_range",
            "show_age_range",
            "developmental_focus",
            "image",
            "hero_image",
            "group_photo",
            "group_photo_alt",
            "gallery_album",
            "display_order",
            "is_published",
        ]
        widgets = {
            "short_introduction": forms.Textarea(attrs={"rows": 2}),
            "overview": forms.Textarea(attrs={"rows": 5}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "hero_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "group_photo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)
        self.fields["gallery_album"].empty_label = "None"


class TeacherForm(forms.ModelForm):
    classes = forms.ModelMultipleChoiceField(
        queryset=ClassLevel.objects.all().order_by("display_order", "name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 8}),
        help_text="Select the classes this teacher works with.",
    )
    lead_class = forms.ModelChoiceField(
        queryset=ClassLevel.objects.all().order_by("display_order", "name"),
        required=False,
        empty_label="Not a lead teacher",
        help_text="Mark this teacher as the lead teacher for one class.",
    )

    class Meta:
        model = Teacher
        fields = [
            "full_name",
            "role",
            "biography",
            "photo",
            "qualifications",
            "email",
            "display_order",
            "is_active",
            "is_featured",
        ]
        widgets = {
            "biography": forms.Textarea(attrs={"rows": 5}),
            "photo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)
        if self.instance and self.instance.pk:
            self.fields["classes"].initial = ClassLevel.objects.filter(
                teacher_assignments__teacher=self.instance
            )
            lead = (
                self.instance.class_assignments.filter(is_lead=True)
                .values_list("class_level_id", flat=True)
                .first()
            )
            self.fields["lead_class"].initial = lead

    def clean(self):
        cleaned = super().clean()
        lead = cleaned.get("lead_class")
        classes = cleaned.get("classes")
        if lead and classes is not None and lead not in classes:
            cleaned["classes"] = list(classes) + [lead]
        return cleaned

    def save(self, commit=True):
        teacher = super().save(commit=commit)
        if commit:
            self._sync_assignments(teacher)
        return teacher

    def _sync_assignments(self, teacher):
        classes = self.cleaned_data.get("classes") or []
        lead = self.cleaned_data.get("lead_class")
        selected_ids = {c.pk for c in classes}
        if lead:
            selected_ids.add(lead.pk)
        ClassTeacherAssignment.objects.filter(teacher=teacher).exclude(
            class_level_id__in=selected_ids
        ).delete()
        for order, class_level in enumerate(
            sorted(classes, key=lambda c: (c.display_order, c.name))
        ):
            ClassTeacherAssignment.objects.update_or_create(
                teacher=teacher,
                class_level=class_level,
                defaults={"is_lead": bool(lead and lead.pk == class_level.pk), "display_order": order},
            )
        if lead and lead.pk not in {c.pk for c in classes}:
            ClassTeacherAssignment.objects.update_or_create(
                teacher=teacher,
                class_level=lead,
                defaults={"is_lead": True, "display_order": 999},
            )


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
