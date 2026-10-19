from __future__ import annotations

from itertools import islice

from django.shortcuts import render

from apps.academics.models import ClassLevel, Teacher
from apps.gallery.models import GalleryAlbum
from apps.school.models import HeroSlide, SchoolBenefit


def _chunked(lst, n):
    it = iter(lst)
    while True:
        chunk = list(islice(it, n))
        if not chunk:
            break
        yield chunk


def home(request):
    slides = list(HeroSlide.objects.filter(is_active=True))
    teachers_qs = list(Teacher.objects.filter(is_active=True, is_featured=True)[:12])
    context = {
        "slides": slides,
        "benefits": SchoolBenefit.objects.filter(is_published=True)[:6],
        "classes": ClassLevel.objects.filter(is_published=True).order_by("display_order", "name"),
        "teachers": teachers_qs,
        "teacher_chunks": list(_chunked(teachers_qs, 2)),
        "albums": GalleryAlbum.objects.filter(is_published=True)[:3],
    }
    return render(request, "public/home.html", context)


def about(request):
    context = {
        "classes": ClassLevel.objects.filter(is_published=True),
        "teachers": Teacher.objects.filter(is_active=True),
    }
    return render(request, "public/about.html", context)


def privacy(request):
    return render(request, "public/privacy.html")


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)
