from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.connectors.base import ConnectorResponse
from app.schemas import DataUpdateLogCreate, RawDataRecordCreate


def raw_record_from_response(
    connector_name: str,
    response: ConnectorResponse,
    *,
    normalized_status: str = "pending",
    error_message: str | None = None,
) -> RawDataRecordCreate:
    return RawDataRecordCreate(
        connector_name=connector_name,
        request_url=response.metadata.source_url,
        request_params=response.request_params,
        response_payload=response.payload,
        response_status=response.response_status,
        normalized_status=normalized_status,
        error_message=error_message,
        source_name=response.metadata.source_name,
        source_url=response.metadata.source_url,
        published_at=response.metadata.published_at,
        retrieved_at=response.metadata.retrieved_at,
        currency=None,
        fiscal_period=None,
        confidence_score=Decimal(str(response.metadata.confidence_score)),
        source_hash=response.metadata.source_hash,
        data_status=response.metadata.data_status,
    )


def update_log(
    *,
    connector_name: str,
    job_type: str,
    target_identifier: str,
    status: str,
    records_read: int = 0,
    records_written: int = 0,
    error_message: str | None = None,
    source_url: str = "internal://insightos/data-update",
) -> DataUpdateLogCreate:
    now = datetime.now(UTC)
    return DataUpdateLogCreate(
        connector_name=connector_name,
        job_type=job_type,
        target_identifier=target_identifier,
        started_at=now,
        finished_at=now,
        status=status,
        records_read=records_read,
        records_written=records_written,
        error_message=error_message,
        source_name="InsightOS Data Update Task",
        source_url=source_url,
        published_at=now,
        retrieved_at=now,
        currency=None,
        fiscal_period=None,
        confidence_score=Decimal("1.0000"),
        source_hash=task_hash(connector_name, job_type, target_identifier, status, records_read),
        data_status="active",
    )


def task_hash(*parts: Any) -> str:
    from app.connectors.base import stable_hash

    return stable_hash([str(part) for part in parts])
