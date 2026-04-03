from __future__ import annotations

import logging
import time

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask, BackgroundTasks

from app.api.router import router
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.security import decode_access_token
from app.services.rate_limiter import rate_limiter
from app.services.usage_logger import log_api_usage

settings = get_settings()
logger = logging.getLogger(__name__)


def _persist_api_usage(*, endpoint: str, response_time_ms: float, status_code: int, user_id: int | None) -> None:
    db = SessionLocal()
    try:
        log_api_usage(
            db=db,
            endpoint=endpoint,
            response_time_ms=response_time_ms,
            status_code=status_code,
            user_id=user_id,
        )
    finally:
        db.close()


def _attach_background_task(response, task: BackgroundTask) -> None:
    if response.background is None:
        response.background = task
        return

    tasks = BackgroundTasks()
    existing = response.background
    if isinstance(existing, BackgroundTasks):
        for queued in existing.tasks:
            tasks.tasks.append(queued)
    else:
        tasks.tasks.append(existing)
    tasks.tasks.append(task)
    response.background = tasks


def enforce_rate_limit(request: Request) -> None:
    if settings.environment.lower() == "development":
        return

    identity, _ = _resolve_request_identity(request)
    allowed, retry_after = rate_limiter.check(identity, settings.rate_limit_requests_per_hour)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )


class LoggedRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            _, user_id = _resolve_request_identity(request)
            started_at = time.perf_counter()
            response = await original_route_handler(request)
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)

            if settings.enable_api_usage_logging:
                _attach_background_task(
                    response,
                    BackgroundTask(
                        _persist_api_usage,
                        endpoint=request.url.path,
                        response_time_ms=duration_ms,
                        status_code=response.status_code,
                        user_id=user_id,
                    ),
                )

            return response

        return custom_route_handler


router.route_class = LoggedRoute

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_v1_prefix, dependencies=[Depends(enforce_rate_limit)])


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


@app.on_event("startup")
def on_startup() -> None:
    if settings.environment.lower() == "production" and settings.secret_key == "change-me-in-production":
        raise RuntimeError("DEEPGUARD_SECRET_KEY must be set for production deployments.")
    should_bootstrap_schema = settings.auto_create_schema or (
        settings.environment.lower() != "production" and settings.database_url.startswith("sqlite")
    )
    if should_bootstrap_schema:
        logger.warning("Auto-creating database schema for the current environment.")
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
