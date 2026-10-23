from __future__ import annotations

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.academics.forms import ClassLevelForm
from apps.academics.models import ClassLevel
from apps.accounts.forms import AdminUserForm
from apps.accounts.permissions import (
    ROLE_GROUPS,
    capability_required,
    get_user_roles,
    user_can,
)
from apps.admissions.models import ContactMessage
from apps.analytics.models import SiteAnalyticsEvent
from apps.analytics import reports
from apps.analytics.services import purge_all_events
from apps.core.forms import (
    FooterSettingsForm,
    NotificationSettingsForm,
    SchoolSettingsForm,
    ThemeSettingsForm,
)
from apps.core.models import (
    NotificationLog,
    NotificationSettings,
    SchoolSettings,
    ThemeSettings,
)
from apps.core.services import log_action
from apps.gallery.forms import GalleryAlbumForm, GalleryImageForm
from apps.gallery.models import GalleryAlbum, GalleryImage
from apps.school.forms import HeroSlideForm, PageHeroForm, SchoolBenefitForm
from apps.school.models import HeroSlide, PageHero, PAGE_HERO_DEFAULTS, SchoolBenefit
from apps.seo.forms import PageSEOForm, SEOSettingsForm
from apps.seo.models import PageSEO, SEOSettings

logger = logging.getLogger("apps.dashboard")
User = get_user_model()


def _page(request, queryset, per_page=15):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def _delete(request, obj, capability, label):
    if not user_can(request.user, capability):
        messages.error(request, "You do not have permission to delete this item.")
        return redirect("dashboard:overview")
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        log_action(request, "delete", description=f"Deleted {label}: {name}")
        messages.success(request, f"{label} deleted.")
        return None
    return obj


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
@capability_required("dashboard_access")
def overview(request):
    start, end, label, days = reports.parse_range(request)
    message_qs = ContactMessage.objects.all()
    context = {
        "page_title": "Dashboard",
        "active": "overview",
        "range_label": label,
        "total_views": reports.total_pageviews(start, end),
        "unique_visitors": reports.unique_visitors(start, end),
        "message_total": message_qs.count(),
        "message_new": message_qs.filter(is_read=False, is_archived=False).count(),
        "unread_messages": message_qs.filter(is_read=False, is_archived=False).count(),
        "classes_count": ClassLevel.objects.count(),
        "albums_count": GalleryAlbum.objects.count(),
        "recent_messages": message_qs.order_by("-created_at")[:6],
        "top_pages": reports.top_pages(start, end, limit=6),
        "recent_activity": request.user.audit_entries.select_related("user")[:8]
        if hasattr(request.user, "audit_entries")
        else [],
        "conversions": reports.conversion_counts(start, end),
    }
    from apps.core.models import AuditLog

    context["recent_activity"] = AuditLog.objects.select_related("user")[:8]
    return render(request, "dashboard/overview.html", context)


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
@capability_required("analytics_view")
def analytics(request):
    start, end, label, days = reports.parse_range(request)
    dates, counts = reports.views_by_day(start, end)
    context = {
        "page_title": "Analytics",
        "active": "analytics",
        "range_label": label,
        "range_key": request.GET.get("range", "30"),
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "total_views": reports.total_pageviews(start, end),
        "unique_visitors": reports.unique_visitors(start, end),
        "top_pages": reports.top_pages(start, end, limit=15),
        "section_totals": reports.section_totals(start, end),
        "conversions": reports.conversion_counts(start, end),
        "messages_in_range": ContactMessage.objects.filter(
            created_at__gte=start, created_at__lte=end
        ).count(),
        "chart_labels": json.dumps([d.strftime("%d %b") for d in dates]),
        "chart_values": json.dumps(counts),
        "device_labels": json.dumps([d[0] for d in reports.device_breakdown(start, end)]),
        "device_values": json.dumps([d[1] for d in reports.device_breakdown(start, end)]),
        "referrers": reports.referrer_sources(start, end),
        "has_data": reports.total_pageviews(start, end) > 0,
    }
    return render(request, "dashboard/analytics.html", context)


# ---------------------------------------------------------------------------
# Appearance
# ---------------------------------------------------------------------------
@capability_required("appearance_manage")
def appearance(request):
    theme = ThemeSettings.get_solo()
    if request.method == "POST":
        form = ThemeSettingsForm(request.POST, instance=theme)
        if form.is_valid():
            form.save()
            log_action(request, "update", theme, "Updated theme colours")
            messages.success(request, "Theme colours saved.")
            return redirect("dashboard:appearance")
        messages.error(request, "Please correct the colour values.")
    else:
        form = ThemeSettingsForm(instance=theme)
    return render(
        request,
        "dashboard/appearance.html",
        {"form": form, "page_title": "Website Appearance", "active": "appearance"},
    )


@capability_required("appearance_manage")
@require_POST
def appearance_reset(request):
    theme = ThemeSettings.get_solo()
    theme.reset_to_defaults()
    log_action(request, "update", theme, "Reset theme to defaults")
    messages.success(request, "Theme colours reset to the brand defaults.")
    return redirect("dashboard:appearance")


# ---------------------------------------------------------------------------
# Hero slideshow
# ---------------------------------------------------------------------------
@capability_required("content_manage")
def slide_list(request):
    slides = HeroSlide.objects.all()
    return render(
        request,
        "dashboard/slides/list.html",
        {"slides": slides, "page_title": "Homepage Slideshow", "active": "slides"},
    )


@capability_required("content_manage")
def slide_create(request):
    form = HeroSlideForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        slide = form.save()
        log_action(request, "create", slide, f"Created slide '{slide.title}'")
        messages.success(request, "Slide created.")
        return redirect("dashboard:slide_list")
    return render(
        request,
        "dashboard/slides/form.html",
        {"form": form, "page_title": "Add slide", "active": "slides"},
    )


@capability_required("content_manage")
def slide_update(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    form = HeroSlideForm(request.POST or None, request.FILES or None, instance=slide)
    if request.method == "POST" and form.is_valid():
        slide = form.save()
        log_action(request, "update", slide, f"Updated slide '{slide.title}'")
        messages.success(request, "Slide updated.")
        return redirect("dashboard:slide_list")
    return render(
        request,
        "dashboard/slides/form.html",
        {"form": form, "slide": slide, "page_title": "Edit slide", "active": "slides"},
    )


@capability_required("content_manage")
def slide_delete(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    result = _delete(request, slide, "content_manage", "Slide")
    if result is None:
        return redirect("dashboard:slide_list")
    return render(
        request,
        "dashboard/confirm_delete.html",
        {"object": slide, "cancel_url": reverse("dashboard:slide_list"),
         "page_title": "Delete slide", "active": "slides"},
    )


@capability_required("content_manage")
@require_POST
def slide_toggle(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    slide.is_active = not slide.is_active
    slide.save(update_fields=["is_active", "updated_at"])
    messages.success(request, f"Slide {'activated' if slide.is_active else 'deactivated'}.")
    return redirect("dashboard:slide_list")


# ---------------------------------------------------------------------------
# School benefits
# ---------------------------------------------------------------------------
@capability_required("content_manage")
def benefit_list(request):
    benefits = SchoolBenefit.objects.all()
    return render(
        request,
        "dashboard/benefits/list.html",
        {"benefits": benefits, "page_title": "School Benefits", "active": "benefits"},
    )


@capability_required("content_manage")
def benefit_create(request):
    form = SchoolBenefitForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        log_action(request, "create", obj, f"Created benefit '{obj.title}'")
        messages.success(request, "Benefit added.")
        return redirect("dashboard:benefit_list")
    return render(
        request,
        "dashboard/generic_form.html",
        {"form": form, "page_title": "Add benefit", "active": "benefits",
         "cancel_url": reverse("dashboard:benefit_list")},
    )


@capability_required("content_manage")
def benefit_update(request, pk):
    obj = get_object_or_404(SchoolBenefit, pk=pk)
    form = SchoolBenefitForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        log_action(request, "update", obj, f"Updated benefit '{obj.title}'")
        messages.success(request, "Benefit updated.")
        return redirect("dashboard:benefit_list")
    return render(
        request,
        "dashboard/generic_form.html",
        {"form": form, "page_title": "Edit benefit", "active": "benefits",
         "cancel_url": reverse("dashboard:benefit_list")},
    )


@capability_required("content_manage")
def benefit_delete(request, pk):
    obj = get_object_or_404(SchoolBenefit, pk=pk)
    result = _delete(request, obj, "content_manage", "Benefit")
    if result is None:
        return redirect("dashboard:benefit_list")
    return render(
        request,
        "dashboard/confirm_delete.html",
        {"object": obj, "cancel_url": reverse("dashboard:benefit_list"),
         "page_title": "Delete benefit", "active": "benefits"},
    )


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------
@capability_required("content_manage")
def class_list(request):
    classes = ClassLevel.objects.all().order_by("display_order", "name")
    return render(
        request,
        "dashboard/classes/list.html",
        {"classes": classes, "page_title": "Classes", "active": "classes"},
    )


@capability_required("content_manage")
def class_create(request):
    form = ClassLevelForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        log_action(request, "create", obj, f"Created class '{obj.name}'")
        messages.success(request, "Class created.")
        return redirect("dashboard:class_list")
    return render(
        request,
        "dashboard/classes/form.html",
        {"form": form, "page_title": "Add class", "active": "classes"},
    )


@capability_required("content_manage")
def class_update(request, pk):
    obj = get_object_or_404(ClassLevel, pk=pk)
    form = ClassLevelForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        log_action(request, "update", obj, f"Updated class '{obj.name}'")
        messages.success(request, "Class updated.")
        return redirect("dashboard:class_list")
    return render(
        request,
        "dashboard/classes/form.html",
        {"form": form, "class_level": obj, "page_title": "Edit class",
         "active": "classes"},
    )


@capability_required("content_manage")
def class_delete(request, pk):
    obj = get_object_or_404(ClassLevel, pk=pk)
    result = _delete(request, obj, "content_manage", "Class")
    if result is None:
        return redirect("dashboard:class_list")
    return render(
        request,
        "dashboard/confirm_delete.html",
        {"object": obj, "cancel_url": reverse("dashboard:class_list"),
         "page_title": "Delete class", "active": "classes"},
    )


# ---------------------------------------------------------------------------
# Gallery
# ---------------------------------------------------------------------------
@capability_required("content_manage")
def album_list(request):
    albums = GalleryAlbum.objects.all().annotate(num_images=Count("images"))
    for key, defaults in PAGE_HERO_DEFAULTS.items():
        PageHero.objects.get_or_create(key=key, defaults=defaults)
    page_heroes = PageHero.objects.all()
    edit_key = (request.GET.get("edit") or "").strip()
    hero_form = None
    editing_hero = None
    if edit_key in PAGE_HERO_DEFAULTS:
        editing_hero, _ = PageHero.objects.get_or_create(
            key=edit_key, defaults=PAGE_HERO_DEFAULTS[edit_key]
        )
        hero_form = PageHeroForm(instance=editing_hero)
    return render(
        request,
        "dashboard/gallery/list.html",
        {
            "albums": albums,
            "page_heroes": page_heroes,
            "hero_form": hero_form,
            "editing_hero": editing_hero,
            "page_title": "Gallery & Albums",
            "active": "gallery",
        },
    )


@capability_required("content_manage")
def page_hero_edit(request, key):
    if key not in PAGE_HERO_DEFAULTS:
        messages.error(request, "Unknown page hero.")
        return redirect("dashboard:album_list")
    hero, _ = PageHero.objects.get_or_create(
        key=key, defaults=PAGE_HERO_DEFAULTS[key]
    )
    if request.method == "POST":
        form = PageHeroForm(request.POST, request.FILES, instance=hero)
        if form.is_valid():
            form.save()
            log_action(request, "update", hero, f"Updated page hero '{hero.get_key_display()}'")
            messages.success(request, "Page hero updated.")
            return redirect("dashboard:album_list")
        messages.error(request, "Please correct the errors below.")
        albums = GalleryAlbum.objects.all().annotate(num_images=Count("images"))
        return render(
            request,
            "dashboard/gallery/list.html",
            {
                "albums": albums,
                "page_heroes": PageHero.objects.all(),
                "hero_form": form,
                "editing_hero": hero,
                "page_title": "Gallery & Albums",
                "active": "gallery",
            },
        )
    return redirect(f"{reverse('dashboard:album_list')}?edit={key}")


@capability_required("content_manage")
def album_create(request):
    form = GalleryAlbumForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        log_action(request, "create", obj, f"Created album '{obj.title}'")
        messages.success(request, "Album created. Add at least two images to publish it.")
        return redirect("dashboard:album_images", album_pk=obj.pk)
    return render(
        request,
        "dashboard/gallery/form.html",
        {"form": form, "page_title": "Add album", "active": "gallery"},
    )


@capability_required("content_manage")
def album_update(request, pk):
    obj = get_object_or_404(GalleryAlbum, pk=pk)
    form = GalleryAlbumForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        log_action(request, "update", obj, f"Updated album '{obj.title}'")
        messages.success(request, "Album updated.")
        return redirect("dashboard:album_list")
    return render(
        request,
        "dashboard/gallery/form.html",
        {"form": form, "album": obj, "page_title": "Edit album", "active": "gallery"},
    )


@capability_required("content_manage")
def album_delete(request, pk):
    obj = get_object_or_404(GalleryAlbum, pk=pk)
    result = _delete(request, obj, "content_manage", "Album")
    if result is None:
        return redirect("dashboard:album_list")
    return render(
        request,
        "dashboard/confirm_delete.html",
        {"object": obj, "cancel_url": reverse("dashboard:album_list"),
         "page_title": "Delete album", "active": "gallery"},
    )


@capability_required("content_manage")
@require_POST
def album_toggle_publish(request, pk):
    obj = get_object_or_404(GalleryAlbum, pk=pk)
    if not obj.is_published and not obj.can_publish:
        messages.error(request, "Add at least two images before publishing this album.")
    else:
        obj.is_published = not obj.is_published
        obj.save(update_fields=["is_published", "updated_at"])
        log_action(request, "update", obj, f"Album '{obj.title}' published={obj.is_published}")
        messages.success(
            request, f"Album {'published' if obj.is_published else 'unpublished'}."
        )
    return redirect("dashboard:album_list")


@capability_required("content_manage")
def album_images(request, album_pk):
    album = get_object_or_404(GalleryAlbum, pk=album_pk)
    images = album.images.all()
    return render(
        request,
        "dashboard/gallery/images.html",
        {"album": album, "images": images, "page_title": f"Images: {album.title}",
         "active": "gallery"},
    )


@capability_required("content_manage")
def image_upload(request, album_pk):
    album = get_object_or_404(GalleryAlbum, pk=album_pk)
    if request.method == "POST":
        image_files = request.FILES.getlist("images")
        video_files = request.FILES.getlist("videos")
        caption = request.POST.get("caption", "")
        is_published = request.POST.get("is_published") == "on"
        if not image_files and not video_files:
            messages.error(request, "Choose at least one image or video to upload.")
            return redirect("dashboard:album_images", album_pk=album.pk)
        from apps.core.validators import ImageValidator, VideoValidator
        from django.core.exceptions import ValidationError

        image_validator = ImageValidator()
        video_validator = VideoValidator()
        order = album.images.count()
        uploaded = 0
        errors = []
        for f in image_files:
            try:
                image_validator(f)
            except ValidationError as exc:
                errors.append(f"{f.name}: {' '.join(exc.messages)}")
                continue
            GalleryImage.objects.create(
                album=album,
                image=f,
                caption=caption,
                display_order=order,
                is_published=is_published,
            )
            order += 1
            uploaded += 1
        for f in video_files:
            try:
                video_validator(f)
            except ValidationError as exc:
                errors.append(f"{f.name}: {' '.join(exc.messages)}")
                continue
            GalleryImage.objects.create(
                album=album,
                video=f,
                caption=caption,
                display_order=order,
                is_published=is_published,
            )
            order += 1
            uploaded += 1
        if uploaded:
            log_action(request, "create", album, f"Uploaded {uploaded} item(s) to '{album.title}'")
            messages.success(request, f"{uploaded} item(s) uploaded.")
        for err in errors:
            messages.error(request, err)
    return redirect("dashboard:album_images", album_pk=album.pk)


@capability_required("content_manage")
def image_update(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    form = GalleryImageForm(request.POST or None, request.FILES or None, instance=image)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Image updated.")
        return redirect("dashboard:album_images", album_pk=image.album_id)
    return render(
        request,
        "dashboard/gallery/image_form.html",
        {"form": form, "image": image, "page_title": "Edit image", "active": "gallery"},
    )


@capability_required("content_manage")
def image_delete(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    album_pk = image.album_id
    result = _delete(request, image, "content_manage", "Image")
    if result is None:
        return redirect("dashboard:album_images", album_pk=album_pk)
    return render(
        request,
        "dashboard/confirm_delete.html",
        {"object": image, "cancel_url": reverse("dashboard:album_images", args=[album_pk]),
         "page_title": "Delete image", "active": "gallery"},
    )


@capability_required("content_manage")
@require_POST
def image_move(request, pk, direction):
    image = get_object_or_404(GalleryImage, pk=pk)
    siblings = list(image.album.images.order_by("display_order", "id"))
    index = siblings.index(image)
    swap_index = index - 1 if direction == "up" else index + 1
    if 0 <= swap_index < len(siblings):
        other = siblings[swap_index]
        image.display_order, other.display_order = other.display_order, image.display_order
        if image.display_order == other.display_order:
            image.display_order = swap_index
            other.display_order = index
        image.save(update_fields=["display_order"])
        other.save(update_fields=["display_order"])
    return redirect("dashboard:album_images", album_pk=image.album_id)


# ---------------------------------------------------------------------------
# School information & footer
# ---------------------------------------------------------------------------
@capability_required("settings_manage")
def school_info(request):
    obj = SchoolSettings.get_solo()
    form = SchoolSettingsForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", obj, "Updated school information")
        messages.success(request, "School information saved.")
        return redirect("dashboard:school_info")
    return render(
        request,
        "dashboard/school_info.html",
        {"form": form, "school": obj, "page_title": "School Information",
         "active": "school"},
    )


@capability_required("settings_manage")
def footer_settings(request):
    obj = SchoolSettings.get_solo()
    form = FooterSettingsForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", obj, "Updated footer & social media")
        messages.success(request, "Footer and social media settings saved.")
        return redirect("dashboard:footer_settings")
    return render(
        request,
        "dashboard/generic_form.html",
        {"form": form, "page_title": "Footer & Social Media", "active": "footer",
         "cancel_url": reverse("dashboard:overview"), "wide": True},
    )


# ---------------------------------------------------------------------------
# SEO
# ---------------------------------------------------------------------------
@capability_required("seo_manage")
def seo_settings(request):
    obj = SEOSettings.get_solo()
    form = SEOSettingsForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", obj, "Updated SEO settings")
        messages.success(request, "SEO settings saved.")
        return redirect("dashboard:seo_settings")
    pages = PageSEO.objects.all()
    return render(
        request,
        "dashboard/seo/settings.html",
        {"form": form, "pages": pages, "page_title": "SEO Settings",
         "active": "seo"},
    )


@capability_required("seo_manage")
def seo_page(request, key):
    page, _created = PageSEO.objects.get_or_create(key=key)
    form = PageSEOForm(request.POST or None, request.FILES or None, instance=page)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", page, f"Updated SEO for '{page.get_key_display()}'")
        messages.success(request, "Page SEO saved.")
        return redirect("dashboard:seo_settings")
    return render(
        request,
        "dashboard/seo/page_form.html",
        {"form": form, "page_seo": page, "page_title": f"SEO: {page.get_key_display()}",
         "active": "seo"},
    )


# ---------------------------------------------------------------------------
# Users & permissions
# ---------------------------------------------------------------------------
def _assign_role(user, role_code):
    user.groups.remove(*Group.objects.filter(name__in=ROLE_GROUPS.values()))
    if role_code and role_code in ROLE_GROUPS:
        group, _ = Group.objects.get_or_create(name=ROLE_GROUPS[role_code])
        user.groups.add(group)


@capability_required("users_manage")
def user_list(request):
    users = User.objects.all().prefetch_related("groups").order_by("-is_active", "username")
    rows = [
        {"user": u, "roles": get_user_roles(u)} for u in users
    ]
    return render(
        request,
        "dashboard/users/list.html",
        {"rows": rows, "page_title": "Users & Permissions", "active": "users"},
    )


@capability_required("users_manage")
def user_create(request):
    form = AdminUserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        _assign_role(user, form.cleaned_data.get("role"))
        log_action(request, "create", user, f"Created staff account '{user.username}'")
        messages.success(request, "Staff account created.")
        return redirect("dashboard:user_list")
    return render(
        request,
        "dashboard/users/form.html",
        {"form": form, "page_title": "Add user", "active": "users"},
    )


@capability_required("users_manage")
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = AdminUserForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        _assign_role(user, form.cleaned_data.get("role"))
        log_action(request, "update", user, f"Updated staff account '{user.username}'")
        messages.success(request, "Staff account updated.")
        return redirect("dashboard:user_list")
    return render(
        request,
        "dashboard/users/form.html",
        {"form": form, "staff": user, "page_title": "Edit user", "active": "users"},
    )


@capability_required("users_manage")
@require_POST
def user_toggle(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "You cannot disable your own account.")
        return redirect("dashboard:user_list")
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])
    log_action(request, "update", user, f"Set active={user.is_active} for '{user.username}'")
    messages.success(request, f"Account {'enabled' if user.is_active else 'disabled'}.")
    return redirect("dashboard:user_list")


# ---------------------------------------------------------------------------
# Notifications & system
# ---------------------------------------------------------------------------
@capability_required("notifications_manage")
def notification_settings(request):
    obj = NotificationSettings.get_solo()
    form = NotificationSettingsForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "update", obj, "Updated notification settings")
        messages.success(request, "Notification settings saved.")
        return redirect("dashboard:notification_settings")
    logs = NotificationLog.objects.all()[:10]
    return render(
        request,
        "dashboard/notifications.html",
        {"form": form, "logs": logs, "page_title": "Email & Notifications",
         "active": "notifications"},
    )


@capability_required("system_manage")
def system_settings(request):
    context = {
        "page_title": "System Settings",
        "active": "system",
        "analytics_count": SiteAnalyticsEvent.objects.count(),
        "audit_count": request.user.audit_entries.count() if hasattr(request.user, "audit_entries") else 0,
    }
    from apps.core.models import AuditLog

    context["audit_count"] = AuditLog.objects.count()
    return render(request, "dashboard/system.html", context)


@capability_required("system_manage")
def audit_log(request):
    logs = _page(request, request_logs := _audit_qs(), per_page=25)
    return render(
        request,
        "dashboard/audit_log.html",
        {"logs": logs, "page_title": "Audit Log", "active": "system"},
    )


def _audit_qs():
    from apps.core.models import AuditLog

    return AuditLog.objects.select_related("user").all()


@capability_required("system_manage")
@require_POST
def analytics_purge(request):
    deleted = purge_all_events()
    log_action(request, "other", description=f"Purged {deleted} analytics event(s) (full reset)")
    messages.success(request, f"Purged {deleted} analytics event(s). All analytics data has been reset.")
    return redirect("dashboard:system_settings")


# ---------------------------------------------------------------------------
# Contact messages
# ---------------------------------------------------------------------------
@capability_required("messages_manage")
def message_list(request):
    qs = ContactMessage.objects.all()
    query = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip()
    show = request.GET.get("show", "active")
    if query:
        qs = qs.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(subject__icontains=query)
        )
    if category in dict(ContactMessage.CATEGORY_CHOICES):
        qs = qs.filter(category=category)
    if show == "archived":
        qs = qs.filter(is_archived=True)
    else:
        qs = qs.filter(is_archived=False)
    page = _page(request, qs, per_page=20)
    return render(
        request,
        "dashboard/messages/list.html",
        {
            "page": page,
            "categories": ContactMessage.CATEGORY_CHOICES,
            "query": query,
            "current_category": category,
            "show": show,
            "page_title": "Contact Messages",
            "active": "messages",
        },
    )


@capability_required("messages_manage")
def message_detail(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "archive":
            message.is_archived = True
            message.save(update_fields=["is_archived", "updated_at"])
            messages.success(request, "Message archived.")
            return redirect("dashboard:message_list")
        if action == "restore":
            message.is_archived = False
            message.is_read = True
            message.save(update_fields=["is_archived", "is_read", "updated_at"])
            messages.success(request, "Message restored.")
            return redirect("dashboard:message_detail", pk=pk)
    if not message.is_read:
        message.is_read = True
        message.save(update_fields=["is_read", "updated_at"])
    return render(
        request,
        "dashboard/messages/detail.html",
        {"message": message, "page_title": f"Message: {message.subject}",
         "active": "messages"},
    )


@capability_required("messages_manage")
@require_POST
def message_reply(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    body = (request.POST.get("body") or "").strip()
    subject = (request.POST.get("subject") or f"Re: {message.subject}").strip()
    if not body:
        messages.error(request, "Please enter a reply message.")
        return redirect("dashboard:message_detail", pk=pk)
    notif = NotificationSettings.get_solo()
    from_email = f"{notif.sender_name or 'Ebenezer Educational Centre'} <{notif.sender_email}>" if notif.sender_email else settings.DEFAULT_FROM_EMAIL
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[message.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        email.send(fail_silently=False)
        message.is_read = True
        message.save(update_fields=["is_read", "updated_at"])
        log_action(request, "other", model_name="ContactMessage", description=f"Replied to message {message.pk}")
        messages.success(request, f"Reply sent to {message.email}.")
    except Exception as exc:
        logger.warning("Reply email failed: %s", exc)
        messages.error(request, f"Failed to send reply: {exc}")
    return redirect("dashboard:message_detail", pk=pk)
