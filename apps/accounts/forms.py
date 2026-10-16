from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.db.models import Q

from .permissions import ROLE_CHOICES, get_user_roles

User = get_user_model()


class StaffAuthenticationForm(AuthenticationForm):
    """Authenticate with a username OR an email address."""

    username = forms.CharField(
        label="Username or email",
        widget=forms.TextInput(
            attrs={"autofocus": True, "autocomplete": "username", "placeholder": "you@example.com", "class": "form-control"}
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "placeholder": "Your password", "class": "form-control"}
        ),
    )
    remember_me = forms.BooleanField(required=False, initial=False, label="Keep me signed in")

    def clean_username(self):
        return (self.cleaned_data.get("username") or "").strip()

    def clean(self):
        username = self.cleaned_data.get("username")
        if username and "@" in username:
            match = (
                User.objects.filter(Q(email__iexact=username) | Q(username__iexact=username))
                .order_by("id")
                .first()
            )
            if match is not None:
                self.cleaned_data["username"] = match.get_username()
                self.data = self.data.copy()
                self.data["username"] = match.get_username()
        return super().clean()


class StaffPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com"}),
    )


class StaffSetPasswordForm(SetPasswordForm):
    pass


class AdminUserForm(UserCreationForm):
    """Create or edit a staff account and assign a dashboard role."""

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        help_text="Controls which dashboard modules this user can access.",
    )
    is_active = forms.BooleanField(required=False, initial=True, label="Account active")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            roles = get_user_roles(self.instance)
            for code, _label in ROLE_CHOICES:
                if code in roles:
                    self.fields["role"].initial = code
            self.fields["is_active"].initial = self.instance.is_active
            # Password fields are optional when editing an existing user.
            for field_name in ("password1", "password2"):
                self.fields[field_name].required = False
                self.fields[field_name].help_text = (
                    "Leave blank to keep the current password."
                )
        self.fields["email"].required = True
        for name in self.fields:
            css = self.fields[name].widget.attrs.get("class", "")
            self.fields[name].widget.attrs["class"] = (css + " form-control").strip()
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"
        self.fields["role"].widget.attrs["class"] = "form-select"

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = self.cleaned_data.get("is_active", True)
        if commit:
            user.save()
        return user
