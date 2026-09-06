from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.services.analysis.sentiment import (
    MarketSentimentMetrics,
)

from app.services.analysis.pcr import PCRMetrics

from app.services.analysis.support_resistance import (
    SupportResistanceMetrics,
)



@dataclass(frozen=True)
class TradingRecommendation:
    recommendation: str
    confidence_score: Decimal
    reasons: list[str]


def calculate_trading_recommendation(
    market_sentiment: MarketSentimentMetrics | None,
    pcr: PCRMetrics | None,
    support_resistance: SupportResistanceMetrics | None,
    underlying_price: Decimal | None,
) -> TradingRecommendation:

    score = 0
    reasons: list[str] = []

    # ==========================================
    # MARKET SENTIMENT
    # ==========================================

    if market_sentiment is not None:

        sentiment = market_sentiment.sentiment

        if sentiment == "STRONG_BULLISH":
            score += 40
            reasons.append(
                "Overall market sentiment is strongly bullish"
            )

        elif sentiment == "BULLISH":
            score += 20
            reasons.append(
                "Overall market sentiment is bullish"
            )

        elif sentiment == "STRONG_BEARISH":
            score -= 40
            reasons.append(
                "Overall market sentiment is strongly bearish"
            )

        elif sentiment == "BEARISH":
            score -= 20
            reasons.append(
                "Overall market sentiment is bearish"
            )

        else:
            reasons.append(
                "Overall market sentiment is neutral"
            )

    # ==========================================
    # PCR ANALYSIS
    # ==========================================

    if pcr is not None and pcr.oi_pcr is not None:

        if pcr.oi_pcr >= Decimal("1.20"):
            score += 15
            reasons.append(
                "High PCR provides bullish support"
            )

        elif pcr.oi_pcr <= Decimal("0.70"):
            score -= 15
            reasons.append(
                "Low PCR indicates bearish pressure"
            )

    # ==========================================
    # SUPPORT / RESISTANCE
    # ==========================================

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
                "Price is holding above the identified support"
            )

        if (
            resistance is not None
            and underlying_price >= resistance
        ):
            score += 10
            reasons.append(
                "Price is testing or trading above resistance"
            )

    # ==========================================
    # FINAL RECOMMENDATION
    # ==========================================

    if score >= 45:
        recommendation = "STRONG_BUY"

    elif score >= 20:
        recommendation = "BUY"

    elif score <= -45:
        recommendation = "STRONG_SELL"

    elif score <= -20:
        recommendation = "SELL"

    else:
        recommendation = "HOLD"

    confidence_score = min(
        Decimal(abs(score)),
        Decimal("100"),
    )

    if not reasons:
        reasons.append(
            "Insufficient signals available for a directional recommendation"
        )

    return TradingRecommendation(
        recommendation=recommendation,
        confidence_score=confidence_score,
        reasons=reasons,
    )
def get_trading_recommendation(
    self,
    underlying_symbol: str,
    expiry_date: date | None = None,
) -> TradingRecommendation:

    pcr = self.get_pcr_metrics(
        underlying_symbol=underlying_symbol,
        expiry_date=expiry_date,
    )

    support_resistance = self.get_support_resistance(
        underlying_symbol=underlying_symbol,
        expiry_date=expiry_date,
    )

    market_sentiment = self.get_market_sentiment(
        underlying_symbol=underlying_symbol,
        expiry_date=expiry_date,
    )

    options = self.analyze_option_chain(
        underlying_symbol=underlying_symbol,
        expiry_date=expiry_date,
    )

    underlying_price = None

    if options:
        underlying_price = options[0].underlying_price

    return calculate_trading_recommendation(
        market_sentiment=market_sentiment,
        pcr=pcr,
        support_resistance=support_resistance,
        underlying_price=underlying_price,
    )