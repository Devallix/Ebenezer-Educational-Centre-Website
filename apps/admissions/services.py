from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMessage

from apps.core.models import NotificationLog, NotificationSettings

logger = logging.getLogger("apps.admissions")


def _from_email(notif: NotificationSettings) -> str:
    if notif.sender_email:
        name = notif.sender_name or "Ebenezer Educational Centre"
        return f"{name} <{notif.sender_email}>"
    return settings.DEFAULT_FROM_EMAIL


def _log(kind, status, recipients, subject, related, error=""):
    try:
        NotificationLog.objects.create(
            kind=kind,
            status=status,
            recipients=", ".join(recipients)[:500],
            subject=subject[:255],
            related_model=related.__class__.__name__,
            related_object_id=str(getattr(related, "pk", "") or ""),
            error_message=error[:2000],
        )
    except Exception:  # pragma: no cover
        logger.exception("Failed to write notification log")


def _send(kind, subject, body, recipients, related, reply_to=None) -> bool:
    notif = NotificationSettings.get_solo()
    if not recipients:
        _log(kind, NotificationLog.STATUS_FAILED, [], subject, related, "No recipients configured")
        return False
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=_from_email(notif),
            to=recipients,
            reply_to=[reply_to] if reply_to else None,
        )
        email.send(fail_silently=False)
    except Exception as exc:  # delivery must never break the request
        logger.warning("Notification email failed: %s", exc)
        _log(kind, NotificationLog.STATUS_FAILED, recipients, subject, related, str(exc))
        return False
    _log(kind, NotificationLog.STATUS_SENT, recipients, subject, related)
    return True


def _contact_line(obj) -> str:
    parts = []
    if getattr(obj, "phone", ""):
        parts.append(f"Phone: {obj.phone}")
    if getattr(obj, "email", ""):
        parts.append(f"Email: {obj.email}")
    return "\n".join(parts)


def notify_new_admission(enquiry) -> None:
    notif = NotificationSettings.get_solo()
    if not notif.notify_admissions:
        return
    site = settings.SITE_URL
    body = (
        "A new admission enquiry has been submitted.\n\n"
        f"Parent/guardian: {enquiry.parent_name}\n"
        f"Child's first name: {enquiry.child_first_name}\n"
        f"Preferred class: {enquiry.preferred_class or 'Not specified'}\n"
        f"Preferred period: {enquiry.preferred_period or 'Not specified'}\n"
        f"{_contact_line(enquiry)}\n\n"
        f"Message:\n{enquiry.message or '(none)'}\n\n"
        f"View in dashboard: {site}/dashboard/admissions/{enquiry.pk}/\n"
    )
    _send(
        NotificationLog.KIND_STAFF,
        f"{notif.admission_subject or 'New admission enquiry'}: {enquiry.parent_name}",
        body,
        notif.recipients,
        enquiry,
        reply_to=enquiry.email or None,
    )
    if notif.send_parent_confirmation and enquiry.email:
        parent_body = (
            f"Dear {enquiry.parent_name},\n\n"
            "Thank you for your interest in Ebenezer Educational Centre. "
            "We have received your admission enquiry and a member of our team "
            "will contact you shortly.\n\n"
            f"Child's name: {enquiry.child_first_name}\n"
            f"Preferred class: {enquiry.preferred_class or 'Not specified'}\n\n"
            "Warm regards,\nEbenezer Educational Centre"
        )
        _send(
            NotificationLog.KIND_PARENT,
            "We received your admission enquiry",
            parent_body,
            [enquiry.email],
            enquiry,
        )


def notify_new_contact(message) -> None:
    notif = NotificationSettings.get_solo()
    if not notif.notify_contact:
        return
    site = settings.SITE_URL
    body = (
        "A new message has been submitted through the website contact form.\n\n"
        f"Name: {message.name}\n"
        f"{_contact_line(message)}\n"
        f"Category: {message.get_category_display()}\n"
        f"Subject: {message.subject}\n\n"
        f"Message:\n{message.message}\n\n"
        f"View in dashboard: {site}/dashboard/messages/{message.pk}/\n"
    )
    _send(
        NotificationLog.KIND_STAFF,
        f"{notif.contact_subject or 'New website message'}: {message.subject}",
        body,
        notif.recipients,
        message,
        reply_to=message.email or None,
    )
