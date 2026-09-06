from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class SignalMetrics:
    signal: str
    confidence_score: Decimal
    reasons: list[str]


def calculate_option_signal(
    option_type: str,
    moneyness: str,
    oi_buildup: str,
    liquidity_score: Decimal,
) -> SignalMetrics:
    """
    Generate an intelligence signal for an option
    using OI buildup, moneyness, and liquidity.
    """

    score = 0
    reasons: list[str] = []

    option_type = option_type.upper()
    moneyness = moneyness.upper()
    oi_buildup = oi_buildup.upper()

    # -------------------------
    # OI BUILDUP ANALYSIS
    # -------------------------

    if oi_buildup == "LONG_BUILDUP":
        score += 40
        reasons.append("Long buildup detected")

    elif oi_buildup == "SHORT_COVERING":
        score += 30
        reasons.append("Short covering detected")

    elif oi_buildup == "SHORT_BUILDUP":
        score -= 40
        reasons.append("Short buildup detected")

    elif oi_buildup == "LONG_UNWINDING":
        score -= 30
        reasons.append("Long unwinding detected")

    # -------------------------
    # MONEYNESS ANALYSIS
    # -------------------------

    if moneyness == "ATM":
        score += 20
        reasons.append("ATM option")

    elif moneyness == "ITM":
        score += 10
        reasons.append("ITM option")

    elif moneyness == "OTM":
        score += 5
        reasons.append("OTM option")

    # -------------------------
    # LIQUIDITY ANALYSIS
    # -------------------------

    if liquidity_score >= Decimal("70"):
        score += 20
        reasons.append("High liquidity")

    elif liquidity_score >= Decimal("40"):
        score += 10
        reasons.append("Moderate liquidity")

    else:
        reasons.append("Low liquidity")

    # -------------------------
    # SIGNAL CLASSIFICATION
    # -------------------------

    if score >= 60:
        signal = "STRONG_BULLISH"

    elif score >= 25:
        signal = "BULLISH"

    elif score <= -60:
        signal = "STRONG_BEARISH"

    elif score <= -25:
        signal = "BEARISH"

    else:
        signal = "NEUTRAL"

    # -------------------------
    # CONFIDENCE SCORE
    # -------------------------

    confidence_score = min(
        Decimal(abs(score)),
        Decimal("100"),
    )

    return SignalMetrics(
        signal=signal,
        confidence_score=confidence_score,
        reasons=reasons,
    )
