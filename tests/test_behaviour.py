from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.academics.models import ClassLevel
from apps.admissions.models import ContactMessage
from apps.analytics.models import SiteAnalyticsEvent

User = get_user_model()


class ContactFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school_class = ClassLevel.objects.create(name="Primary 1", is_published=True)

    def test_valid_contact_submission_creates_message(self):
        response = self.client.post(
            reverse("admissions:contact"),
            {
                "name": "Akosua",
                "email": "akosua@example.com",
                "phone": "0244000000",
                "category": "general",
                "subject": "School hours",
                "message": "Please share your opening hours and term dates.",
                "consent_given": "on",
            },
        )
        self.assertIn(response.status_code, (200, 302))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_honeypot_blocks_bots(self):
        self.client.post(
            reverse("admissions:contact"),
            {
                "name": "Bot",
                "email": "bot@example.com",
                "category": "general",
                "subject": "spam",
                "message": "This is a spammy message that should be rejected.",
                "consent_given": "on",
                "website": "http://spam.example.com",
            },
        )
        self.assertEqual(ContactMessage.objects.count(), 0)


class AnalyticsTrackingTests(TestCase):
    def test_public_page_view_is_recorded(self):
        self.client.get(reverse("core:home"))
        self.assertTrue(
            SiteAnalyticsEvent.objects.filter(
                event_type=SiteAnalyticsEvent.EVENT_PAGEVIEW, path=reverse("core:home")
            ).exists()
        )

    def test_dashboard_views_are_not_recorded(self):
        admin = User.objects.create_superuser(
            username="analyticsadmin", email="a@example.com", password="pass12345!"
        )
        self.client.force_login(admin)
        before = SiteAnalyticsEvent.objects.count()
        self.client.get(reverse("dashboard:overview"))
        self.assertEqual(SiteAnalyticsEvent.objects.count(), before)


class RolePermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.editor_group = Group.objects.create(name="Content Editors")
        cls.editor = User.objects.create_user(
            username="editor", email="editor@example.com", password="pass12345!"
        )
        cls.editor.groups.add(cls.editor_group)

    def setUp(self):
        self.client.force_login(self.editor)

    def test_editor_can_access_content_pages(self):
        self.assertEqual(self.client.get(reverse("dashboard:class_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:slide_list")).status_code, 200)

    def test_editor_cannot_manage_users(self):
        self.assertEqual(self.client.get(reverse("dashboard:user_list")).status_code, 403)

    def test_editor_cannot_manage_system(self):
        self.assertEqual(self.client.get(reverse("dashboard:system_settings")).status_code, 403)
