from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analysis.service import AnalysisService


router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)


@router.get("/option-chain")
def analyze_option_chain(
    underlying_symbol: str,
    expiry_date: date,
    db: Session = Depends(get_db),
):
    """
    Complete Option Chain Intelligence Analysis.

    Includes:
    - Underlying price
    - ATM strike
    - ITM / ATM / OTM
    - Price analysis
    - OI analysis
    - OI Buildup
    - Option Signal
    - PCR
    - Support / Resistance
    - Max Pain
    - Market Sentiment
    - IV
    - Greeks
    """

    try:
        analysis_service = AnalysisService(db)

        # ====================================================
        # OPTION CHAIN
        # ====================================================

        options = analysis_service.analyze_option_chain(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        # ====================================================
        # PCR
        # ====================================================

        pcr = analysis_service.get_pcr_metrics(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        # ====================================================
        # SUPPORT / RESISTANCE
        # ====================================================

        support_resistance = (
            analysis_service.get_support_resistance(
                underlying_symbol=underlying_symbol,
                expiry_date=expiry_date,
            )
        )

        # ====================================================
        # MAX PAIN
        # ====================================================

        max_pain = analysis_service.get_max_pain(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        # ====================================================
        # MARKET SENTIMENT
        # ====================================================

        market_sentiment = (
            analysis_service.get_market_sentiment(
                underlying_symbol=underlying_symbol,
                expiry_date=expiry_date,
            )
        )

        # ====================================================
        # NO OPTIONS
        # ====================================================

        if not options:
            return {
                "success": True,
                "data": {
                    "underlying_symbol": underlying_symbol.upper(),
                    "expiry_date": expiry_date,
                    "contracts_count": 0,
                    "underlying_price": None,
                    "atm_strike": None,
                    "pcr": None,
                    "support_resistance": None,
                    "max_pain": None,
                    "market_sentiment": None,
                    "options": [],
                },
            }

        underlying_price = options[0].underlying_price
        atm_strike = options[0].atm_strike

        # ====================================================
        # SUCCESS RESPONSE
        # ====================================================

        return {
            "success": True,
            "data": {
                "underlying_symbol": underlying_symbol.upper(),
                "expiry_date": expiry_date,
                "contracts_count": len(options),

                # ====================================================
                # UNDERLYING
                # ====================================================

                "underlying_price": (
                    float(underlying_price)
                    if underlying_price is not None
                    else None
                ),

                "atm_strike": (
                    float(atm_strike)
                    if atm_strike is not None
                    else None
                ),

                # ====================================================
                # PCR
                # ====================================================

                "pcr": (
                    {
                        "total_call_oi": pcr.total_call_oi,
                        "total_put_oi": pcr.total_put_oi,

                        "total_call_volume": (
                            pcr.total_call_volume
                        ),

                        "total_put_volume": (
                            pcr.total_put_volume
                        ),

                        "oi_pcr": (
                            float(pcr.oi_pcr)
                            if pcr.oi_pcr is not None
                            else None
                        ),

                        "volume_pcr": (
                            float(pcr.volume_pcr)
                            if pcr.volume_pcr is not None
                            else None
                        ),
                    }
                    if pcr is not None
                    else None
                ),

                # ====================================================
                # SUPPORT / RESISTANCE
                # ====================================================

                "support_resistance": (
                    {
                        "support": (
                            float(support_resistance.support)
                            if support_resistance.support
                            is not None
                            else None
                        ),

                        "resistance": (
                            float(
                                support_resistance.resistance
                            )
                            if support_resistance.resistance
                            is not None
                            else None
                        ),

                        "top_supports": [
                            float(level)
                            for level
                            in support_resistance.top_supports
                        ],

                        "top_resistances": [
                            float(level)
                            for level
                            in support_resistance.top_resistances
                        ],
                    }
                    if support_resistance is not None
                    else None
                ),

                # ====================================================
                # MAX PAIN
                # ====================================================

                "max_pain": (
                    {
                        "max_pain_strike": (
                            float(max_pain.max_pain_strike)
                            if max_pain.max_pain_strike
                            is not None
                            else None
                        ),

                        "minimum_pain": (
                            float(max_pain.minimum_pain)
                            if max_pain.minimum_pain
                            is not None
                            else None
                        ),
                    }
                    if max_pain is not None
                    else None
                ),

                # ====================================================
                # MARKET SENTIMENT
                # ====================================================

                "market_sentiment": (
                    {
                        "sentiment": (
                            market_sentiment.sentiment
                        ),

                        "confidence_score": float(
                            market_sentiment.confidence_score
                        ),

                        "reasons": (
                            market_sentiment.reasons
                        ),
                    }
                    if market_sentiment is not None
                    else None
                ),

                # ====================================================
                # OPTIONS
                # ====================================================

                "options": [
                    {
                        # --------------------------------------------
                        # Contract
                        # --------------------------------------------

                        "trading_symbol": (
                            option.trading_symbol
                        ),

                        "option_type": option.option_type,

                        "strike_price": float(
                            option.strike_price
                        ),

                        # --------------------------------------------
                        # Underlying / ATM
                        # --------------------------------------------

                        "underlying_price": (
                            float(option.underlying_price)
                            if option.underlying_price
                            is not None
                            else None
                        ),

                        "atm_strike": (
                            float(option.atm_strike)
                            if option.atm_strike is not None
                            else None
                        ),

                        # --------------------------------------------
                        # Moneyness
                        # --------------------------------------------

                        "moneyness": option.moneyness,

                        # --------------------------------------------
                        # Price
                        # --------------------------------------------

                        "ltp": (
                            float(option.last_price)
                            if option.last_price is not None
                            else None
                        ),

                        "previous_price": (
                            float(option.previous_price)
                            if option.previous_price
                            is not None
                            else None
                        ),

                        "price_change": (
                            float(option.price_change)
                            if option.price_change
                            is not None
                            else None
                        ),

                        "price_change_percent": (
                            float(option.price_change_percent)
                            if option.price_change_percent
                            is not None
                            else None
                        ),

                        # --------------------------------------------
                        # Volume
                        # --------------------------------------------

                        "volume": option.volume,

                        # --------------------------------------------
                        # Open Interest
                        # --------------------------------------------

                        "open_interest": (
                            option.open_interest
                        ),

                        "previous_open_interest": (
                            option.previous_open_interest
                        ),

                        "oi_change": option.oi_change,

                        "oi_change_percent": (
                            float(option.oi_change_percent)
                            if option.oi_change_percent
                            is not None
                            else None
                        ),

                        # --------------------------------------------
                        # OI Buildup
                        # --------------------------------------------

                        "oi_buildup": option.oi_buildup,

                        # --------------------------------------------
                        # Signal Intelligence
                        # --------------------------------------------

                       # --------------------------------------------
                        # Signal Intelligence
                        # --------------------------------------------

                        "signal": option.trading_signal,

                        "signal_score": option.signal_score,

                        "signal_reasons": option.signal_reasons,

                        # --------------------------------------------
                        # Implied Volatility
                        # --------------------------------------------

                        "implied_volatility": (
                            float(option.implied_volatility)
                            if option.implied_volatility
                            is not None
                            else None
                        ),

                        # --------------------------------------------
                        # Greeks
                        # --------------------------------------------

                        "delta": (
                            float(option.delta)
                            if option.delta is not None
                            else None
                        ),

                        "gamma": (
                            float(option.gamma)
                            if option.gamma is not None
                            else None
                        ),

                        "theta": (
                            float(option.theta)
                            if option.theta is not None
                            else None
                        ),

                        "vega": (
                            float(option.vega)
                            if option.vega is not None
                            else None
                        ),

                        # --------------------------------------------
                        # Strike Analysis
                        # --------------------------------------------

                        "strike_distance": (
                            float(option.strike_distance)
                            if option.strike_distance
                            is not None
                            else None
                        ),

                        "strike_distance_percent": (
                            float(
                                option.strike_distance_percent
                            )
                            if option.strike_distance_percent
                            is not None
                            else None
                        ),

                        # --------------------------------------------
                        # Scores
                        # --------------------------------------------

                        "liquidity_score": float(
                            option.liquidity_score
                        ),

                        "data_quality_score": float(
                            option.data_quality_score
                        ),
                    }
                    for option in options
                ],
            },
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )