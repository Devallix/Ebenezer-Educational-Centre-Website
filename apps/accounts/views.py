from __future__ import annotations

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from apps.core.services import log_action

from .forms import StaffAuthenticationForm

logger = logging.getLogger("apps.accounts")


def _rate_key(request) -> str:
    username = (request.POST.get("username") or "").strip().lower()
    ip = request.META.get("REMOTE_ADDR", "")
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    return f"login_attempts:{ip}:{username}"


def _too_many_attempts(request) -> bool:
    limit = getattr(settings, "LOGIN_RATE_LIMIT", 10)
    if limit <= 0:
        return False
    count = cache.get(_rate_key(request), 0)
    return count >= limit


def register_failed_attempt(request):
    window = getattr(settings, "LOGIN_RATE_WINDOW", 300)
    key = _rate_key(request)
    try:
        count = cache.get(key, 0) + 1
    except Exception:  # pragma: no cover
        count = 1
    cache.set(key, count, window)


def clear_attempts(request):
    cache.delete(_rate_key(request))


@method_decorator(never_cache, name="dispatch")
class StaffLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = StaffAuthenticationForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["locked_out"] = _too_many_attempts(self.request)
        try:
            from apps.school.models import HeroSlide

            context["slides"] = list(HeroSlide.objects.filter(is_active=True)[:5])
        except Exception:  # pragma: no cover
            context["slides"] = []
        return context

    def post(self, request, *args, **kwargs):
        if _too_many_attempts(request):
            messages.error(
                request,
                "Too many failed sign-in attempts. Please wait a few minutes and try again.",
            )
            return self.render_to_response(
                self.get_context_data(locked_out=True), status=429
            )
        response = super().post(request, *args, **kwargs)
        if isinstance(response, HttpResponseRedirect):
            clear_attempts(request)
            if request.user.is_authenticated:
                log_action(request, "login", model_name="User", description="Signed in")
        else:
            register_failed_attempt(request)
        return response

    def form_invalid(self, form):
        register_failed_attempt(self.request)
        return super().form_invalid(form)


@method_decorator(never_cache, name="dispatch")
class StaffLogoutView(auth_views.LogoutView):
    """Log the user out and send them to the dashboard login page."""

    http_method_names = ["get", "post", "options"]

    def get_default_redirect_url(self):
        """After signing out, send the user to the dashboard login page."""
        login_url = reverse("accounts:login")
        return f"{login_url}?next={reverse('dashboard:overview')}"

    def get(self, request, *args, **kwargs):
        """Allow sign-out via GET as well as POST."""
        return self.post(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            log_action(request, "logout", model_name="User", description="Signed out")
        return super().dispatch(request, *args, **kwargs)
