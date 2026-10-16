from __future__ import annotations

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("analytics/", views.analytics, name="analytics"),

    # Appearance & branding
    path("appearance/", views.appearance, name="appearance"),
    path("appearance/reset/", views.appearance_reset, name="appearance_reset"),

    # Homepage slideshow
    path("slides/", views.slide_list, name="slide_list"),
    path("slides/add/", views.slide_create, name="slide_create"),
    path("slides/<int:pk>/edit/", views.slide_update, name="slide_update"),
    path("slides/<int:pk>/delete/", views.slide_delete, name="slide_delete"),
    path("slides/<int:pk>/toggle/", views.slide_toggle, name="slide_toggle"),

    # School benefits
    path("benefits/", views.benefit_list, name="benefit_list"),
    path("benefits/add/", views.benefit_create, name="benefit_create"),
    path("benefits/<int:pk>/edit/", views.benefit_update, name="benefit_update"),
    path("benefits/<int:pk>/delete/", views.benefit_delete, name="benefit_delete"),

    # Classes
    path("classes/", views.class_list, name="class_list"),
    path("classes/add/", views.class_create, name="class_create"),
    path("classes/<int:pk>/edit/", views.class_update, name="class_update"),
    path("classes/<int:pk>/delete/", views.class_delete, name="class_delete"),

    # Teachers
    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/add/", views.teacher_create, name="teacher_create"),
    path("teachers/<int:pk>/edit/", views.teacher_update, name="teacher_update"),
    path("teachers/<int:pk>/delete/", views.teacher_delete, name="teacher_delete"),

    # Programmes / learning areas
    path("programmes/", views.programme_list, name="programme_list"),
    path("programmes/add/", views.programme_create, name="programme_create"),
    path("programmes/<int:pk>/edit/", views.programme_update, name="programme_update"),
    path("programmes/<int:pk>/delete/", views.programme_delete, name="programme_delete"),

    # Gallery
    path("gallery/", views.album_list, name="album_list"),
    path("gallery/add/", views.album_create, name="album_create"),
    path("gallery/<int:pk>/edit/", views.album_update, name="album_update"),
    path("gallery/<int:pk>/delete/", views.album_delete, name="album_delete"),
    path("gallery/<int:pk>/publish/", views.album_toggle_publish, name="album_toggle_publish"),
    path("gallery/<int:album_pk>/images/", views.album_images, name="album_images"),
    path("gallery/<int:album_pk>/images/upload/", views.image_upload, name="image_upload"),
    path("gallery/images/<int:pk>/edit/", views.image_update, name="image_update"),
    path("gallery/images/<int:pk>/delete/", views.image_delete, name="image_delete"),
    path("gallery/images/<int:pk>/move/<str:direction>/", views.image_move, name="image_move"),
    path("gallery/heroes/<str:key>/edit/", views.page_hero_edit, name="page_hero_edit"),

    # School information
    path("school/", views.school_info, name="school_info"),
    path("footer/", views.footer_settings, name="footer_settings"),

    # SEO
    path("seo/", views.seo_settings, name="seo_settings"),
    path("seo/pages/<str:key>/", views.seo_page, name="seo_page"),

    # Users & permissions
    path("users/", views.user_list, name="user_list"),
    path("users/add/", views.user_create, name="user_create"),
    path("users/<int:pk>/edit/", views.user_update, name="user_update"),
    path("users/<int:pk>/toggle/", views.user_toggle, name="user_toggle"),

    # Notifications & system
    path("notifications/", views.notification_settings, name="notification_settings"),
    path("system/", views.system_settings, name="system_settings"),
    path("system/audit/", views.audit_log, name="audit_log"),
    path("system/analytics/purge/", views.analytics_purge, name="analytics_purge"),

    # Admission enquiries
    path("admissions/", views.admission_list, name="admission_list"),
    path("admissions/export/", views.admission_export, name="admission_export"),
    path("admissions/<int:pk>/", views.admission_detail, name="admission_detail"),
    path("admissions/<int:pk>/status/", views.admission_status, name="admission_status"),
    path("admissions/<int:pk>/reply/", views.admission_reply, name="admission_reply"),

    # Contact messages
    path("messages/", views.message_list, name="message_list"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
    path("messages/<int:pk>/reply/", views.message_reply, name="message_reply"),
]
