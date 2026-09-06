from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.option_chain_snapshot import OptionChainSnapshot
from app.models.option_contract import OptionContract


def save_option_snapshot(
    db: Session,
    trading_symbol: str,
    underlying_price: Decimal,
    last_price: Decimal,
    volume: int | None,
    open_interest: int | None,
    oi_change: int | None,
    implied_volatility: Decimal | None,
    delta: Decimal | None,
    gamma: Decimal | None,
    theta: Decimal | None,
    vega: Decimal | None,
    bid_price: Decimal | None = None,
    ask_price: Decimal | None = None,
) -> OptionChainSnapshot | None:

    option_contract = (
        db.query(OptionContract)
        .filter(
            OptionContract.trading_symbol == trading_symbol
        )
        .first()
    )

    if option_contract is None:
        return None

    snapshot = OptionChainSnapshot(
        option_contract_id=option_contract.id,

        snapshot_time=datetime.now(timezone.utc),

        underlying_price=underlying_price,

        last_price=last_price,

        bid_price=bid_price,
        ask_price=ask_price,

        volume=volume,

        open_interest=open_interest,

        oi_change=oi_change,

        implied_volatility=implied_volatility,

        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
    )

    db.add(snapshot)

    return snapshot