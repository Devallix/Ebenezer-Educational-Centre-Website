from __future__ import annotations

from django import forms

from .models import ContactMessage

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
