from __future__ import annotations

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.gallery.models import GalleryAlbum

from .models import SEOSettings


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["core:home", "core:about",
                "gallery:album_list", "admissions:contact", "admissions:admission"]

    def location(self, item):
        return reverse(item)


class GalleryAlbumSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return GalleryAlbum.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "static": StaticViewSitemap,
    "albums": GalleryAlbumSitemap,
}
