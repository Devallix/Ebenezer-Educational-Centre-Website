"""Create the initial super administrator securely.

Usage:
    python manage.py create_initial_admin --username admin --email you@example.com

The password may be supplied through the ADMIN_PASSWORD environment variable
(for automated setup) or entered interactively with confirmation. No default
password is ever baked in.
"""
from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.permissions import ROLE_GROUPS, ROLE_SUPER_ADMIN

User = get_user_model()


class Command(BaseCommand):
    help = "Create an initial super administrator account securely."

    def add_arguments(self, parser):
        parser.add_argument("--username", default=os.environ.get("ADMIN_USERNAME", ""))
        parser.add_argument("--email", default=os.environ.get("ADMIN_EMAIL", ""))
        parser.add_argument("--noinput", action="store_true")

    def handle(self, *args, **options):
        username = (options.get("username") or "").strip()
        email = (options.get("email") or "").strip()
        noinput = options.get("noinput")

        if not username and not noinput:
            username = input("Username: ").strip()
        if not email and not noinput:
            email = input("Email: ").strip()

        if not username:
            raise CommandError("A username is required.")
        if User.objects.filter(username__iexact=username).exists():
            raise CommandError(f"A user named '{username}' already exists.")

        password = os.environ.get("ADMIN_PASSWORD", "")
        if not password:
            if noinput:
                raise CommandError(
                    "ADMIN_PASSWORD must be set when using --noinput."
                )
            from django.core.management.utils import get_random_secret_key

            password = input("Password: ").strip()
            confirm = input("Confirm password: ").strip()
            if password != confirm:
                raise CommandError("Passwords did not match.")
        if len(password) < 8:
            raise CommandError("Choose a password of at least 8 characters.")

        user = User.objects.create_superuser(
            username=username, email=email or None, password=password
        )
        group, _ = Group.objects.get_or_create(name=ROLE_GROUPS[ROLE_SUPER_ADMIN])
        user.groups.add(group)
        self.stdout.write(self.style.SUCCESS(f"Super administrator '{username}' created."))
