from __future__ import annotations

from django.urls import path, reverse_lazy

from .views import (
    StaffLoginView,
    StaffLogoutView,
    CustomPasswordResetView,
    CustomPasswordSetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetCompleteView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", StaffLoginView.as_view(), name="login"),
    path("logout/", StaffLogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/set/",
        CustomPasswordSetView.as_view(),
        name="password_reset_set",
    ),
    path(
        "password-reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/done/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
