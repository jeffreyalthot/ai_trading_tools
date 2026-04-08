from pathlib import Path

import pandas as pd

from ai_trading_tools.signal_engine import AISignalConfig, AISignalEngine


def test_load_legacy_prediction(tmp_path: Path) -> None:
    signal_file = tmp_path / "signals.csv"
    signal_file.write_text(
        "date,prediction\n"
        "2026-01-01T00:00:00Z,0.4\n"
        "2026-01-01T00:15:00Z,-0.2\n",
        encoding="utf-8",
    )

    engine = AISignalEngine(AISignalConfig(signal_file=signal_file))
    loaded = engine.load_signals()

    assert list(loaded.columns) == ["date", "ai_prediction", "ai_regime"]
    assert loaded["ai_prediction"].tolist() == [0.4, -0.2]


def test_load_weighted_ensemble_prediction(tmp_path: Path) -> None:
    signal_file = tmp_path / "ensemble.csv"
    signal_file.write_text(
        "date,prediction_fast,prediction_slow,weight_fast,weight_slow,regime\n"
        "2026-01-01T00:00:00Z,0.8,0.2,0.75,0.25,trend\n",
        encoding="utf-8",
    )

    engine = AISignalEngine(AISignalConfig(signal_file=signal_file))
    loaded = engine.load_signals()

    assert round(float(loaded.iloc[0]["ai_prediction"]), 4) == 0.65
    assert loaded.iloc[0]["ai_regime"] == "trend"


def test_merge_fills_missing_predictions(tmp_path: Path) -> None:
    signal_file = tmp_path / "signals.csv"
    signal_file.write_text(
        "date,prediction\n"
        "2026-01-01T00:00:00Z,0.1\n",
        encoding="utf-8",
    )

    dataframe = pd.DataFrame(
        {
            "date": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:15:00Z",
            ],
            "close": [100.0, 101.0],
            "volume": [10, 12],
        }
    )

    engine = AISignalEngine(AISignalConfig(signal_file=signal_file))
    merged = engine.merge_into_dataframe(dataframe)

    assert merged["ai_prediction"].tolist() == [0.1, 0.0]
    assert merged["ai_regime"].tolist() == ["unknown", "unknown"]
