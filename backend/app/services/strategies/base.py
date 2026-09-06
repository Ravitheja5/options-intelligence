from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.analysis.metrics import OptionMetrics
from app.services.strategies.models import StrategySignal


class Strategy(ABC):
    """
    Base interface for every trading strategy.

    Every future strategy must implement evaluate().
    """

    name: str = "base"

    @abstractmethod
    def evaluate(
        self,
        option: OptionMetrics,
    ) -> StrategySignal | None:
        """
        Evaluate one option.

        Return:
            StrategySignal -> when the option qualifies.
            None           -> when it does not qualify.
        """
        raise NotImplementedError
