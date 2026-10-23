from __future__ import annotations

import json

from django.http import HttpResponse
from django.shortcuts import render

from apps.academics.models import ClassLevel
from apps.gallery.models import GalleryAlbum
from apps.school.models import HeroSlide


def home(request):
    slides = list(HeroSlide.objects.filter(is_active=True))
    classes = ClassLevel.objects.filter(is_published=True).order_by("display_order", "name")
    albums = GalleryAlbum.objects.filter(is_published=True)[:3]

    from apps.core.models import SchoolSettings

    school = SchoolSettings.get_solo()

    # JSON-LD structured data for AI agents and search engines.
    json_ld = {
        "@context": "https://schema.org",
        "@type": "EducationalOrganization",
        "name": school.school_name,
        "url": request.build_absolute_uri("/"),
        "telephone": school.phone_primary or "",
        "email": school.email_primary or "",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": school.address or "",
            "addressLocality": school.town or "",
            "addressRegion": school.region or "",
            "postalCode": "",
            "addressCountry": school.country or "GH",
        },
        "description": school.full_description or "",
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "07:00",
                "closes": "16:00",
            }
        ],
        "hasCourse": [
            {
                "@type": "Course",
                "name": cls.name,
                "description": cls.overview or cls.short_introduction or "",
                "educationalLevel": cls.published_age_range or "",
            }
            for cls in classes
        ],
    }

    context = {
        "slides": slides,
        "classes": classes,
        "albums": albums,
        "json_ld": json.dumps(json_ld),
    }
    return render(request, "public/home.html", context)


def about(request):
    return render(request, "public/about.html")


def llms_txt(request):
    """Machine-readable llms.txt for AI models and autonomous agents.

    Content is generated dynamically from the database so it stays in sync
    with the school's public settings and published class offerings.
    """
    from apps.core.models import SchoolSettings

    school = SchoolSettings.get_solo()
    classes = ClassLevel.objects.filter(is_published=True).order_by("display_order", "name")

    lines = []
    lines.append(f"# {school.school_name}")
    lines.append("")
    if school.full_description:
        lines.append(school.full_description)
    else:
        lines.append(
            f"A preschool and primary school in {school.full_address or 'Jukwa, Cape Coast, Ghana'}. "
            "We provide a safe, happy and stimulating environment where children are encouraged "
            "to explore, ask questions and grow in confidence."
        )
    lines.append("")

    lines.append("## Core Offerings")
    if classes:
        for cls in classes:
            age = cls.published_age_range or "all ages"
            focus = cls.developmental_focus or cls.short_introduction or ""
            lines.append(f"- {cls.name}: {focus} (ages: {age})")
    else:
        lines.append("- No published class offerings at this time.")
    lines.append("")

    lines.append("## Location & Contact")
    lines.append(f"- Physical Address: {school.full_address or 'Jukwa, Cape Coast, Central Region, Ghana'}")
    if school.phone_primary:
        lines.append(f"- Phone: {school.phone_primary}")
    if school.email_primary:
        lines.append(f"- Email: {school.email_primary}")
    if school.opening_hours:
        lines.append(f"- Operating Hours: {school.opening_hours}")
    lines.append("")
    lines.append("## Frequently Asked Questions")
    lines.append("- Do you offer online classes? No, all classes are in-person at our Jukwa, Cape Coast campus.")
    lines.append("- How do enrollments work? Use the Contact Us page to get in touch with our team about class availability and next steps.")
    lines.append("")
    lines.append(f"- Website: {request.build_absolute_uri('/')}")
    lines.append(f"- Contact page: {request.build_absolute_uri('/contact/')}")

    content = "\n".join(lines).strip() + "\n"
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)
