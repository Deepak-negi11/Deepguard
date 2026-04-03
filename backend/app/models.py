from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    tier: Mapped[str] = mapped_column(String(20), default="free")
    monthly_usage: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    requests: Mapped[list[VerificationRequest]] = relationship(back_populates="user")


class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="requests")
    result: Mapped[VerificationResult | None] = relationship(back_populates="request", uselist=False, cascade="all, delete-orphan")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("verification_requests.id", ondelete="CASCADE"), unique=True)
    authenticity_score: Mapped[float] = mapped_column(Float, nullable=False)
    verdict: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    breakdown: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    processing_time_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(128), default="prototype-v1")
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request: Mapped[VerificationRequest] = relationship(back_populates="result")
    evidence_items: Mapped[list[EvidenceItemRecord]] = relationship(
        back_populates="result",
        cascade="all, delete-orphan",
    )


class EvidenceItemRecord(Base):
    __tablename__ = "evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    result_id: Mapped[int] = mapped_column(ForeignKey("verification_results.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    timestamp_in_media: Mapped[float | None] = mapped_column(Float, nullable=True)
    visualization_hint: Mapped[str | None] = mapped_column(String(120), nullable=True)

    result: Mapped[VerificationResult] = relationship(back_populates="evidence_items")


class StoredAnalysisPayload(Base):
    __tablename__ = "stored_analysis_payloads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("verification_requests.id", ondelete="CASCADE"), unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ApiUsage(Base):
    __tablename__ = "api_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    endpoint: Mapped[str] = mapped_column(String(120), nullable=False)
    request_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
