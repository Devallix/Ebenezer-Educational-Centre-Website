from __future__ import annotations

from django.contrib import admin

from .models import PageSEO, SEOSettings


@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_title", "allow_indexing", "enable_sitemap", "updated_at")


@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "index", "follow", "updated_at")
