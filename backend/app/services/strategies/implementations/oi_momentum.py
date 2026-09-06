from __future__ import annotations

from decimal import Decimal

from app.services.analysis.metrics import OptionMetrics
from app.services.strategies.base import Strategy
from app.services.strategies.models import StrategySignal


class OIMomentumStrategy(Strategy):
    """
    Strategy #1:
    Open Interest + Price Momentum
    """

    name = "OI + Price Momentum"

    MIN_LIQUIDITY_SCORE = Decimal("10")
    MIN_DATA_QUALITY_SCORE = Decimal("80")

    def evaluate(
        self,
        option: OptionMetrics,
    ) -> StrategySignal | None:

        print("\n========================================")
        print("CHECKING OPTION")
        print("========================================")
        print("Trading Symbol:", option.trading_symbol)
        print("Option Type:", option.option_type)
        print("Strike Price:", option.strike_price)
        print("Last Price:", option.last_price)
        print("Volume:", option.volume)
        print("Open Interest:", option.open_interest)
        print("OI Change:", option.oi_change)
        print("Liquidity Score:", option.liquidity_score)
        print("Data Quality Score:", option.data_quality_score)
        print("Delta:", option.delta)

        # -----------------------------
        # BASIC DATA VALIDATION
        # -----------------------------

        if option.last_price is None:
            print("❌ REJECTED → last_price is None")
            return None

        if option.open_interest is None:
            print("❌ REJECTED → open_interest is None")
            return None

        if option.oi_change is None:
            print("❌ REJECTED → oi_change is None")
            return None

        if option.volume is None:
            print("❌ REJECTED → volume is None")
            return None

        # -----------------------------
        # DATA QUALITY CHECK
        # -----------------------------

        if option.data_quality_score < self.MIN_DATA_QUALITY_SCORE:
            print(
                f"❌ REJECTED → data_quality_score "
                f"{option.data_quality_score} < "
                f"{self.MIN_DATA_QUALITY_SCORE}"
            )
            return None

        # -----------------------------
        # LIQUIDITY CHECK
        # -----------------------------

        if option.liquidity_score < self.MIN_LIQUIDITY_SCORE:
            print(
                f"❌ REJECTED → liquidity_score "
                f"{option.liquidity_score} < "
                f"{self.MIN_LIQUIDITY_SCORE}"
            )
            return None

        # -----------------------------
        # PRICE CHECK
        # -----------------------------

        if option.last_price <= 0:
            print("❌ REJECTED → last_price <= 0")
            return None

        # -----------------------------
        # OI MOMENTUM CHECK
        # -----------------------------

        if option.oi_change <= 0:
            print(
                f"❌ REJECTED → oi_change "
                f"{option.oi_change} <= 0"
            )
            return None

        option_type = option.option_type.upper()

        # -----------------------------
        # DELTA CHECK
        # -----------------------------

        if option.delta is None:
            print("❌ REJECTED → delta is None")
            return None

        delta_strength = abs(option.delta)

        if delta_strength < Decimal("0.20"):
            print(
                f"❌ REJECTED → delta strength "
                f"{delta_strength} < 0.20"
            )
            return None

        # ========================================
        # OPTION PASSED ALL FILTERS
        # ========================================

        print("✅ PASSED ALL FILTERS")

        # -----------------------------
        # BASE SCORE
        # -----------------------------

        score = Decimal("50")

        # -----------------------------
        # OI PARTICIPATION SCORE
        # -----------------------------

        if option.open_interest > 0:

            oi_ratio = (
                Decimal(option.oi_change)
                / Decimal(option.open_interest)
            )

            print("OI Ratio:", oi_ratio)

            if oi_ratio >= Decimal("0.10"):
                score += Decimal("20")
                print("➕ OI Score: +20")

            elif oi_ratio >= Decimal("0.05"):
                score += Decimal("10")
                print("➕ OI Score: +10")

        # -----------------------------
        # LIQUIDITY SCORE
        # -----------------------------

        liquidity_contribution = min(
            option.liquidity_score * Decimal("0.20"),
            Decimal("20"),
        )

        score += liquidity_contribution

        print(
            "➕ Liquidity Score:",
            liquidity_contribution,
        )

        # -----------------------------
        # DELTA SCORE
        # -----------------------------

        delta_contribution = min(
            delta_strength * Decimal("10"),
            Decimal("10"),
        )

        score += delta_contribution

        print(
            "➕ Delta Score:",
            delta_contribution,
        )

        # -----------------------------
        # FINAL SCORE
        # -----------------------------

        score = min(score, Decimal("100"))

        print("🎯 FINAL SCORE:", score)

        # -----------------------------
        # SIGNAL TYPE
        # -----------------------------

        if option_type == "CE":

            signal = "BUY CALL"

            reason = (
                "Positive OI change with sufficient liquidity "
                "and bullish option sensitivity."
            )

        elif option_type == "PE":

            signal = "BUY PUT"

            reason = (
                "Positive OI change with sufficient liquidity "
                "and bearish option sensitivity."
            )

        else:

            print(
                f"❌ REJECTED → Unknown option type: "
                f"{option_type}"
            )

            return None

        print("🚀 SIGNAL GENERATED")
        print("Signal:", signal)
        print("Score:", score)

        return StrategySignal(
            strategy_name=self.name,
            trading_symbol=option.trading_symbol,
            option_type=option.option_type,
            strike_price=option.strike_price,
            signal=signal,
            score=score.quantize(Decimal("0.01")),
            reason=reason,
            option=option,
        )