from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.option_chain_snapshot import OptionChainSnapshot
from app.models.option_contract import OptionContract
from app.models.underlying import Underlying


class MarketDataPersistenceService:

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # PERSIST COMPLETE OPTION CHAIN
    # =========================================================

    def persist_option_chain(
        self,
        underlying_symbol: str,
        quotes: list[Any],
        underlying_price: Decimal,
    ) -> int:

        symbol = underlying_symbol.upper().strip()

        # =====================================================
        # GET OR CREATE UNDERLYING
        # =====================================================

        underlying = self.db.scalar(
            select(Underlying).where(
                Underlying.symbol == symbol
            )
        )

        if underlying is None:

            underlying = Underlying(
                symbol=symbol,
                name=symbol,
                exchange="NSE",
                segment="DERIVATIVES",
                underlying_type="INDEX",
                currency="INR",
                is_active=True,
            )

            self.db.add(underlying)
            self.db.flush()

        persisted_count = 0

        # =====================================================
        # PROCESS ALL OPTION QUOTES
        # =====================================================

        for quote in quotes:

            try:

                # =============================================
                # CONTRACT DATA
                # =============================================

                trading_symbol = self._get_value(
                    quote,
                    "trading_symbol",
                )

                option_type = self._get_value(
                    quote,
                    "option_type",
                )

                strike_price = self._get_value(
                    quote,
                    "strike_price",
                )

                expiry_date = self._get_value(
                    quote,
                    "expiry_date",
                )

                # =============================================
                # VALIDATE REQUIRED CONTRACT FIELDS
                # =============================================

                if (
                    trading_symbol is None
                    or option_type is None
                    or strike_price is None
                    or expiry_date is None
                ):
                    print(
                        "⚠️ Skipping invalid contract"
                    )
                    continue

                trading_symbol = str(
                    trading_symbol
                ).strip()

                if not trading_symbol:
                    continue

                option_type = str(
                    option_type
                ).upper().strip()

                strike_price = Decimal(
                    str(strike_price)
                )

                # =============================================
                # GET OR CREATE OPTION CONTRACT
                # =============================================

                contract = self.db.scalar(
                    select(OptionContract).where(
                        OptionContract.trading_symbol
                        == trading_symbol
                    )
                )

                if contract is None:

                    exchange = (
                        self._get_value(
                            quote,
                            "exchange",
                        )
                        or "NSE"
                    )

                    lot_size = (
                        self._int_or_none(
                            self._get_value(
                                quote,
                                "lot_size",
                            )
                        )
                        or 1
                    )

                    tick_size = (
                        self._decimal_or_none(
                            self._get_value(
                                quote,
                                "tick_size",
                            )
                        )
                        or Decimal("0.05")
                    )

                    contract = OptionContract(
                        underlying_id=underlying.id,
                        exchange=str(exchange),
                        trading_symbol=trading_symbol,
                        expiry_date=expiry_date,
                        strike_price=strike_price,
                        option_type=option_type,
                        lot_size=lot_size,
                        tick_size=tick_size,
                        is_active=True,
                    )

                    self.db.add(contract)
                    self.db.flush()

                # =============================================
                # MARKET DATA
                # =============================================

                ltp = self._decimal_or_none(
                    self._get_value(
                        quote,
                        "ltp",
                    )
                )

                # LTP is required by DB model
                if ltp is None:
                    print(
                        f"⚠️ Skipping {trading_symbol}: "
                        "LTP missing"
                    )
                    continue

                volume = self._int_or_none(
                    self._get_value(
                        quote,
                        "volume",
                    )
                )

                open_interest = self._int_or_none(
                    self._get_value(
                        quote,
                        "open_interest",
                    )
                )

                # =============================================
                # OI CHANGE
                # =============================================

                oi_change = self._int_or_none(
                    self._get_value(
                        quote,
                        "oi_change",
                    )
                )

                # =============================================
                # IMPLIED VOLATILITY
                # =============================================

                iv = self._decimal_or_none(
                    self._get_value(
                        quote,
                        "iv",
                    )
                )

                # =============================================
                # GREEKS
                # =============================================

                delta = self._decimal_or_none(
                    self._get_value(
                        quote,
                        "delta",
                    )
                )

                gamma = self._decimal_or_none(
                    self._get_value(
                        quote,
                        "gamma",
                    )
                )

                theta = self._decimal_or_none(
                    self._get_value(
                        quote,
                        "theta",
                    )
                )

                vega = self._decimal_or_none(
                    self._get_value(
                        quote,
                        "vega",
                    )
                )

                # =============================================
                # SNAPSHOT TIME
                # =============================================

                snapshot_time = (
                    self._get_value(
                        quote,
                        "timestamp",
                    )
                    or datetime.now(timezone.utc)
                )

                # =============================================
                # CREATE MARKET SNAPSHOT
                # =============================================

                snapshot = OptionChainSnapshot(

                    option_contract_id=contract.id,

                    snapshot_time=snapshot_time,

                    underlying_price=underlying_price,

                    last_price=ltp,

                    bid_price=self._decimal_or_none(
                        self._get_value(
                            quote,
                            "bid_price",
                        )
                    ),

                    ask_price=self._decimal_or_none(
                        self._get_value(
                            quote,
                            "ask_price",
                        )
                    ),

                    volume=volume or 0,

                    open_interest=open_interest or 0,

                    # IMPORTANT: SAVE OI CHANGE
                    oi_change=oi_change,

                    implied_volatility=iv,

                    delta=delta,

                    gamma=gamma,

                    theta=theta,

                    vega=vega,
                )

                self.db.add(snapshot)

                persisted_count += 1

            except Exception as error:

                print(
                    f"⚠️ Failed to persist quote: "
                    f"{error}"
                )

                self.db.rollback()

                # Reload underlying after rollback

                underlying = self.db.scalar(
                    select(Underlying).where(
                        Underlying.symbol == symbol
                    )
                )

                if underlying is None:
                    raise

                continue

        # =====================================================
        # COMMIT ALL DATA
        # =====================================================

        try:

            self.db.commit()

        except Exception as error:

            self.db.rollback()

            print(
                f"❌ Database commit failed: {error}"
            )

            raise

        print(
            f"💾 MARKET SNAPSHOTS SAVED: "
            f"{persisted_count}"
        )

        return persisted_count

    # =========================================================
    # GET VALUE FROM OBJECT OR DICTIONARY
    # =========================================================

    @staticmethod
    def _get_value(
        data: Any,
        field_name: str,
    ) -> Any:

        if isinstance(data, dict):
            return data.get(field_name)

        return getattr(
            data,
            field_name,
            None,
        )

    # =========================================================
    # DECIMAL HELPER
    # =========================================================

    @staticmethod
    def _decimal_or_none(
        value: Any,
    ) -> Decimal | None:

        if value is None:
            return None

        try:

            return Decimal(str(value))

        except (
            ValueError,
            TypeError,
        ):

            return None

    # =========================================================
    # INTEGER HELPER
    # =========================================================

    @staticmethod
    def _int_or_none(
        value: Any,
    ) -> int | None:

        if value is None:
            return None

        try:

            return int(value)

        except (
            ValueError,
            TypeError,
        ):

            return None