from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token


def _extract_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip() or None

    # Cookie-based auth for browser clients.
    from app.config import get_settings

    settings = get_settings()
    cookie_value = request.cookies.get(settings.auth_cookie_name)
    return cookie_value or None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:  # noqa: B008
    """Resolve the authenticated user from bearer token or auth cookie."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = _extract_token(request)
    if not token:
        raise credentials_exception

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("user_id"))
    except (JWTError, TypeError, ValueError) as exc:
        raise credentials_exception from exc

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user
