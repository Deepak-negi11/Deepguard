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


class SessionUserResponse(BaseModel):
    user_id: int
    email: EmailStr


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
    mode: Literal["image", "news"]
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
    gradcam_overlay_url: str | None = None


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


class DemoDatasetEntry(BaseModel):
    key: str
    display_name: str
    category: str
    source_url: str
    access: str
    notes: list[str] = Field(default_factory=list)


class DemoSourceLink(BaseModel):
    label: str
    category: Literal["news", "image", "general"]
    url: str
    purpose: str


class ModelRegistryEntry(BaseModel):
    key: str
    mode: Literal["image", "news"]
    display_name: str
    provider: str
    model_id: str
    source: Literal["prototype", "local_weights", "huggingface"]
    active_version: str
    weights_path: str | None = None
    dataset_version: str | None = None
    trained_at: str | None = None
    validation_accuracy: float | None = None
    notes: list[str] = Field(default_factory=list)


class ModelStatusEntry(BaseModel):
    mode: Literal["image", "news"]
    analyzer_family: str
    source: Literal["prototype", "local_weights", "huggingface"]
    model_id: str
    local_weights_available: bool
    local_weights_path: str | None = None
    warmup_on_startup: bool = False
    notes: list[str] = Field(default_factory=list)


class BenchmarkCaseEntry(BaseModel):
    key: str
    mode: Literal["image", "news"]
    title: str
    input_kind: Literal["text", "file"]
    expected_verdict: Literal["likely real", "likely fake", "uncertain"]
    text: str | None = None
    url: str | None = None
    sample_path: str | None = None
    required: bool = True
    notes: list[str] = Field(default_factory=list)


class SystemStatusResponse(BaseModel):
    app_name: str
    environment: str
    supported_modes: list[Literal["image", "news"]]
    demo_analyzers_enabled: bool
    celery_workers_enabled: bool
    upload_storage: str
    news_url_fetch_enabled: bool
    datasets: list[DemoDatasetEntry] = Field(default_factory=list)
    sample_sources: list[DemoSourceLink] = Field(default_factory=list)
    model_registry: list[ModelRegistryEntry] = Field(default_factory=list)
    model_status: list[ModelStatusEntry] = Field(default_factory=list)
    benchmark_suite: list[BenchmarkCaseEntry] = Field(default_factory=list)


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
