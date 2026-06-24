from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import httpx

from app.connectors.base import ConnectorError, ConnectorResponse, HttpConnector
from app.core.config import settings

FRED_BASE = "https://api.stlouisfed.org/fred"


@dataclass(frozen=True)
class NormalizedMacroObservation:
    series_code: str
    observation_date: str
    value: Decimal
    unit: str
    frequency: str
    source_url: str
    source_hash: str


class FredConnector(HttpConnector):
    source_name = "FRED"

    def __init__(self, client: httpx.Client | None = None) -> None:
        super().__init__(
            timeout_seconds=settings.connector_timeout_seconds,
            cache_ttl_seconds=settings.connector_cache_ttl_seconds,
            max_requests_per_second=5,
            client=client,
        )

    def get_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> ConnectorResponse:
        if not settings.fred_api_key:
            raise ConnectorError("FRED_API_KEY is required for live FRED requests.")
        params: dict[str, Any] = {
            "series_id": series_id,
            "api_key": settings.fred_api_key,
            "file_type": "json",
        }
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        return self.get_json(f"{FRED_BASE}/series/observations", params=params)


def normalize_fred_observations(
    series_id: str,
    response: ConnectorResponse,
    *,
    unit: str = "index",
    frequency: str = "unknown",
) -> list[NormalizedMacroObservation]:
    normalized: list[NormalizedMacroObservation] = []
    for observation in response.payload.get("observations", []):
        value = observation.get("value")
        if value in {None, "."}:
            continue
        normalized.append(
            NormalizedMacroObservation(
                series_code=series_id,
                observation_date=observation["date"],
                value=Decimal(str(value)),
                unit=unit,
                frequency=frequency,
                source_url=response.metadata.source_url,
                source_hash=response.metadata.source_hash,
            )
        )
    return normalized
