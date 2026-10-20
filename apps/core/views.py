from __future__ import annotations

from django.shortcuts import render

from apps.academics.models import ClassLevel
from apps.gallery.models import GalleryAlbum
from apps.school.models import HeroSlide


def home(request):
    slides = list(HeroSlide.objects.filter(is_active=True))
    context = {
        "slides": slides,
        "classes": ClassLevel.objects.filter(is_published=True).order_by("display_order", "name"),
        "albums": GalleryAlbum.objects.filter(is_published=True)[:3],
    }
    return render(request, "public/home.html", context)


def about(request):
    return render(request, "public/about.html")


def privacy(request):
    return render(request, "public/privacy.html")


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)
