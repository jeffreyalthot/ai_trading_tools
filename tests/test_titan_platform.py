from ai_trading_tools.titan_platform import TitanExecutionPlatform, build_roadmap_catalog, execute_r001, validate_r001


def test_catalog_contains_730_items() -> None:
    catalog = build_roadmap_catalog()
    assert len(catalog) == 730
    assert catalog[0].code == "R001"
    assert catalog[-1].code == "R730"


def test_platform_completion_and_gate() -> None:
    platform = TitanExecutionPlatform()
    status = execute_r001(platform, note="kpi owner set")
    assert status.completed is True
    assert platform.completion_ratio() > 0
    assert platform.promotion_stage(sharpe=1.3, drawdown=0.1, observations=500) == "capital_elargi"


def test_validation_template() -> None:
    assert validate_r001({"coverage": 0.9, "latency": 120.0, "stability": 0.95})
    assert not validate_r001({"coverage": 0.6, "latency": 120.0, "stability": 0.95})
