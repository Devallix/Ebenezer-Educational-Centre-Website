from __future__ import annotations

from django.urls import path

from . import views

app_name = "admissions"

urlpatterns = [
    path("contact/", views.contact, name="contact"),
]
