from __future__ import annotations

from datetime import date

from app.core.database import SessionLocal
from app.services.analysis.service import AnalysisService
from app.services.strategies.base import Strategy
from app.services.strategies.implementations.oi_momentum import (
    OIMomentumStrategy,
)


class StrategyRunner:

    def __init__(self, strategies: list[Strategy] | None = None):
        self.strategies = strategies or [
            OIMomentumStrategy(),
        ]

    def run(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ):

        db = SessionLocal()

        try:
            analysis_service = AnalysisService(db)

            options = analysis_service.analyze_option_chain(
                underlying_symbol=underlying_symbol,
                expiry_date=expiry_date,
            )

            signals = []

            for option in options:
                for strategy in self.strategies:

                    signal = strategy.evaluate(option)

                    if signal is not None:
                        signals.append(signal)

            signals.sort(
                key=lambda signal: signal.score,
                reverse=True,
            )

            return signals

        finally:
            db.close()
