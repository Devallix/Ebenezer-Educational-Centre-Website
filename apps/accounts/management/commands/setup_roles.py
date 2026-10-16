"""Create the standard dashboard roles/groups (idempotent)."""
from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from apps.accounts.permissions import ROLE_GROUPS


class Command(BaseCommand):
    help = "Create the dashboard role groups used for permissions."

    def handle(self, *args, **options):
        for code, name in ROLE_GROUPS.items():
            group, created = Group.objects.get_or_create(name=name)
            action = "Created" if created else "Exists"
            self.stdout.write(f"{action}: {name}")
        self.stdout.write(self.style.SUCCESS("Roles ready."))
