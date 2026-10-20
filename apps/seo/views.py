from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse
from django.template import loader

from .models import SEOSettings


def robots_txt(request):
    cfg = SEOSettings.get_solo()
    lines = []
    if settings.DEBUG or not cfg.allow_indexing:
        lines.append("User-agent: *")
        lines.append("Disallow: /")
    else:
        lines.append("User-agent: *")
        lines.append("Disallow: /dashboard/")
        lines.append("Disallow: /accounts/")
        lines.append("Disallow: /admin/")
        lines.append("Disallow: /contact/")
        if cfg.enable_sitemap:
            lines.append("")
            lines.append(f"Sitemap: {cfg.canonical_base()}/sitemap.xml")
    content = "\n".join(lines).strip() + "\n"
    return HttpResponse(content, content_type="text/plain")
