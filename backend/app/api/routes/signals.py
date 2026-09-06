from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query

from app.services.strategies.runner import StrategyRunner


router = APIRouter(
    prefix="/signals",
    tags=["Trading Signals"],
)


@router.get("")
def get_trading_signals(
    underlying_symbol: str = Query(
        default="NIFTY",
        description="Underlying symbol",
    ),
    expiry_date: date | None = Query(
        default=None,
        description="Option expiry date",
    ),
):

    runner = StrategyRunner()

    signals = runner.run(
        underlying_symbol=underlying_symbol,
        expiry_date=expiry_date,
    )

    return {
        "success": True,
        "underlying_symbol": underlying_symbol.upper(),
        "total_signals": len(signals),
        "signals": [
            {
                "strategy_name": signal.strategy_name,
                "trading_symbol": signal.trading_symbol,
                "option_type": signal.option_type,
                "strike_price": float(signal.strike_price),
                "signal": signal.signal,
                "score": float(signal.score),
                "reason": signal.reason,

                "last_price": (
                    float(signal.option.last_price)
                    if signal.option.last_price is not None
                    else None
                ),

                "volume": signal.option.volume,

                "open_interest": signal.option.open_interest,

                "oi_change": signal.option.oi_change,

                "liquidity_score": float(
                    signal.option.liquidity_score
                ),

                "moneyness": signal.option.moneyness,
            }
            for signal in signals
        ],
    }
