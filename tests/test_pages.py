from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.academics.models import ClassLevel, LearningArea, Teacher
from apps.admissions.models import AdmissionEnquiry, ContactMessage
from apps.gallery.models import GalleryAlbum, GalleryImage
from apps.school.models import HeroSlide, PAGE_HERO_DEFAULTS, PageHero

User = get_user_model()


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school_class = ClassLevel.objects.create(name="Nursery 1", is_published=True)
        cls.area = LearningArea.objects.create(name="Literacy", is_published=True)

    def test_public_pages_render(self):
        urls = [
            reverse("core:home"),
            reverse("core:about"),
            reverse("core:privacy"),
            reverse("academics:class_list"),
            reverse("academics:class_detail", args=[self.school_class.slug]),
            reverse("gallery:album_list"),
            reverse("admissions:contact"),
            reverse("admissions:admission"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_robots_and_sitemap(self):
        self.assertEqual(self.client.get("/robots.txt").status_code, 200)
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)

    def test_unknown_page_returns_404(self):
        self.assertEqual(self.client.get("/does-not-exist-xyz/").status_code, 404)


class AuthFlowTests(TestCase):
    def test_login_page_renders(self):
        self.assertEqual(self.client.get(reverse("accounts:login")).status_code, 200)

    def test_password_reset_pages_render(self):
        self.assertEqual(self.client.get(reverse("accounts:password_reset")).status_code, 200)
        self.assertEqual(self.client.get(reverse("accounts:password_reset_done")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("accounts:password_reset_complete")).status_code, 200
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard:overview"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)


class DashboardPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username="smokeadmin", email="smoke@example.com", password="pass12345!"
        )
        cls.school_class = ClassLevel.objects.create(name="KG 1", is_published=True)
        cls.teacher = Teacher.objects.create(full_name="Ama Teacher")
        cls.area = LearningArea.objects.create(name="Numeracy", is_published=True)
        cls.slide = HeroSlide.objects.create(title="Welcome")
        cls.album = GalleryAlbum.objects.create(title="Opening Day")
        cls.image = GalleryImage.objects.create(
            album=cls.album, image="gallery/opening.jpg", caption="Arrival"
        )
        cls.enquiry = AdmissionEnquiry.objects.create(
            parent_name="Kofi Mensah", child_first_name="Esi", phone="0240000000"
        )
        cls.message = ContactMessage.objects.create(
            name="Yaw", email="yaw@example.com", subject="Hello", message="Hi there"
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_all_dashboard_pages_render(self):
        urls = [
            reverse("dashboard:overview"),
            reverse("dashboard:analytics"),
            reverse("dashboard:appearance"),
            reverse("dashboard:slide_list"),
            reverse("dashboard:slide_create"),
            reverse("dashboard:slide_update", args=[self.slide.pk]),
            reverse("dashboard:slide_delete", args=[self.slide.pk]),
            reverse("dashboard:benefit_list"),
            reverse("dashboard:benefit_create"),
            reverse("dashboard:class_list"),
            reverse("dashboard:class_create"),
            reverse("dashboard:class_update", args=[self.school_class.pk]),
            reverse("dashboard:teacher_list"),
            reverse("dashboard:teacher_create"),
            reverse("dashboard:teacher_update", args=[self.teacher.pk]),
            reverse("dashboard:album_list"),
            reverse("dashboard:album_create"),
            reverse("dashboard:album_update", args=[self.album.pk]),
            reverse("dashboard:album_images", args=[self.album.pk]),
            reverse("dashboard:image_update", args=[self.image.pk]),
            reverse("dashboard:school_info"),
            reverse("dashboard:footer_settings"),
            reverse("dashboard:seo_settings"),
            reverse("dashboard:seo_page", args=["home"]),
            reverse("dashboard:user_list"),
            reverse("dashboard:user_create"),
            reverse("dashboard:user_update", args=[self.admin.pk]),
            reverse("dashboard:notification_settings"),
            reverse("dashboard:system_settings"),
            reverse("dashboard:audit_log"),
            reverse("dashboard:admission_list"),
            reverse("dashboard:admission_detail", args=[self.enquiry.pk]),
            reverse("dashboard:message_list"),
            reverse("dashboard:message_detail", args=[self.message.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_admission_export_csv(self):
        response = self.client.get(reverse("dashboard:admission_export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")


class PageHeroTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username="heroadmin", email="hero@example.com", password="pass12345!"
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_gallery_page_lists_page_heroes_and_seeds_them(self):
        response = self.client.get(reverse("dashboard:album_list"))
        self.assertContains(response, "Page heroes")
        self.assertEqual(PageHero.objects.count(), len(PAGE_HERO_DEFAULTS))

    def test_edit_page_hero_updates_public_page(self):
        response = self.client.post(
            reverse("dashboard:page_hero_edit", args=["about"]),
            {
                "label": "About",
                "title": "Our Story",
                "subtitle": "How we began.",
                "is_active": "on",
            },
        )
        self.assertRedirects(response, reverse("dashboard:album_list"))
        page = self.client.get(reverse("core:about"))
        self.assertContains(page, "Our Story")
        self.assertContains(page, "How we began.")

    def test_page_hero_edit_get_redirects_to_gallery(self):
        response = self.client.get(reverse("dashboard:page_hero_edit", args=["classes"]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("edit=classes", response.url)

    def test_unknown_page_hero_key_is_rejected(self):
        response = self.client.get(reverse("dashboard:page_hero_edit", args=["nope"]))
        self.assertRedirects(response, reverse("dashboard:album_list"))


class SeedPageHeroesCommandTests(TestCase):
    def test_command_is_idempotent_and_preserves_edits(self):
        call_command("seed_page_heroes")
        self.assertEqual(PageHero.objects.count(), len(PAGE_HERO_DEFAULTS))

        hero = PageHero.objects.get(key="about")
        hero.title = "Edited Heading"
        hero.save()

        call_command("seed_page_heroes")
        hero.refresh_from_db()
        self.assertEqual(hero.title, "Edited Heading")
        self.assertEqual(PageHero.objects.count(), len(PAGE_HERO_DEFAULTS))

    def test_force_resets_to_defaults(self):
        call_command("seed_page_heroes")
        hero = PageHero.objects.get(key="about")
        hero.title = "Edited Heading"
        hero.save()

        call_command("seed_page_heroes", "--force")
        hero.refresh_from_db()
        self.assertEqual(hero.title, PAGE_HERO_DEFAULTS["about"]["title"])
