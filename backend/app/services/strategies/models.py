from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.services.analysis.metrics import OptionMetrics


@dataclass(frozen=True)
class StrategySignal:
    """
    Result produced by a strategy for one option.
    """

    strategy_name: str
    trading_symbol: str
    option_type: str
    strike_price: Decimal

    signal: str
    score: Decimal

    reason: str

    option: OptionMetrics
