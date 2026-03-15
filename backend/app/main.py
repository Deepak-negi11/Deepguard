from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import router
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.security import decode_access_token
from app.services.rate_limiter import rate_limiter
from app.services.usage_logger import log_api_usage

settings = get_settings()
logger = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_v1_prefix)


def _resolve_request_identity(request: Request) -> tuple[str, int | None]:
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        try:
            payload = decode_access_token(token)
            user_id = int(payload.get("user_id"))
            return f"user:{user_id}", user_id
        except Exception:
            pass

    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}", None


@app.middleware("http")
async def rate_limit_and_log_requests(request: Request, call_next):
    identity, user_id = _resolve_request_identity(request)
    if request.url.path.startswith(settings.api_v1_prefix):
        allowed, retry_after = rate_limiter.check(identity, settings.rate_limit_requests_per_hour)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": str(retry_after)},
            )

    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)

    if settings.enable_api_usage_logging and request.url.path.startswith(settings.api_v1_prefix):
        db = SessionLocal()
        try:
            log_api_usage(
                db=db,
                endpoint=request.url.path,
                response_time_ms=duration_ms,
                status_code=response.status_code,
                user_id=user_id,
            )
        finally:
            db.close()

    return response


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_create_schema:
        logger.warning("Auto-creating database schema because DEEPGUARD_AUTO_CREATE_SCHEMA is enabled.")
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
