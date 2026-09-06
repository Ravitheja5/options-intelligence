from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.option_chain_snapshot import OptionChainSnapshot
from app.models.option_contract import OptionContract
from app.models.underlying import Underlying

from app.services.market_data.schemas import OptionQuote


class SnapshotService:
    """
    Handles persistent option-chain snapshots.

    Responsibilities:
    - Find or create option contracts
    - Save current market snapshots
    - Retrieve the previous snapshot
    - Provide real historical comparison data
    """

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # UNDERLYING
    # ============================================================

    def get_underlying(
        self,
        underlying_symbol: str,
    ) -> Underlying | None:

        statement = (
            select(Underlying)
            .where(
                Underlying.symbol == underlying_symbol
            )
        )

        return self.db.scalar(statement)

    # ============================================================
    # OPTION CONTRACT
    # ============================================================

    def get_or_create_option_contract(
        self,
        quote: OptionQuote,
        underlying: Underlying,
    ) -> OptionContract:

        statement = (
            select(OptionContract)
            .where(
                OptionContract.trading_symbol
                == quote.trading_symbol
            )
        )

        contract = self.db.scalar(statement)

        if contract is not None:
            return contract

        contract = OptionContract(
            underlying_id=underlying.id,
            exchange=quote.exchange,
            trading_symbol=quote.trading_symbol,
            expiry_date=quote.expiry_date,
            strike_price=quote.strike_price,
            option_type=quote.option_type,
            lot_size=1,
            tick_size=Decimal("0.05"),
            is_active=True,
        )

        self.db.add(contract)

        self.db.flush()

        return contract

    # ============================================================
    # PREVIOUS SNAPSHOT
    # ============================================================

    def get_previous_snapshot(
        self,
        option_contract_id: int,
        current_time: datetime,
    ) -> OptionChainSnapshot | None:

        statement = (
            select(OptionChainSnapshot)
            .where(
                OptionChainSnapshot.option_contract_id
                == option_contract_id,
                OptionChainSnapshot.snapshot_time
                < current_time,
            )
            .order_by(
                OptionChainSnapshot.snapshot_time.desc()
            )
            .limit(1)
        )

        return self.db.scalar(statement)

    # ============================================================
    # SAVE SNAPSHOT
    # ============================================================

    def save_snapshot(
        self,
        quote: OptionQuote,
        contract: OptionContract,
        underlying_price: Decimal,
    ) -> OptionChainSnapshot:

        snapshot = OptionChainSnapshot(
            option_contract_id=contract.id,
            snapshot_time=quote.timestamp,
            underlying_price=underlying_price,
            last_price=quote.ltp or Decimal("0"),
            bid_price=quote.bid_price,
            ask_price=quote.ask_price,
            volume=quote.volume,
            open_interest=quote.open_interest,
            oi_change=quote.oi_change,
            implied_volatility=quote.iv,
            delta=quote.delta,
            gamma=quote.gamma,
            theta=quote.theta,
            vega=quote.vega,
        )

        self.db.add(snapshot)

        return snapshot

    # ============================================================
    # PROCESS COMPLETE OPTION CHAIN
    # ============================================================

    def process_option_chain(
        self,
        quotes: list[OptionQuote],
        underlying_symbol: str,
        underlying_price: Decimal,
    ) -> dict[str, OptionChainSnapshot | None]:
        """
        Save the current option chain and return
        previous snapshots for comparison.

        Returns:
            {
                trading_symbol: previous_snapshot
            }
        """

        underlying = self.get_underlying(
            underlying_symbol
        )

        if underlying is None:
            raise ValueError(
                f"Underlying not found: {underlying_symbol}"
            )

        previous_snapshots: dict[
            str,
            OptionChainSnapshot | None
        ] = {}

        for quote in quotes:

            contract = self.get_or_create_option_contract(
                quote=quote,
                underlying=underlying,
            )

            previous_snapshot = self.get_previous_snapshot(
                option_contract_id=contract.id,
                current_time=quote.timestamp,
            )

            previous_snapshots[
                quote.trading_symbol
            ] = previous_snapshot

            self.save_snapshot(
                quote=quote,
                contract=contract,
                underlying_price=underlying_price,
            )

        self.db.commit()

        return previous_snapshots