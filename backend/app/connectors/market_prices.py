from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from io import StringIO

import httpx

from app.connectors.base import ConnectorError, SourceMetadata, stable_hash
from app.core.config import settings

STOOQ_DAILY_URL = "https://stooq.com/q/d/l/"


@dataclass(frozen=True)
class PriceBar:
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass(frozen=True)
class MarketPriceResponse:
    ticker: str
    bars: list[PriceBar]
    metadata: SourceMetadata
    response_status: int


class MarketPriceConnector:
    source_name = "Stooq Daily Historical Prices"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=settings.connector_timeout_seconds)

    def get_daily_prices(self, ticker: str) -> MarketPriceResponse:
        normalized = normalize_stooq_symbol(ticker)
        params = {"s": normalized, "i": "d"}
        response = self.client.get(STOOQ_DAILY_URL, params=params)
        try:
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise ConnectorError(f"Market price request failed for {ticker}: {error}") from error

        bars = parse_stooq_csv(response.text)
        if not bars:
            raise ConnectorError(f"No market price rows returned for {ticker}.")

        retrieved_at = datetime.now(UTC)
        source_url = str(response.url)
        return MarketPriceResponse(
            ticker=ticker.upper().strip(),
            bars=bars,
            metadata=SourceMetadata(
                source_name=self.source_name,
                source_url=source_url,
                published_at=retrieved_at,
                retrieved_at=retrieved_at,
                confidence_score=0.82,
                source_hash=stable_hash([bar_to_hash_payload(bar) for bar in bars]),
            ),
            response_status=response.status_code,
        )


def normalize_stooq_symbol(ticker: str) -> str:
    normalized = ticker.lower().strip().replace("-", ".")
    if "." not in normalized:
        return f"{normalized}.us"
    return normalized


def parse_stooq_csv(content: str) -> list[PriceBar]:
    rows = csv.DictReader(StringIO(content.strip()))
    bars: list[PriceBar] = []
    for row in rows:
        parsed = parse_price_row(row)
        if parsed is not None:
            bars.append(parsed)
    return sorted(bars, key=lambda bar: bar.date)


def parse_price_row(row: dict[str, str]) -> PriceBar | None:
    try:
        raw_date = row.get("Date")
        if raw_date is None or raw_date.lower() == "no data":
            return None
        return PriceBar(
            date=date.fromisoformat(raw_date),
            open=Decimal(row["Open"]),
            high=Decimal(row["High"]),
            low=Decimal(row["Low"]),
            close=Decimal(row["Close"]),
            volume=int(row.get("Volume") or 0),
        )
    except (KeyError, ValueError, InvalidOperation):
        return None


def bar_to_hash_payload(bar: PriceBar) -> dict[str, str | int]:
    return {
        "date": bar.date.isoformat(),
        "open": str(bar.open),
        "high": str(bar.high),
        "low": str(bar.low),
        "close": str(bar.close),
        "volume": bar.volume,
    }
