from ai_trading_tools.titan_runtime import ServiceHealth, TitanRuntimeControlPlane, runtime_guard_r001, runtime_budget_r001


def test_runtime_control_plane() -> None:
    plane = TitanRuntimeControlPlane()
    plane.update_health(ServiceHealth(name="ingestor", latency_ms=40, error_rate=0.001, saturation=0.4))
    assert plane.global_health() is True

    incident = plane.open_incident("INC-1", "high")
    assert incident.incident_id == "INC-1"
    plane.resolve_incident("INC-1", "fixed")
    assert plane.incidents["INC-1"].resolved_at is not None


def test_runtime_helpers() -> None:
    assert runtime_guard_r001(latency_ms=120.0, error_rate=0.001, saturation=0.7)
    assert not runtime_guard_r001(latency_ms=400.0, error_rate=0.001, saturation=0.7)
    budget = runtime_budget_r001(events_per_second=1200.0, cpu_pct=30.0, memory_pct=40.0)
    assert 0.0 <= budget["runtime_score"] <= 1.0
