from datetime import date
import traceback

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.option_chain_snapshot import OptionChainSnapshot
from app.models.option_contract import OptionContract
from app.models.underlying import Underlying
from app.services.market_pipeline import MarketPipeline


router = APIRouter(
    prefix="/market",
    tags=["Market"],
)


@router.post("/run")
async def run_market_pipeline(
    underlying_symbol: str = "NIFTY",
    expiry_date: date | None = None,
):
    if expiry_date is None:
        expiry_date = date(2026, 9, 8)

    try:
        pipeline = MarketPipeline()

        result = await pipeline.run(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        return {
            "success": True,
            "data": result,
        }

    except Exception as error:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.get("/data")
def get_market_data(
    underlying_symbol: str = "NIFTY",
    expiry_date: date | None = None,
    db: Session = Depends(get_db),
):
    symbol = underlying_symbol.upper().strip()

    latest_snapshots = (
        select(
            OptionChainSnapshot.option_contract_id.label(
                "option_contract_id"
            ),
            func.max(
                OptionChainSnapshot.snapshot_time
            ).label(
                "latest_snapshot_time"
            ),
        )
        .group_by(
            OptionChainSnapshot.option_contract_id
        )
        .subquery()
    )

    query = (
        select(
            OptionChainSnapshot,
            OptionContract,
        )
        .join(
            OptionContract,
            OptionChainSnapshot.option_contract_id
            == OptionContract.id,
        )
        .join(
            Underlying,
            OptionContract.underlying_id
            == Underlying.id,
        )
        .join(
            latest_snapshots,
            and_(
                OptionChainSnapshot.option_contract_id
                == latest_snapshots.c.option_contract_id,

                OptionChainSnapshot.snapshot_time
                == latest_snapshots.c.latest_snapshot_time,
            ),
        )
        .where(
            Underlying.symbol == symbol
        )
    )

    if expiry_date:
        query = query.where(
            OptionContract.expiry_date == expiry_date
        )

    query = query.order_by(
        OptionContract.strike_price,
        OptionContract.option_type,
    )

    rows = db.execute(query).all()

    if not rows:
        return {
            "success": True,
            "data": {
                "underlying_symbol": symbol,
                "total_options": 0,
                "underlying_price": None,
                "last_updated": None,
                "option_chain": [],
            },
        }

    option_chain = []

    latest_underlying_price = None
    latest_snapshot_time = None

    for snapshot, contract in rows:

        latest_underlying_price = (
            float(snapshot.underlying_price)
            if snapshot.underlying_price is not None
            else None
        )

        latest_snapshot_time = (
            snapshot.snapshot_time.isoformat()
            if snapshot.snapshot_time
            else None
        )

        option_chain.append(
            {
                "option_contract_id": contract.id,
                "trading_symbol": contract.trading_symbol,

                "expiry_date": (
                    contract.expiry_date.isoformat()
                    if contract.expiry_date
                    else None
                ),

                "strike_price": float(contract.strike_price),

                "option_type": contract.option_type,

                "last_price": (
                    float(snapshot.last_price)
                    if snapshot.last_price is not None
                    else None
                ),

                "bid_price": (
                    float(snapshot.bid_price)
                    if snapshot.bid_price is not None
                    else None
                ),

                "ask_price": (
                    float(snapshot.ask_price)
                    if snapshot.ask_price is not None
                    else None
                ),

                "volume": snapshot.volume,

                "open_interest": snapshot.open_interest,

                "oi_change": snapshot.oi_change,

                "implied_volatility": (
                    float(snapshot.implied_volatility)
                    if snapshot.implied_volatility is not None
                    else None
                ),

                "delta": (
                    float(snapshot.delta)
                    if snapshot.delta is not None
                    else None
                ),

                "gamma": (
                    float(snapshot.gamma)
                    if snapshot.gamma is not None
                    else None
                ),

                "theta": (
                    float(snapshot.theta)
                    if snapshot.theta is not None
                    else None
                ),

                "vega": (
                    float(snapshot.vega)
                    if snapshot.vega is not None
                    else None
                ),

                "snapshot_time": (
                    snapshot.snapshot_time.isoformat()
                    if snapshot.snapshot_time
                    else None
                ),
            }
        )

    return {
        "success": True,
        "data": {
            "underlying_symbol": symbol,
            "underlying_price": latest_underlying_price,
            "last_updated": latest_snapshot_time,
            "total_options": len(option_chain),
            "option_chain": option_chain,
        },
    }