from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DataStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ERROR = "error"
    DELETED = "deleted"


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class IdMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class ProvenanceMixin:
    source_name: Mapped[str] = mapped_column(String(120), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    fiscal_period: Mapped[str | None] = mapped_column(String(32), nullable=True)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    data_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=DataStatus.ACTIVE.value
    )


class EvidenceModelMixin(IdMixin, ProvenanceMixin, TimestampMixin):
    pass
