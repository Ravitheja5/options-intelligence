from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.option_chain_snapshot import OptionChainSnapshot
from app.models.option_contract import OptionContract


class SnapshotRepository:
    """
    Repository responsible for storing and retrieving
    historical option-chain snapshots.
    """

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # GET OPTION CONTRACT
    # ============================================================

    def get_option_contract(
        self,
        trading_symbol: str,
    ) -> OptionContract | None:

        return (
            self.db.query(OptionContract)
            .filter(
                OptionContract.trading_symbol
                == trading_symbol
            )
            .first()
        )

    # ============================================================
    # GET PREVIOUS SNAPSHOT
    # ============================================================

    def get_previous_snapshot(
        self,
        option_contract_id: int,
        current_time: datetime,
    ) -> OptionChainSnapshot | None:

        return (
            self.db.query(OptionChainSnapshot)
            .filter(
                OptionChainSnapshot.option_contract_id
                == option_contract_id,
                OptionChainSnapshot.snapshot_time
                < current_time,
            )
            .order_by(
                OptionChainSnapshot.snapshot_time.desc()
            )
            .first()
        )

    # ============================================================
    # SAVE SNAPSHOT
    # ============================================================

    def save_snapshot(
        self,
        option_contract_id: int,
        snapshot_time: datetime,
        underlying_price: Decimal,
        last_price: Decimal,
        bid_price: Decimal | None,
        ask_price: Decimal | None,
        volume: int | None,
        open_interest: int | None,
        implied_volatility: Decimal | None,
        delta: Decimal | None,
        gamma: Decimal | None,
        theta: Decimal | None,
        vega: Decimal | None,
    ) -> OptionChainSnapshot:

        snapshot = OptionChainSnapshot(
            option_contract_id=option_contract_id,

            snapshot_time=snapshot_time,

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

        self.db.add(snapshot)

        return snapshot