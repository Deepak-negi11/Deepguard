from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    user_id: int
    email: EmailStr
    access_token: str
    token_type: str = "bearer"


class NewsVerifyRequest(BaseModel):
    text: str | None = Field(default=None, min_length=20)
    url: HttpUrl | None = None


class EvidenceItem(BaseModel):
    category: str
    severity: Literal["low", "medium", "high"]
    description: str
    timestamp: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    visualization_hint: str | None = None


class AnalysisInputProfile(BaseModel):
    mode: Literal["video", "news", "audio"]
    filename: str | None = None
    content_type: str | None = None
    size_bytes: int | None = None
    url_domain: str | None = None
    text_length: int | None = None
    analyzer_family: str


class AnalysisPayload(BaseModel):
    authenticity_score: float
    verdict: str
    confidence: float
    summary: str
    disclaimer: str
    breakdown: dict[str, float]
    evidence: list[EvidenceItem]
    recommended_actions: list[str] = Field(default_factory=list)
    input_profile: AnalysisInputProfile
    processing_time_seconds: float
    model_version: str


class TaskQueuedResponse(BaseModel):
    task_id: str
    request_id: str
    status: Literal["queued"]
    message: str


class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    current_step: str
    result: AnalysisPayload | None = None


class HistoryItem(BaseModel):
    request_id: str
    type: str
    status: str
    verdict: str | None = None
    confidence: float | None = None
    created_at: datetime


class HistoryResponse(BaseModel):
    total: int
    results: list[HistoryItem]


class TokenPayload(BaseModel):
    sub: str
    user_id: int
    exp: int


class StoredJob(BaseModel):
    task_id: str
    request_id: str
    status: str
    progress: int
    current_step: str
    result: AnalysisPayload | None = None
