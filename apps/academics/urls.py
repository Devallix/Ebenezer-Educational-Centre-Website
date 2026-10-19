from __future__ import annotations

from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    path("classes/", views.class_list, name="class_list"),
    path("classes/<slug:slug>/", views.class_detail, name="class_detail"),
]
