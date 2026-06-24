from __future__ import annotations

from fastapi import APIRouter

from app.services.archetypes import ARCHETYPES, archetype_examples, match_company_archetype

router = APIRouter(prefix="/api/archetypes", tags=["archetypes"])


@router.get("")
def list_archetypes() -> dict[str, object]:
    return {"archetypes": list(ARCHETYPES.values())}


@router.get("/examples")
def get_archetype_examples() -> dict[str, object]:
    return {"examples": archetype_examples()}


@router.get("/match/{ticker}")
def match_archetype(ticker: str, industry_text: str | None = None) -> dict[str, object]:
    archetype = match_company_archetype(ticker, industry_text)
    return {"ticker": ticker.upper(), "archetype": archetype}
