"""AI trading tools package for Freqtrade strategies."""

__version__ = "57.0.0"

from ai_trading_tools.signal_engine import AISignalConfig, AISignalEngine
from ai_trading_tools.titan_platform import TitanExecutionPlatform, build_roadmap_catalog
from ai_trading_tools.titan_runtime import TitanRuntimeControlPlane

__all__ = [
    "AISignalConfig",
    "AISignalEngine",
    "TitanExecutionPlatform",
    "TitanRuntimeControlPlane",
    "build_roadmap_catalog",
]
