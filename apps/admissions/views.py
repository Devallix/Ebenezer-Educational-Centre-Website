from __future__ import annotations

import logging

from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect, render

from apps.analytics.models import SiteAnalyticsEvent
from apps.analytics.services import record_event
from apps.core.models import SchoolSettings

from .forms import AdmissionEnquiryForm, ContactForm
from .services import notify_new_admission, notify_new_contact

logger = logging.getLogger("apps.admissions")

SUBMISSION_LIMIT = 5
SUBMISSION_WINDOW = 600


def _client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _rate_limited(request, bucket: str) -> bool:
    ip = _client_ip(request)
    key = f"form_submit:{bucket}:{ip}"
    count = cache.get(key, 0)
    if count >= SUBMISSION_LIMIT:
        return True
    cache.set(key, count + 1, SUBMISSION_WINDOW)
    return False


def contact(request):
    if request.method == "POST":
        if _rate_limited(request, "contact"):
            messages.error(
                request, "Too many submissions. Please wait a few minutes and try again."
            )
            return redirect("admissions:contact")
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.source_ip = _client_ip(request) or None
            message.save()
            notify_new_contact(message)
            record_event(request, SiteAnalyticsEvent.EVENT_CONTACT)
            messages.success(
                request,
                "Thank you. Your message has been received and we will respond shortly.",
            )
            return redirect("admissions:contact")
        messages.error(request, "Please correct the highlighted fields and try again.")
    else:
        form = ContactForm()

    request.seo = {"title": "Contact Us | Ebenezer Educational Centre"}
    return render(
        request,
        "admissions/contact.html",
        {"form": form, "school": SchoolSettings.get_solo()},
    )


def admission(request):
    if request.method == "POST":
        if _rate_limited(request, "admission"):
            messages.error(
                request, "Too many submissions. Please wait a few minutes and try again."
            )
            return redirect("admissions:admission")
        form = AdmissionEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.source_ip = _client_ip(request) or None
            enquiry.save()
            notify_new_admission(enquiry)
            record_event(request, SiteAnalyticsEvent.EVENT_ADMISSION)
            messages.success(
                request,
                "Thank you. Your admission enquiry has been received. "
                "Our team will contact you soon.",
            )
            return redirect("admissions:admission")
        messages.error(request, "Please correct the highlighted fields and try again.")
    else:
        initial = {}
        prefill_class = request.GET.get("class", "").strip()
        if prefill_class.isdigit():
            initial["preferred_class"] = prefill_class
        form = AdmissionEnquiryForm(initial=initial)

    request.seo = {"title": "Admission Enquiries | Ebenezer Educational Centre"}
    return render(request, "admissions/admission.html", {"form": form})
