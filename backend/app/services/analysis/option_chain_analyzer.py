from decimal import Decimal

from app.services.analysis.metrics import OptionMetrics

class OptionChainAnalyzer:
    """
    Converts raw option-chain quotes into useful market intelligence.

    Current analysis:
    - ATM Strike
    - Total Call OI
    - Total Put OI
    - PCR
    - Support levels
    - Resistance levels
    - Basic market sentiment
    """

    def analyze(
        self,
       quotes: list[OptionMetrics],
        underlying_price: float | None,
    ) -> dict:

        if not quotes:
            return {
                "atm_strike": None,
                "underlying_price": underlying_price,
                "total_call_oi": 0,
                "total_put_oi": 0,
                "pcr": None,
                "support_levels": [],
                "resistance_levels": [],
                "sentiment": "NEUTRAL",
            }

        # =====================================================
        # ATM STRIKE
        # =====================================================

        strikes = sorted(
            {
                float(quote.strike_price)
                for quote in quotes
            }
        )

        atm_strike = None

        if underlying_price is not None and strikes:

            atm_strike = min(
                strikes,
                key=lambda strike: abs(
                    strike - underlying_price
                ),
            )

        # =====================================================
        # TOTAL OI
        # =====================================================

        total_call_oi = sum(
            quote.open_interest or 0
            for quote in quotes
            if quote.option_type == "CE"
        )

        total_put_oi = sum(
            quote.open_interest or 0
            for quote in quotes
            if quote.option_type == "PE"
        )

        # =====================================================
        # PCR
        # =====================================================

        pcr = None

        if total_call_oi > 0:

            pcr = round(
                total_put_oi / total_call_oi,
                4,
            )

        # =====================================================
        # SUPPORT LEVELS
        # Highest Put OI
        # =====================================================

        put_oi_by_strike = {}

        for quote in quotes:

            if quote.option_type != "PE":
                continue

            strike = float(quote.strike_price)

            put_oi_by_strike[strike] = (
                put_oi_by_strike.get(strike, 0)
                + (quote.open_interest or 0)
            )

        support_levels = [
            {
                "strike": strike,
                "open_interest": oi,
            }
            for strike, oi in sorted(
                put_oi_by_strike.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:3]
        ]

        # =====================================================
        # RESISTANCE LEVELS
        # Highest Call OI
        # =====================================================

        call_oi_by_strike = {}

        for quote in quotes:

            if quote.option_type != "CE":
                continue

            strike = float(quote.strike_price)

            call_oi_by_strike[strike] = (
                call_oi_by_strike.get(strike, 0)
                + (quote.open_interest or 0)
            )

        resistance_levels = [
            {
                "strike": strike,
                "open_interest": oi,
            }
            for strike, oi in sorted(
                call_oi_by_strike.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:3]
        ]

        # =====================================================
        # MARKET SENTIMENT
        # =====================================================

        sentiment = "NEUTRAL"

        if pcr is not None:

            if pcr >= 1.2:
                sentiment = "BULLISH"

            elif pcr <= 0.8:
                sentiment = "BEARISH"

        # =====================================================
        # FINAL RESPONSE
        # =====================================================

        return {
            "underlying_price": underlying_price,

            "atm_strike": atm_strike,

            "total_call_oi": total_call_oi,

            "total_put_oi": total_put_oi,

            "pcr": pcr,

            "support_levels": support_levels,

            "resistance_levels": resistance_levels,

            "sentiment": sentiment,
        }