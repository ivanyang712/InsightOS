from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndustryArchetype:
    key: str
    name: str
    operating_metrics: list[str]
    financial_metrics: list[str]
    common_risks: list[str]
    valuation_priority: list[str]
    peer_comparison_principles: list[str]
    fallback_metrics: list[str]
    not_applicable_metrics: list[str]


ARCHETYPES: dict[str, IndustryArchetype] = {
    "saas_software": IndustryArchetype(
        key="saas_software",
        name="SaaS / Software",
        operating_metrics=["ARR", "net revenue retention", "gross retention", "CAC payback"],
        financial_metrics=["revenue growth", "gross margin", "FCF margin", "Rule of 40"],
        common_risks=["seat expansion slowdown", "pricing pressure", "AI feature commoditization"],
        valuation_priority=["EV/Sales", "EV/FCF", "DCF"],
        peer_comparison_principles=[
            "Compare recurring revenue mix and retention before headline growth."
        ],
        fallback_metrics=["billings growth", "remaining performance obligations"],
        not_applicable_metrics=["inventory turnover", "reserve ratio"],
    ),
    "consumer_goods": IndustryArchetype(
        key="consumer_goods",
        name="Consumer Goods",
        operating_metrics=[
            "volume / price / mix",
            "channel inventory",
            "market share",
            "customer concentration",
        ],
        financial_metrics=["gross margin", "operating margin", "working capital", "inventory days"],
        common_risks=["private label pressure", "input cost inflation", "retailer concentration"],
        valuation_priority=["PE", "EV/EBITDA", "DCF"],
        peer_comparison_principles=["Separate volume growth from price/mix and FX effects."],
        fallback_metrics=["organic sales growth", "sell-through commentary"],
        not_applicable_metrics=["net interest margin", "proved reserves"],
    ),
    "retail": IndustryArchetype(
        key="retail",
        name="Retail",
        operating_metrics=["same-store sales", "traffic", "basket size", "inventory turns"],
        financial_metrics=["gross margin", "operating margin", "lease-adjusted leverage"],
        common_risks=["inventory markdowns", "wage inflation", "consumer demand slowdown"],
        valuation_priority=["PE", "EV/EBITDA", "DCF"],
        peer_comparison_principles=["Compare store format, online mix, and inventory discipline."],
        fallback_metrics=["comparable sales", "gross merchandise value"],
        not_applicable_metrics=["ARR", "loss ratio"],
    ),
    "manufacturing": IndustryArchetype(
        key="manufacturing",
        name="Manufacturing",
        operating_metrics=[
            "volume / price / mix",
            "capacity utilization",
            "backlog",
            "supply chain risk",
            "customer concentration",
        ],
        financial_metrics=["gross margin", "working capital", "inventory days", "ROIC"],
        common_risks=["capacity underutilization", "input cost volatility", "supply disruption"],
        valuation_priority=["EV/EBITDA", "DCF", "PE"],
        peer_comparison_principles=["Normalize for cycle position and capacity utilization."],
        fallback_metrics=["order growth", "book-to-bill"],
        not_applicable_metrics=["net retention", "loan loss provision"],
    ),
    "semiconductor": IndustryArchetype(
        key="semiconductor",
        name="Semiconductor",
        operating_metrics=["wafer starts", "book-to-bill", "ASP", "design wins"],
        financial_metrics=["gross margin", "capex intensity", "inventory days", "FCF margin"],
        common_risks=["inventory cycle", "export controls", "customer concentration"],
        valuation_priority=["PE", "EV/Sales", "DCF"],
        peer_comparison_principles=["Separate cyclical rebound from durable content growth."],
        fallback_metrics=["backlog", "data center revenue mix"],
        not_applicable_metrics=["same-store sales", "loss ratio"],
    ),
    "bank": IndustryArchetype(
        key="bank",
        name="Bank",
        operating_metrics=["loan growth", "deposit beta", "net interest margin", "credit cost"],
        financial_metrics=["ROE", "CET1", "efficiency ratio", "loan loss provision"],
        common_risks=["credit deterioration", "duration mismatch", "deposit flight"],
        valuation_priority=["PB", "PE", "dividend yield"],
        peer_comparison_principles=[
            "Compare capital, asset mix, funding base, and credit quality."
        ],
        fallback_metrics=["tangible book value", "non-performing assets"],
        not_applicable_metrics=["gross margin", "EV/EBITDA"],
    ),
    "insurance": IndustryArchetype(
        key="insurance",
        name="Insurance",
        operating_metrics=["combined ratio", "loss ratio", "premium growth", "reserve development"],
        financial_metrics=["ROE", "book value growth", "investment yield"],
        common_risks=["under-reserving", "catastrophe losses", "duration mismatch"],
        valuation_priority=["PB", "PE", "embedded value"],
        peer_comparison_principles=["Compare underwriting quality before investment income."],
        fallback_metrics=["net written premiums", "reserve adequacy"],
        not_applicable_metrics=["ARR", "same-store sales"],
    ),
    "reit": IndustryArchetype(
        key="reit",
        name="REIT",
        operating_metrics=["occupancy", "same-property NOI", "lease spread", "WALE"],
        financial_metrics=["FFO", "AFFO", "net debt / EBITDA", "dividend payout"],
        common_risks=["refinancing risk", "cap rate expansion", "tenant concentration"],
        valuation_priority=["P/AFFO", "NAV discount", "dividend yield"],
        peer_comparison_principles=["Compare property type, lease maturity, and leverage."],
        fallback_metrics=["NOI growth", "occupancy"],
        not_applicable_metrics=["inventory turnover", "gross margin"],
    ),
    "energy": IndustryArchetype(
        key="energy",
        name="Energy",
        operating_metrics=["production volume", "realized price", "reserve life", "lifting cost"],
        financial_metrics=["FCF yield", "net debt", "ROCE", "capex intensity"],
        common_risks=["commodity price volatility", "reserve replacement", "regulatory risk"],
        valuation_priority=["EV/EBITDA", "DCF", "NAV"],
        peer_comparison_principles=["Normalize for commodity strip and reserve quality."],
        fallback_metrics=["hedge book", "production guidance"],
        not_applicable_metrics=["net retention", "same-store sales"],
    ),
    "healthcare_biotech": IndustryArchetype(
        key="healthcare_biotech",
        name="Healthcare / Biotech",
        operating_metrics=["pipeline stage", "trial readouts", "approval status", "patent life"],
        financial_metrics=["R&D intensity", "cash runway", "revenue growth"],
        common_risks=["clinical failure", "regulatory delay", "patent cliff"],
        valuation_priority=["risk-adjusted NPV", "DCF", "EV/Sales"],
        peer_comparison_principles=["Compare pipeline probability and cash runway."],
        fallback_metrics=["cash runway", "trial milestones"],
        not_applicable_metrics=["inventory turnover", "same-store sales"],
    ),
    "internet_platform": IndustryArchetype(
        key="internet_platform",
        name="Internet Platform",
        operating_metrics=["MAU/DAU", "engagement", "take rate", "ad load"],
        financial_metrics=["revenue growth", "operating margin", "FCF margin", "capex intensity"],
        common_risks=["regulation", "traffic acquisition cost", "platform disintermediation"],
        valuation_priority=["DCF", "PE", "EV/Sales"],
        peer_comparison_principles=[
            "Compare engagement quality and monetization, not users alone."
        ],
        fallback_metrics=["ARPU", "impressions growth"],
        not_applicable_metrics=["loan loss provision", "reserve life"],
    ),
    "logistics_transportation": IndustryArchetype(
        key="logistics_transportation",
        name="Logistics / Transportation",
        operating_metrics=["load factor", "yield", "on-time performance", "fleet utilization"],
        financial_metrics=["operating margin", "fuel cost ratio", "capex intensity", "ROIC"],
        common_risks=["fuel volatility", "labor disruption", "network underutilization"],
        valuation_priority=["EV/EBITDA", "PE", "DCF"],
        peer_comparison_principles=["Normalize for route mix and cycle position."],
        fallback_metrics=["ton-miles", "package volume"],
        not_applicable_metrics=["ARR", "net interest margin"],
    ),
}


COMPANY_ARCHETYPE_HINTS = {
    "AAPL": "consumer_goods",
    "NVDA": "semiconductor",
    "KO": "consumer_goods",
    "JPM": "bank",
    "MSFT": "saas_software",
    "GOOGL": "internet_platform",
    "AMZN": "internet_platform",
}


def match_company_archetype(ticker: str, industry_text: str | None = None) -> IndustryArchetype:
    key = COMPANY_ARCHETYPE_HINTS.get(ticker.upper())
    if key is not None:
        return ARCHETYPES[key]
    text = (industry_text or "").lower()
    for candidate_key, archetype in ARCHETYPES.items():
        if (
            archetype.name.lower().split(" / ")[0] in text
            or candidate_key.replace("_", " ") in text
        ):
            return archetype
    return ARCHETYPES["manufacturing"]


def archetype_examples() -> dict[str, dict[str, object]]:
    return {
        ticker: {
            "ticker": ticker,
            "archetype": match_company_archetype(ticker).key,
            "template": match_company_archetype(ticker),
        }
        for ticker in ("AAPL", "NVDA", "KO", "JPM")
    }
