from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from time import monotonic, sleep
from typing import Any

import httpx


class ConnectorError(RuntimeError):
    pass


@dataclass(frozen=True)
class SourceMetadata:
    source_name: str
    source_url: str
    published_at: datetime
    retrieved_at: datetime
    confidence_score: float
    source_hash: str
    data_status: str = "active"


@dataclass(frozen=True)
class ConnectorResponse:
    payload: dict[str, Any]
    metadata: SourceMetadata
    response_status: int
    request_params: dict[str, Any] | None = None


class SimpleTTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, tuple[float, ConnectorResponse]] = {}

    def get(self, key: str) -> ConnectorResponse | None:
        item = self._items.get(key)
        if item is None:
            return None
        expires_at, value = item
        if monotonic() > expires_at:
            del self._items[key]
            return None
        return value

    def set(self, key: str, value: ConnectorResponse) -> None:
        self._items[key] = (monotonic() + self.ttl_seconds, value)


class RateLimiter:
    def __init__(self, max_per_second: float) -> None:
        self.min_interval = 1.0 / max_per_second
        self._last_call = 0.0

    def wait(self) -> None:
        elapsed = monotonic() - self._last_call
        if elapsed < self.min_interval:
            sleep(self.min_interval - elapsed)
        self._last_call = monotonic()


class HttpConnector:
    source_name = "External Source"

    def __init__(
        self,
        *,
        timeout_seconds: float,
        cache_ttl_seconds: int,
        max_requests_per_second: float,
        client: httpx.Client | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.client = client or httpx.Client(timeout=timeout_seconds, headers=headers)
        self.cache = SimpleTTLCache(cache_ttl_seconds)
        self.rate_limiter = RateLimiter(max_requests_per_second)

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> ConnectorResponse:
        cache_key = stable_hash({"url": url, "params": params})
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        response: httpx.Response | None = None
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                self.rate_limiter.wait()
                response = self.client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ConnectorError("Connector expected a JSON object response.")
                connector_response = ConnectorResponse(
                    payload=payload,
                    metadata=SourceMetadata(
                        source_name=self.source_name,
                        source_url=str(response.url),
                        published_at=parse_http_date(response.headers.get("last-modified")),
                        retrieved_at=datetime.now(UTC),
                        confidence_score=0.95,
                        source_hash=stable_hash(payload),
                    ),
                    response_status=response.status_code,
                    request_params=params,
                )
                self.cache.set(cache_key, connector_response)
                return connector_response
            except (httpx.HTTPError, ValueError, ConnectorError) as error:
                last_error = error
                if attempt < 2:
                    sleep(0.25 * (attempt + 1))

        status = response.status_code if response is not None else "no-response"
        raise ConnectorError(f"Request failed for {url}; status={status}; error={last_error}")


def stable_hash(payload: Any) -> str:
    import json

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(encoded.encode("utf-8")).hexdigest()


def parse_http_date(value: str | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    try:
        from email.utils import parsedate_to_datetime

        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except (TypeError, ValueError):
        return datetime.now(UTC)
