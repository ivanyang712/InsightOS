from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.connectors import ConnectorError
from app.services.company_research import (
    UnsupportedTickerError,
    run_single_company_research,
)

router = APIRouter(prefix="/api/research", tags=["research"])


@router.get("/company/{ticker}")
def get_company_research(ticker: str) -> dict[str, object]:
    try:
        return run_single_company_research(ticker)
    except UnsupportedTickerError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ConnectorError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
