from app.services.demo_research import (
    cloud_platform_comparison_demo,
    nvidia_demo_report,
    semiconductor_equipment_demo,
)


def test_nvidia_demo_report_has_required_sections_and_no_advice() -> None:
    report = nvidia_demo_report()
    output = report["research_output"]

    assert report["demo_notice"]
    assert output["financial_quality"]
    assert set(output["valuation"]) == {"dcf", "ev_sales", "pe"}
    assert set(output["bull_base_bear"]) == {"bear", "base", "bull"}
    assert "buy now" not in str(report).lower()


def test_semiconductor_equipment_demo_has_industry_sections() -> None:
    report = semiconductor_equipment_demo()

    assert report["value_chain_map"]["upstream"]
    assert report["cycle_indicators"]
    assert report["tracking_metrics"]


def test_cloud_platform_comparison_demo_has_score_matrix() -> None:
    comparison = cloud_platform_comparison_demo()

    assert len(comparison["score_matrix"]) == 3
    assert comparison["score_matrix"][0]["ticker"] == "MSFT"
