from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import Resolver404, resolve


def _is_photos_calendar_or_media_path(path):
    """URLs that must only be reachable with a paired fencer profile."""
    if path == "/photos" or path.startswith("/photos/"):
        return True
    if path == "/calendar" or path.startswith("/calendar/"):
        return True
    media_url = (getattr(settings, "MEDIA_URL", "/media/") or "/media/").rstrip("/")
    if media_url and (path == media_url or path.startswith(media_url + "/")):
        return True
    return False


class RequireFencerProfileMiddleware:
    """Logged-in users must pair to a FencerProfile before using the app."""

    ALLOWED_URL_NAMES = frozenset(
        {
            "match_profile",
            "logout",
            "password_change",
            "password_change_done",
        }
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            request.fencer_profile = getattr(user, "fencer_profile", None)
        else:
            request.fencer_profile = None

        path = request.path

        static_url = getattr(settings, "STATIC_URL", "/static/") or "/static/"
        if static_url.startswith("/") and path.startswith(static_url):
            return self.get_response(request)

        if user.is_authenticated and user.is_staff and path.startswith("/admin/"):
            return self.get_response(request)

        if _is_photos_calendar_or_media_path(path):
            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if request.fencer_profile is None:
                return redirect("match_profile")
            return self.get_response(request)

        block_response = self._redirect_if_unpaired(request, path)
        if block_response is not None:
            return block_response

        return self.get_response(request)

    def _redirect_if_unpaired(self, request, path):
        user = request.user
        if not user.is_authenticated or request.fencer_profile is not None:
            return None

        try:
            match = resolve(path)
        except Resolver404:
            return redirect("match_profile")

        if match.url_name in self.ALLOWED_URL_NAMES:
            return None

        return redirect("match_profile")
