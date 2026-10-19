from __future__ import annotations

from django.shortcuts import get_object_or_404, render

from .models import ClassLevel, ClassTeacherAssignment


def class_list(request):
    classes = ClassLevel.objects.filter(is_published=True)
    return render(request, "classes/list.html", {"classes": classes})


def class_detail(request, slug):
    class_level = get_object_or_404(ClassLevel, slug=slug, is_published=True)
    assignments = (
        ClassTeacherAssignment.objects.select_related("teacher")
        .filter(class_level=class_level, teacher__is_active=True)
        .order_by("-is_lead", "display_order")
    )
    programmes = (
        class_level.programme_links.select_related("learning_area")
        .filter(learning_area__is_published=True)
        .order_by("display_order", "learning_area__display_order")
    )
    gallery_images = []
    if class_level.gallery_album_id:
        gallery_images = list(class_level.gallery_album.published_images[:12])
    related = (
        ClassLevel.objects.filter(is_published=True)
        .exclude(pk=class_level.pk)
        .order_by("display_order")
    )
    request.seo = {
        "title": f"{class_level.name} | Ebenezer Educational Centre",
        "description": class_level.short_introduction
        or (class_level.overview[:150] if class_level.overview else ""),
    }
    context = {
        "class_level": class_level,
        "assignments": assignments,
        "lead_teacher": class_level.lead_teacher,
        "programmes": programmes,
        "gallery_images": gallery_images,
        "related_classes": related,
    }
    return render(request, "classes/detail.html", context)
