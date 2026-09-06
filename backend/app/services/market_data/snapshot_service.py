from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.option_chain_snapshot import OptionChainSnapshot


def create_option_snapshot(
    db: Session,
    option_contract_id: int,
    underlying_price: Decimal,
    last_price: Decimal,
    volume: int | None,
    open_interest: int | None,
    implied_volatility: Decimal | None,
    delta: Decimal | None,
    gamma: Decimal | None,
    theta: Decimal | None,
    vega: Decimal | None,
    bid_price: Decimal | None = None,
    ask_price: Decimal | None = None,
) -> OptionChainSnapshot:
    """
    Create and save a market snapshot for one option contract.
    """

    snapshot = OptionChainSnapshot(
        option_contract_id=option_contract_id,

        snapshot_time=datetime.now(timezone.utc),

        underlying_price=underlying_price,

        last_price=last_price,

        bid_price=bid_price,
        ask_price=ask_price,

        volume=volume,
        open_interest=open_interest,

        implied_volatility=implied_volatility,

        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
    )

    db.add(snapshot)

    return snapshot


def get_previous_snapshot(
    db: Session,
    option_contract_id: int,
    before_time: datetime | None = None,
) -> OptionChainSnapshot | None:
    """
    Get the latest historical snapshot
    before the specified time.
    """

    query = db.query(
        OptionChainSnapshot
    ).filter(
        OptionChainSnapshot.option_contract_id
        == option_contract_id
    )

    if before_time is not None:

        query = query.filter(
            OptionChainSnapshot.snapshot_time
            < before_time
        )

    return (
        query
        .order_by(
            OptionChainSnapshot.snapshot_time.desc()
        )
        .first()
    )