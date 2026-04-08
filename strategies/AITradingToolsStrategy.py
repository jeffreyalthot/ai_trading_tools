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
    # Parametres par defaut (surchageables via config["ai_strategy_params"])
    ema_fast_period = 12
    ema_slow_period = 26
    rsi_period = 14
    atr_period = 14
    regime_window = 20
    trend_weight = 0.45
    momentum_weight = 0.35
    volatility_weight = 0.20

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        signal_path = Path("user_data/data/ai_signals.csv")
        self.ai_engine = AISignalEngine(AISignalConfig(signal_file=signal_path))
        self.ai_params = config.get("ai_strategy_params", {})

    def _param(self, key: str, default: float) -> float:
        value = self.ai_params.get(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        ema_fast_period = int(self._param("ema_fast_period", self.ema_fast_period))
        ema_slow_period = int(self._param("ema_slow_period", self.ema_slow_period))
        rsi_period = int(self._param("rsi_period", self.rsi_period))
        atr_period = int(self._param("atr_period", self.atr_period))
        regime_window = int(self._param("regime_window", self.regime_window))

        trend_weight = self._param("trend_weight", self.trend_weight)
        momentum_weight = self._param("momentum_weight", self.momentum_weight)
        volatility_weight = self._param("volatility_weight", self.volatility_weight)

        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=ema_fast_period)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=ema_slow_period)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=rsi_period)

        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]

        dataframe["atr"] = ta.ATR(dataframe, timeperiod=atr_period)
        dataframe["atr_pct"] = (dataframe["atr"] / dataframe["close"]).fillna(0.0)

        dataframe = self.ai_engine.merge_into_dataframe(dataframe)
        dataframe["ai_conviction"] = dataframe["ai_prediction"].abs()

        # L'IA derive une "lecture du marche" a partir des parametres,
        # au lieu d'utiliser directement des seuils statiques.
        dataframe["trend_strength"] = (
            (dataframe["ema_fast"] - dataframe["ema_slow"]) / dataframe["close"]
        ).fillna(0.0)
        dataframe["momentum_strength"] = ((dataframe["rsi"] - 50.0) / 50.0).fillna(0.0)
        dataframe["volatility_penalty"] = (
            dataframe["atr_pct"] / max(self._param("max_atr_pct", self.max_atr_pct), 1e-9)
        ).clip(lower=0.0, upper=2.0)
        dataframe["market_regime_score"] = (
            trend_weight * dataframe["trend_strength"]
            + momentum_weight * dataframe["momentum_strength"]
            - volatility_weight * dataframe["volatility_penalty"]
        ).rolling(regime_window, min_periods=1).mean()

        # Detection des patterns de declenchement (buy/sell pressure) pour contexte IA.
        dataframe["buy_pattern_trigger"] = (
            ((dataframe["ema_fast"] > dataframe["ema_slow"]) & (dataframe["macd"] > dataframe["macdsignal"])).astype(float)
            * (dataframe["rsi"] > 50).astype(float)
        )
        dataframe["sell_pattern_trigger"] = (
            ((dataframe["ema_fast"] < dataframe["ema_slow"]) & (dataframe["macd"] < dataframe["macdsignal"])).astype(float)
            * (dataframe["rsi"] < 50).astype(float)
        )
        dataframe["ai_context_bias"] = (
            dataframe["buy_pattern_trigger"].rolling(regime_window, min_periods=1).mean()
            - dataframe["sell_pattern_trigger"].rolling(regime_window, min_periods=1).mean()
        ).fillna(0.0)

        dataframe["ai_dynamic_buy_threshold"] = (
            self._param("ai_buy_threshold", self.ai_buy_threshold)
            + dataframe["market_regime_score"].clip(-0.2, 0.2) * 0.25
            + dataframe["ai_context_bias"].clip(-0.3, 0.3) * 0.15
        )
        dataframe["ai_dynamic_sell_threshold"] = (
            self._param("ai_sell_threshold", self.ai_sell_threshold)
            + dataframe["market_regime_score"].clip(-0.2, 0.2) * 0.25
            + dataframe["ai_context_bias"].clip(-0.3, 0.3) * 0.15
        )

        dataframe["risk_off"] = (
            (dataframe["atr_pct"] > self._param("max_atr_pct", self.max_atr_pct))
            | (dataframe["volume"] <= 0)
        ).astype(int)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema_fast"] > dataframe["ema_slow"])
                & (dataframe["rsi"] > 45)
                & (dataframe["macd"] > dataframe["macdsignal"])
                & (dataframe["ai_prediction"] >= dataframe["ai_dynamic_buy_threshold"])
                & (dataframe["ai_conviction"] >= self._param("min_ai_conviction", self.min_ai_conviction))
                & (dataframe["market_regime_score"] > self._param("entry_regime_floor", -0.05))
                & (dataframe["ai_context_bias"] > self._param("entry_context_floor", -0.10))
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
                | (dataframe["ai_prediction"] <= dataframe["ai_dynamic_sell_threshold"])
                | (dataframe["ai_prediction"] <= self._param("hard_exit_ai", self.hard_exit_ai))
                | (dataframe["market_regime_score"] < self._param("exit_regime_ceiling", -0.20))
                | (dataframe["ai_context_bias"] < self._param("exit_context_ceiling", -0.25))
                | (dataframe["risk_off"] == 1)
            ),
            "exit_long",
        ] = 1

        return dataframe
