from __future__ import annotations

from django.contrib import admin

from .models import GalleryAlbum, GalleryImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 0


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "display_order")
    list_filter = ("is_published", "category")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [GalleryImageInline]
