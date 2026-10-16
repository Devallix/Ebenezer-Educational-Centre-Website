from __future__ import annotations

from django import forms

from apps.academics.models import ClassLevel

from .models import AdmissionEnquiry, ContactMessage

CONTROL_CLASS = "form-control"


class HoneypotMixin(forms.Form):
    """A hidden field that must remain empty; bots tend to fill it in."""

    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                "class": "hp-field",
                "aria-hidden": "true",
            }
        ),
    )

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Spam submission detected.")
        return value


class ContactForm(HoneypotMixin, forms.ModelForm):
    consent_given = forms.BooleanField(
        required=True,
        label="I agree that my details may be used to respond to this enquiry.",
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "category", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": CONTROL_CLASS, "autocomplete": "name"}),
            "email": forms.EmailInput(
                attrs={"class": CONTROL_CLASS, "autocomplete": "email"}
            ),
            "phone": forms.TextInput(
                attrs={"class": CONTROL_CLASS, "autocomplete": "tel"}
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.TextInput(attrs={"class": CONTROL_CLASS}),
            "message": forms.Textarea(attrs={"class": CONTROL_CLASS, "rows": 5}),
        }
        labels = {
            "name": "Your name",
            "message": "Message",
            "category": "What is this about?",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.Textarea)):
                field.widget.attrs.setdefault("class", CONTROL_CLASS)
        self.fields["consent_given"].widget.attrs["class"] = "form-check-input"

    def clean_email(self):
        return (self.cleaned_data.get("email") or "").strip().lower()

    def clean_message(self):
        message = (self.cleaned_data.get("message") or "").strip()
        if len(message) < 10:
            raise forms.ValidationError("Please provide a little more detail.")
        if len(message) > 4000:
            raise forms.ValidationError("Please keep your message under 4000 characters.")
        return message


class AdmissionEnquiryForm(HoneypotMixin, forms.ModelForm):
    consent_given = forms.BooleanField(
        required=True,
        label="I acknowledge that the information provided will be used to respond to this admission enquiry.",
    )

    class Meta:
        model = AdmissionEnquiry
        fields = [
            "parent_name",
            "phone",
            "email",
            "child_first_name",
            "preferred_class",
            "preferred_period",
            "message",
        ]
        widgets = {
            "parent_name": forms.TextInput(
                attrs={"class": CONTROL_CLASS, "autocomplete": "name"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": CONTROL_CLASS,
                    "autocomplete": "tel",
                    "placeholder": "e.g. 024 000 0000",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": CONTROL_CLASS, "autocomplete": "email"}
            ),
            "child_first_name": forms.TextInput(attrs={"class": CONTROL_CLASS}),
            "preferred_class": forms.Select(attrs={"class": "form-select"}),
            "preferred_period": forms.TextInput(
                attrs={"class": CONTROL_CLASS, "placeholder": "e.g. September 2026"}
            ),
            "message": forms.Textarea(
                attrs={"class": CONTROL_CLASS, "rows": 5, "placeholder": "Optional"}
            ),
        }
        labels = {
            "parent_name": "Parent / guardian full name",
            "child_first_name": "Child's first name",
            "preferred_class": "Preferred class",
            "preferred_period": "Preferred admission period",
            "message": "Questions or additional information",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_class"].queryset = ClassLevel.objects.filter(
            is_published=True
        ).order_by("display_order", "name")
        self.fields["preferred_class"].required = True
        self.fields["preferred_class"].empty_label = "Select a class"
        self.fields["email"].required = False
        self.fields["phone"].required = False
        self.fields["consent_given"].widget.attrs["class"] = "form-check-input"
        for name in ("phone", "email"):
            self.fields[name].help_text = "Provide at least a phone number or an email."
        if self.instance and self.instance.pk:
            self.fields["consent_given"].required = False

    def clean_email(self):
        return (self.cleaned_data.get("email") or "").strip().lower()

    def clean_message(self):
        return (self.cleaned_data.get("message") or "").strip()[:4000]

    def clean(self):
        cleaned = super().clean()
        if not (cleaned.get("phone") or "").strip() and not (
            cleaned.get("email") or ""
        ).strip():
            raise forms.ValidationError(
                "Please provide either a phone number or an email address so we can reply."
            )
        return cleaned
