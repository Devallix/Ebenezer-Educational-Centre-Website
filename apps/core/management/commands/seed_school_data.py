"""Idempotently seed the initial school content.

Safe to run repeatedly: existing rows are looked up by a stable key and only
missing rows are created. It never creates duplicate classes.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.academics.models import ClassLevel, LearningArea
from apps.core.models import (
    NotificationSettings,
    SchoolSettings,
    ThemeSettings,
)
from apps.school.models import PAGE_HERO_DEFAULTS, PageHero, SchoolBenefit
from apps.seo.models import PageSEO, SEOSettings

CLASSES = [
    ("Creche", "A warm, caring first step away from home for our youngest learners, with plenty of cuddles, play and gentle routine.", "Care, comfort and early stimulation through play."),
    ("Nursery 1", "A playful introduction to group learning, where children build confidence, language and friendships.", "Language, listening and social confidence."),
    ("Nursery 2", "Building on early exploration with songs, stories, sensory play and the first steps towards structured learning.", "Early language, number and sensory discovery."),
    ("Kindergarten 1", "A lively year of stories, songs, letters, numbers and hands-on discovery that builds school readiness.", "Foundational literacy, numeracy and creativity."),
    ("Kindergarten 2", "Consolidating early reading, writing and number skills while nurturing curiosity and independence.", "School readiness for Primary 1."),
    ("Primary 1", "A confident start to primary education with structured literacy, numeracy and creative subjects.", "Reading, writing and early mathematics."),
    ("Primary 2", "Growing independence across the curriculum with deeper reading, writing and problem-solving.", "Fluent literacy and mathematical thinking."),
    ("Primary 3", "Strengthening core academic skills and encouraging curiosity, teamwork and responsibility.", "Independent learning and critical thinking."),
]

LEARNING_AREAS = [
    ("Language and Literacy", "bi-book", "Listening, speaking, early reading and writing, storytelling and vocabulary development."),
    ("Mathematics and Numeracy", "bi-calculator", "Number recognition, counting, shapes, patterns, measurement and early problem solving."),
    ("Environmental Awareness and Introductory Science", "bi-globe2", "Exploring nature, the local environment, weather, plants, animals and simple science."),
    ("Creative Arts", "bi-palette", "Drawing, painting, modelling, craft and imaginative expression."),
    ("Music and Movement", "bi-music-note-beamed", "Songs, rhythm, dance and movement that build coordination and joy in learning."),
    ("Physical Development", "bi-bicycle", "Gross and fine motor skills through active indoor and outdoor play."),
    ("Personal and Social Development", "bi-people", "Sharing, turn-taking, kindness, independence and confidence."),
    ("Communication and Early Problem-Solving", "bi-chat-dots", "Expressing ideas, asking questions and thinking through simple challenges."),
    ("Practical Activities and Exploration", "bi-hand-index-thumb", "Hands-on discovery, sensory play and everyday practical experiences."),
]

BENEFITS = [
    ("Caring and Attentive Teaching", "bi-heart", "Our teachers know every child by name and give each learner the attention they need to thrive."),
    ("Age-Appropriate Learning", "bi-stars", "Activities and expectations are matched carefully to each child's stage of development."),
    ("Foundational Literacy and Numeracy", "bi-book-half", "Children build strong early reading, writing and number skills step by step."),
    ("Creativity and Exploration", "bi-palette", "Art, music, movement and play spark imagination and a love of discovery."),
    ("Positive Social Development", "bi-people", "Children learn to share, cooperate, respect others and grow in confidence."),
    ("A Supportive Learning Environment", "bi-shield-check", "A warm, welcoming and well-supervised setting where children feel safe to learn."),
]


class Command(BaseCommand):
    help = "Seed the initial classes, programmes, benefits and settings (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        created_classes = 0
        for order, (name, intro, focus) in enumerate(CLASSES, start=1):
            _obj, created = ClassLevel.objects.update_or_create(
                name=name,
                defaults={
                    "short_introduction": intro,
                    "developmental_focus": focus,
                    "display_order": order,
                },
            )
            if created:
                created_classes += 1

        created_areas = 0
        for order, (name, icon, description) in enumerate(LEARNING_AREAS, start=1):
            _obj, created = LearningArea.objects.update_or_create(
                name=name,
                defaults={"icon": icon, "description": description, "display_order": order},
            )
            if created:
                created_areas += 1

        created_benefits = 0
        for order, (title, icon, description) in enumerate(BENEFITS, start=1):
            _obj, created = SchoolBenefit.objects.update_or_create(
                title=title,
                defaults={"icon": icon, "description": description, "display_order": order},
            )
            if created:
                created_benefits += 1

        # Singletons
        SchoolSettings.get_solo()
        ThemeSettings.get_solo()
        NotificationSettings.get_solo()
        SEOSettings.get_solo()
        for key, _label in PageSEO.KEY_CHOICES:
            PageSEO.objects.get_or_create(key=key)

        created_heroes = 0
        for key, defaults in PAGE_HERO_DEFAULTS.items():
            _obj, created = PageHero.objects.get_or_create(key=key, defaults=defaults)
            if created:
                created_heroes += 1

        self.stdout.write(self.style.SUCCESS("Initial content seeded."))
        self.stdout.write(
            f"Classes created: {created_classes}; learning areas: {created_areas}; "
            f"benefits: {created_benefits}; page heroes: {created_heroes}."
        )
