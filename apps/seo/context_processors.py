from __future__ import annotations

from django.conf import settings

from .models import PageSEO, SEOSettings

URL_NAME_MAP = {
    "core:home": PageSEO.KEY_HOME,
    "core:about": PageSEO.KEY_ABOUT,
    "gallery:album_list": PageSEO.KEY_GALLERY,
    "admissions:contact": PageSEO.KEY_CONTACT,
    "admissions:admission": PageSEO.KEY_ADMISSION,
}


def _absolute(request, url: str) -> str:
    if not url:
        return ""
    if url.startswith(("http://", "https://")):
        return url
    return request.build_absolute_uri(url)


def seo_context(request):
    cfg = SEOSettings.get_solo()
    base = cfg.canonical_base()

    seo = {
        "title": cfg.site_title,
        "description": cfg.default_meta_description,
        "canonical": "",
        "og_title": "",
        "og_description": "",
        "og_image": "",
        "robots": cfg.robots_directive(),
        "site_title": cfg.site_title,
        "verification_google": cfg.verification_google,
        "verification_bing": cfg.verification_bing,
        "allow_indexing": cfg.allow_indexing,
    }

    page = None
    resolver = getattr(request, "resolver_match", None)
    url_name = ""
    if resolver is not None and resolver.namespace:
        url_name = f"{resolver.namespace}:{resolver.url_name}"

    override = getattr(request, "seo", None)
    if url_name in URL_NAME_MAP and override is None:
        page = PageSEO.objects.filter(key=URL_NAME_MAP[url_name]).first()

    if page is not None:
        seo["title"] = page.title or seo["title"]
        seo["description"] = page.meta_description or seo["description"]
        seo["og_title"] = page.og_title or seo["title"]
        seo["og_description"] = page.og_description or seo["description"]
        seo["robots"] = page.robots
        if page.og_image:
            seo["og_image"] = _absolute(request, page.og_image.url)
        if page.canonical_url:
            seo["canonical"] = page.canonical_url

    if override:
        seo.update({k: v for k, v in override.items() if v})

    if not seo["canonical"]:
        seo["canonical"] = _absolute(request, request.path)

    if not seo["og_title"]:
        seo["og_title"] = seo["title"]
    if not seo["og_description"]:
        seo["og_description"] = seo["description"]
    if not seo["og_image"] and cfg.default_share_image:
        seo["og_image"] = _absolute(request, cfg.default_share_image.url)

    seo["canonical_base"] = base
    # Never index while DEBUG is on, even if settings misconfigured.
    if settings.DEBUG:
        seo["robots"] = "noindex, nofollow"
        seo["allow_indexing"] = False
    return {"seo": seo}
