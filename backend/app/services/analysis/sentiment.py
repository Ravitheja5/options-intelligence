from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.services.analysis.metrics import OptionMetrics
from app.services.analysis.pcr import PCRMetrics
from app.services.analysis.support_resistance import (
    SupportResistanceMetrics,
)
from app.services.analysis.max_pain import (
    MaxPainMetrics,
)


@dataclass(frozen=True)
class MarketSentimentMetrics:
    sentiment: str
    confidence_score: Decimal
    reasons: list[str]


def calculate_market_sentiment(
    options: list[OptionMetrics],
    pcr: PCRMetrics | None,
    support_resistance: SupportResistanceMetrics | None,
    max_pain: MaxPainMetrics | None,
    underlying_price: Decimal | None,
) -> MarketSentimentMetrics:
    """
    Calculate overall market sentiment using:

    - PCR
    - OI buildup
    - Support / Resistance
    - Max Pain
    """

    score = 0
    reasons: list[str] = []

    # =========================================================
    # PCR ANALYSIS
    # =========================================================

    if pcr is not None and pcr.oi_pcr is not None:

        if pcr.oi_pcr >= Decimal("1.20"):
            score += 25
            reasons.append(
                "High Put-Call Ratio indicates bullish support"
            )

        elif pcr.oi_pcr >= Decimal("1.00"):
            score += 10
            reasons.append(
                "Put-Call Ratio indicates mildly bullish sentiment"
            )

        elif pcr.oi_pcr <= Decimal("0.70"):
            score -= 25
            reasons.append(
                "Low Put-Call Ratio indicates bearish pressure"
            )

        elif pcr.oi_pcr <= Decimal("0.90"):
            score -= 10
            reasons.append(
                "Put-Call Ratio indicates mildly bearish sentiment"
            )

    # =========================================================
    # OI BUILDUP ANALYSIS
    # =========================================================

    long_buildup = sum(
        1
        for option in options
        if option.oi_buildup == "LONG_BUILDUP"
    )

    short_covering = sum(
        1
        for option in options
        if option.oi_buildup == "SHORT_COVERING"
    )

    short_buildup = sum(
        1
        for option in options
        if option.oi_buildup == "SHORT_BUILDUP"
    )

    long_unwinding = sum(
        1
        for option in options
        if option.oi_buildup == "LONG_UNWINDING"
    )

    bullish_activity = (
        long_buildup
        + short_covering
    )

    bearish_activity = (
        short_buildup
        + long_unwinding
    )

    if bullish_activity > bearish_activity:
        score += 25
        reasons.append(
            "Bullish OI activity dominates the option chain"
        )

    elif bearish_activity > bullish_activity:
        score -= 25
        reasons.append(
            "Bearish OI activity dominates the option chain"
        )

    # =========================================================
    # SUPPORT / RESISTANCE ANALYSIS
    # =========================================================

    if (
        support_resistance is not None
        and underlying_price is not None
    ):

        support = support_resistance.support
        resistance = support_resistance.resistance

        if (
            support is not None
            and underlying_price >= support
        ):
            score += 10
            reasons.append(
                "Underlying price is holding above support"
            )

        if (
            resistance is not None
            and underlying_price >= resistance
        ):
            score += 15
            reasons.append(
                "Underlying price is testing or breaking resistance"
            )

    # =========================================================
    # MAX PAIN ANALYSIS
    # =========================================================

    if (
        max_pain is not None
        and max_pain.max_pain_strike is not None
        and underlying_price is not None
    ):

        distance = abs(
            underlying_price
            - max_pain.max_pain_strike
        )

        if distance == 0:
            score += 5
            reasons.append(
                "Underlying is trading at Max Pain"
            )

    # =========================================================
    # FINAL SENTIMENT
    # =========================================================

    if score >= 40:
        sentiment = "STRONG_BULLISH"

    elif score >= 15:
        sentiment = "BULLISH"

    elif score <= -40:
        sentiment = "STRONG_BEARISH"

    elif score <= -15:
        sentiment = "BEARISH"

    else:
        sentiment = "NEUTRAL"

    # =========================================================
    # CONFIDENCE SCORE
    # =========================================================

    confidence_score = min(
        Decimal(abs(score)),
        Decimal("100"),
    )

    if not reasons:
        reasons.append(
            "Insufficient directional signals available"
        )

    return MarketSentimentMetrics(
        sentiment=sentiment,
        confidence_score=confidence_score,
        reasons=reasons,
    )