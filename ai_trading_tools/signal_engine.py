from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class AISignalConfig:
    """Configuration for loading AI model signals."""

    signal_file: Path
    timestamp_column: str = "date"
    prediction_column: str = "prediction"
    regime_column: str = "regime"


class AISignalEngine:
    """
    Loads AI predictions from CSV files and merges them into a Freqtrade dataframe.

    Supported CSV formats:
    1) Single-model (legacy):
       - date, prediction

    2) Multi-model ensemble:
       - date, regime (optional), prediction_<model_a>, prediction_<model_b>, ...
       - weight_<model_a>, weight_<model_b>, ... (optional)

    Ensemble behavior:
    - If `prediction` exists, it is used directly as `ai_prediction`.
    - Otherwise, all `prediction_*` columns are aggregated.
    - If matching `weight_*` columns exist, a weighted mean is used.
      Missing or null weights are treated as zero.
    - Without weights, an arithmetic mean is used.
    """

    def __init__(self, config: AISignalConfig) -> None:
        self.config = config

    def load_signals(self) -> pd.DataFrame:
        if not self.config.signal_file.exists():
            return pd.DataFrame(columns=["date", "ai_prediction", "ai_regime"])

        signals = pd.read_csv(self.config.signal_file)
        if self.config.timestamp_column not in signals.columns:
            raise ValueError(f"Missing required signal column: {self.config.timestamp_column}")

        normalized = self._normalize_prediction_columns(signals)
        normalized = normalized.sort_values("date")
        return normalized

    def _normalize_prediction_columns(self, signals: pd.DataFrame) -> pd.DataFrame:
        working = signals.copy()
        working["date"] = pd.to_datetime(working[self.config.timestamp_column], utc=True)

        if self.config.prediction_column in working.columns:
            output = working[["date", self.config.prediction_column]].copy()
            output.columns = ["date", "ai_prediction"]
        else:
            prediction_cols = [c for c in working.columns if c.startswith("prediction_")]
            if not prediction_cols:
                raise ValueError(
                    "Missing prediction columns. Expected `prediction` or `prediction_*` columns."
                )

            prediction_frame = working[prediction_cols].apply(pd.to_numeric, errors="coerce")
            weight_cols = [f"weight_{c.replace('prediction_', '')}" for c in prediction_cols]
            has_all_weight_cols = all(col in working.columns for col in weight_cols)

            if has_all_weight_cols:
                weights = working[weight_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
                weighted_sum = (prediction_frame.fillna(0.0) * weights).sum(axis=1)
                total_weights = weights.sum(axis=1).replace(0.0, pd.NA)
                ensemble = (weighted_sum / total_weights).fillna(prediction_frame.mean(axis=1))
            else:
                ensemble = prediction_frame.mean(axis=1)

            output = pd.DataFrame({"date": working["date"], "ai_prediction": ensemble})

        output["ai_prediction"] = pd.to_numeric(output["ai_prediction"], errors="coerce")
        output = output.dropna(subset=["ai_prediction"]).copy()

        if self.config.regime_column in working.columns:
            output["ai_regime"] = working[self.config.regime_column].fillna("unknown").astype(str)
        else:
            output["ai_regime"] = "unknown"

        output["ai_prediction"] = output["ai_prediction"].clip(-1.0, 1.0)
        return output[["date", "ai_prediction", "ai_regime"]]

    def merge_into_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if dataframe.empty:
            return dataframe

        output = dataframe.copy()
        output["date"] = pd.to_datetime(output["date"], utc=True)
        signals = self.load_signals()

        if signals.empty:
            output["ai_prediction"] = 0.0
            output["ai_regime"] = "unknown"
            return output

        output = output.merge(signals, on="date", how="left")
        output["ai_prediction"] = output["ai_prediction"].fillna(0.0)
        output["ai_regime"] = output["ai_regime"].fillna("unknown")
        return output
