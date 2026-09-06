from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.services.analysis.metrics import OptionMetrics


@dataclass(frozen=True)
class TradingSignalMetrics:
    signal: str
    score: int
    reasons: list[str]


def calculate_trading_signal(
    option: OptionMetrics,
) -> TradingSignalMetrics:
    """
    Calculate a directional trading signal for an individual option.

    Signals:
    - STRONG_BUY
    - BUY
    - NEUTRAL
    - SELL
    - STRONG_SELL
    - AVOID

    Important:
    Liquidity and data quality are treated primarily as
    tradeability filters, not bullish signals.
    """

    score = 0
    reasons: list[str] = []

    # =========================================================
    # HARD TRADEABILITY FILTERS
    # =========================================================

    if option.data_quality_score < Decimal("50"):
        return TradingSignalMetrics(
            signal="AVOID",
            score=0,
            reasons=[
                "Insufficient market data quality"
            ],
        )

    if option.liquidity_score < Decimal("20"):
        return TradingSignalMetrics(
            signal="AVOID",
            score=0,
            reasons=[
                "Low liquidity"
            ],
        )

    # =========================================================
    # OPTION SUITABILITY FILTER
    # =========================================================

    is_far_otm = (
        option.moneyness == "OTM"
        and option.strike_distance_percent is not None
        and option.strike_distance_percent >= Decimal("3")
    )

    has_very_low_delta = (
        option.delta is not None
        and abs(option.delta) < Decimal("0.10")
    )

    if is_far_otm and has_very_low_delta:
        return TradingSignalMetrics(
            signal="AVOID",
            score=-30,
            reasons=[
                "Far OTM option",
                "Very low delta option",
                "Poor probability for directional trading",
            ],
        )

    # =========================================================
    # OI BUILDUP ANALYSIS
    # =========================================================

    if option.oi_buildup == "LONG_BUILDUP":
        score += 30
        reasons.append("Long buildup detected")

    elif option.oi_buildup == "SHORT_COVERING":
        score += 20
        reasons.append("Short covering detected")

    elif option.oi_buildup == "SHORT_BUILDUP":
        score -= 30
        reasons.append("Short buildup detected")

    elif option.oi_buildup == "LONG_UNWINDING":
        score -= 20
        reasons.append("Long unwinding detected")

    # =========================================================
    # PRICE MOMENTUM
    # =========================================================

    if option.price_change_percent is not None:

        if option.price_change_percent >= Decimal("5"):
            score += 25
            reasons.append(
                "Strong positive price momentum"
            )

        elif option.price_change_percent > Decimal("1"):
            score += 10
            reasons.append(
                "Positive price momentum"
            )

        elif option.price_change_percent <= Decimal("-5"):
            score -= 25
            reasons.append(
                "Strong negative price momentum"
            )

        elif option.price_change_percent < Decimal("-1"):
            score -= 10
            reasons.append(
                "Negative price momentum"
            )

    # =========================================================
    # MONEYNESS ANALYSIS
    # =========================================================

    if option.moneyness == "ATM":
        score += 10
        reasons.append("ATM option")

    elif option.moneyness == "ITM":
        score += 5
        reasons.append("ITM option")

    elif option.moneyness == "OTM":

        if (
            option.strike_distance_percent is not None
            and option.strike_distance_percent
            >= Decimal("3")
        ):
            score -= 15
            reasons.append(
                "Far OTM option"
            )

    # =========================================================
    # DELTA ANALYSIS
    # =========================================================

    if option.delta is not None:

        absolute_delta = abs(option.delta)

        if absolute_delta < Decimal("0.10"):
            score -= 15
            reasons.append(
                "Very low delta option"
            )

        elif absolute_delta >= Decimal("0.40"):
            score += 5
            reasons.append(
                "Strong option sensitivity"
            )

    # =========================================================
    # LIQUIDITY QUALITY CONFIRMATION
    # =========================================================

    if option.liquidity_score >= Decimal("70"):
        reasons.append("High liquidity")

    elif option.liquidity_score >= Decimal("40"):
        reasons.append("Moderate liquidity")

    # =========================================================
    # DATA QUALITY CONFIRMATION
    # =========================================================

    if option.data_quality_score >= Decimal("80"):
        reasons.append("High quality market data")

    # =========================================================
    # FINAL SIGNAL
    # =========================================================

    if score >= 50:
        signal = "STRONG_BUY"

    elif score >= 25:
        signal = "BUY"

    elif score <= -50:
        signal = "STRONG_SELL"

    elif score <= -25:
        signal = "SELL"

    else:
        signal = "NEUTRAL"

    if score == 0:
        reasons.insert(
            0,
            "No strong directional signal available",
        )

    return TradingSignalMetrics(
        signal=signal,
        score=score,
        reasons=reasons,
    )