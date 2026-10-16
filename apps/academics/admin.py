from __future__ import annotations

from django.contrib import admin

from .models import ClassLevel, ClassProgramme, ClassTeacherAssignment, LearningArea, Teacher


class ClassTeacherAssignmentInline(admin.TabularInline):
    model = ClassTeacherAssignment
    extra = 0


class ClassProgrammeInline(admin.TabularInline):
    model = ClassProgramme
    extra = 0


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "is_published", "show_age_range")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ClassTeacherAssignmentInline, ClassProgrammeInline]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "is_active", "is_featured", "display_order")
    list_filter = ("is_active", "is_featured")


@admin.register(LearningArea)
class LearningAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "is_published")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("name",)}
