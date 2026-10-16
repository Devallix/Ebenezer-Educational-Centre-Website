from __future__ import annotations

from django.contrib import admin

from .models import HeroSlide, PageHero, SchoolBenefit


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "display_order", "is_active")
    list_filter = ("is_active",)


@admin.register(PageHero)
class PageHeroAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "is_active")
    list_filter = ("is_active",)


@admin.register(SchoolBenefit)
class SchoolBenefitAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "display_order", "is_published")
    list_filter = ("is_published",)
