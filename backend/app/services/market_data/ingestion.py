from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.core.database import SessionLocal
from app.services.market_data.service import market_data_service
from app.services.market_data.persistence import MarketDataPersistenceService


async def ingest_option_chain(
    underlying_symbol: str,
    expiry_date: date,
) -> int:

    quotes = await market_data_service.option_chain(
        underlying_symbol=underlying_symbol,
        expiry_date=expiry_date,
    )

    if not quotes:
        return 0

    underlying_price = await market_data_service.underlying_price(
        underlying_symbol
    )

    if underlying_price is None:
        raise ValueError(
            f"Could not obtain underlying price for {underlying_symbol}"
        )

    db = SessionLocal()

    try:
        persistence = MarketDataPersistenceService(db)

        count = persistence.persist_option_chain(
            underlying_symbol=underlying_symbol,
            quotes=quotes,
            underlying_price=Decimal(str(underlying_price)),
        )

        return count

    finally:
        db.close()
