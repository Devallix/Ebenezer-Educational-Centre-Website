from __future__ import annotations

from django.shortcuts import get_object_or_404, render

from .models import GalleryAlbum


def album_list(request):
    albums = GalleryAlbum.objects.filter(is_published=True)
    category = request.GET.get("category", "").strip()
    valid = {choice[0] for choice in GalleryAlbum.CATEGORY_CHOICES}
    if category in valid:
        albums = albums.filter(category=category)
    else:
        category = ""
    request.seo = {"title": "Photo Gallery | Ebenezer Educational Centre"}
    return render(
        request,
        "gallery/list.html",
        {
            "albums": albums,
            "categories": GalleryAlbum.CATEGORY_CHOICES,
            "active_category": category,
        },
    )


def album_detail(request, slug):
    album = get_object_or_404(GalleryAlbum, slug=slug, is_published=True)
    images = album.published_images
    request.seo = {
        "title": f"{album.title} | Gallery",
        "description": album.description[:150],
    }
    return render(
        request,
        "gallery/detail.html",
        {"album": album, "images": images},
    )
