from __future__ import annotations

from pathlib import Path

import talib.abstract as ta
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

from ai_trading_tools.signal_engine import AISignalConfig, AISignalEngine


class AITradingToolsStrategy(IStrategy):
    """
    Freqtrade strategy compatible with AI-generated prediction signals.

    Place a CSV file at user_data/data/ai_signals.csv with columns:
    - Legacy mode: date, prediction
    - Ensemble mode: date, prediction_model_a, prediction_model_b, ..., weight_model_a, ...
    - Optional: regime
    """

    can_short = False
    timeframe = "15m"

    minimal_roi = {"0": 0.06, "60": 0.03, "180": 0.0}
    stoploss = -0.1

    startup_candle_count = 80

    ai_buy_threshold = 0.25
    ai_sell_threshold = -0.25

    # Risk engine settings
    max_atr_pct = 0.05
    min_ai_conviction = 0.18
    hard_exit_ai = -0.60

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        signal_path = Path("user_data/data/ai_signals.csv")
        self.ai_engine = AISignalEngine(AISignalConfig(signal_file=signal_path))

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=12)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=26)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)

        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]

        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_pct"] = (dataframe["atr"] / dataframe["close"]).fillna(0.0)

        dataframe = self.ai_engine.merge_into_dataframe(dataframe)
        dataframe["ai_conviction"] = dataframe["ai_prediction"].abs()

        dataframe["risk_off"] = (
            (dataframe["atr_pct"] > self.max_atr_pct) | (dataframe["volume"] <= 0)
        ).astype(int)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema_fast"] > dataframe["ema_slow"])
                & (dataframe["rsi"] > 45)
                & (dataframe["macd"] > dataframe["macdsignal"])
                & (dataframe["ai_prediction"] >= self.ai_buy_threshold)
                & (dataframe["ai_conviction"] >= self.min_ai_conviction)
                & (dataframe["risk_off"] == 0)
            ),
            "enter_long",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema_fast"] < dataframe["ema_slow"])
                | (dataframe["rsi"] < 40)
                | (dataframe["ai_prediction"] <= self.ai_sell_threshold)
                | (dataframe["ai_prediction"] <= self.hard_exit_ai)
                | (dataframe["risk_off"] == 1)
            ),
            "exit_long",
        ] = 1

        return dataframe
