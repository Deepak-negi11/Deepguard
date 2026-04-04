from __future__ import annotations

import secrets

from fastapi import HTTPException, Request, status

from app.config import get_settings

settings = get_settings()


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def enforce_csrf(request: Request) -> None:
    """Double-submit CSRF check for cookie-authenticated unsafe requests.

    - Only enforced when the auth cookie is present.
    - Bearer-token clients are not subject to CSRF.
    """

    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return

    auth_cookie = request.cookies.get(settings.auth_cookie_name)
    if not auth_cookie:
        return

    csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        )
