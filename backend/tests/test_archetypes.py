from app.services.archetypes import ARCHETYPES, archetype_examples, match_company_archetype


def test_all_required_archetypes_exist() -> None:
    assert len(ARCHETYPES) >= 12
    assert "manufacturing" in ARCHETYPES
    assert "consumer_goods" in ARCHETYPES
    assert "volume / price / mix" in ARCHETYPES["manufacturing"].operating_metrics
    assert "channel inventory" in ARCHETYPES["consumer_goods"].operating_metrics


def test_company_matching_examples() -> None:
    assert match_company_archetype("AAPL").key == "consumer_goods"
    assert match_company_archetype("NVDA").key == "semiconductor"
    assert match_company_archetype("KO").key == "consumer_goods"
    assert match_company_archetype("JPM").key == "bank"


def test_examples_return_distinct_templates() -> None:
    examples = archetype_examples()

    assert examples["AAPL"]["archetype"] != examples["JPM"]["archetype"]
    assert examples["NVDA"]["archetype"] == "semiconductor"
