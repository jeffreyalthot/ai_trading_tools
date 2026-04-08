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


class AISignalEngine:
    """
    Loads AI predictions from a CSV file and merges them into a Freqtrade dataframe.

    Expected CSV format:
    - date: candle timestamp in UTC (ISO format)
    - prediction: numeric signal in [-1, 1]
        * > 0 means bullish
        * < 0 means bearish
    """

    def __init__(self, config: AISignalConfig) -> None:
        self.config = config

    def load_signals(self) -> pd.DataFrame:
        if not self.config.signal_file.exists():
            return pd.DataFrame(columns=["date", "ai_prediction"])

        signals = pd.read_csv(self.config.signal_file)
        required = {self.config.timestamp_column, self.config.prediction_column}
        missing = required.difference(signals.columns)
        if missing:
            raise ValueError(f"Missing required signal columns: {sorted(missing)}")

        signals = signals[[self.config.timestamp_column, self.config.prediction_column]].copy()
        signals.columns = ["date", "ai_prediction"]
        signals["date"] = pd.to_datetime(signals["date"], utc=True)
        signals = signals.dropna(subset=["ai_prediction"]).sort_values("date")
        return signals

    def merge_into_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if dataframe.empty:
            return dataframe

        output = dataframe.copy()
        output["date"] = pd.to_datetime(output["date"], utc=True)
        signals = self.load_signals()

        if signals.empty:
            output["ai_prediction"] = 0.0
            return output

        output = output.merge(signals, on="date", how="left")
        output["ai_prediction"] = output["ai_prediction"].fillna(0.0)
        return output
