"""Seed editable page-hero banners (safe, idempotent).

Creates a PageHero row for every public page that does not already have one.
Existing rows are never overwritten by default, so admin edits are preserved.
Use --force to reset them back to the built-in defaults.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.school.models import PAGE_HERO_DEFAULTS, PageHero


class Command(BaseCommand):
    help = "Seed editable page heroes for every public page (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing page heroes with the built-in defaults.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options["force"]
        created = 0
        updated = 0
        for key, defaults in PAGE_HERO_DEFAULTS.items():
            defaults = {**defaults, "is_active": True}
            if force:
                hero, was_created = PageHero.objects.update_or_create(
                    key=key, defaults=defaults
                )
            else:
                hero, was_created = PageHero.objects.get_or_create(
                    key=key, defaults=defaults
                )
            if was_created:
                created += 1
            elif force:
                updated += 1

        self.stdout.write(self.style.SUCCESS("Page heroes seeded."))
        self.stdout.write(f"Created: {created}; reset: {updated}.")
