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
    - date (UTC candle timestamp)
    - prediction (float between -1 and 1)
    """

    can_short = False
    timeframe = "15m"

    minimal_roi = {"0": 0.06, "60": 0.03, "180": 0.0}
    stoploss = -0.1

    startup_candle_count = 50

    ai_buy_threshold = 0.25
    ai_sell_threshold = -0.25

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

        dataframe = self.ai_engine.merge_into_dataframe(dataframe)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema_fast"] > dataframe["ema_slow"])
                & (dataframe["rsi"] > 45)
                & (dataframe["macd"] > dataframe["macdsignal"])
                & (dataframe["ai_prediction"] >= self.ai_buy_threshold)
                & (dataframe["volume"] > 0)
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
            ),
            "exit_long",
        ] = 1

        return dataframe
