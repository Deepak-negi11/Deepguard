from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.csrf import new_csrf_token
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import AuthResponse, LoginRequest, RegisterRequest, SessionUserResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter()
settings = get_settings()


def _set_auth_cookies(*, response: Response, access_token: str, csrf_token: str) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=csrf_token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def _normalize_email(value: str) -> str:
    return value.strip().lower()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:  # noqa: B008
    email = _normalize_email(payload.email)
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc
    db.refresh(user)
    token = create_access_token(subject=user.email, user_id=user.id)
    csrf_token = new_csrf_token()
    _set_auth_cookies(response=response, access_token=token, csrf_token=csrf_token)
    return AuthResponse(user_id=user.id, email=user.email, access_token=token)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:  # noqa: B008
    email = _normalize_email(payload.email)
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=user.email, user_id=user.id)
    csrf_token = new_csrf_token()
    _set_auth_cookies(response=response, access_token=token, csrf_token=csrf_token)
    return AuthResponse(user_id=user.id, email=user.email, access_token=token)


@router.get("/me", response_model=SessionUserResponse)
def get_me(user: User = Depends(get_current_user)) -> SessionUserResponse:  # noqa: B008
    return SessionUserResponse(user_id=user.id, email=user.email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(key=settings.auth_cookie_name, path="/")
    response.delete_cookie(key=settings.csrf_cookie_name, path="/")
