from __future__ import annotations

from django.contrib import admin

from .models import ClassLevel, ClassProgramme, LearningArea


class ClassProgrammeInline(admin.TabularInline):
    model = ClassProgramme
    extra = 0


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "is_published", "show_age_range")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ClassProgrammeInline]


@admin.register(LearningArea)
class LearningAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "is_published")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("name",)}
