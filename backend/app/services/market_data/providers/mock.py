from datetime import date, datetime, timezone
from decimal import Decimal

from app.services.market_data.base import MarketDataProvider
from app.services.market_data.schemas import OptionQuote


class MockMarketDataProvider(MarketDataProvider):

    async def get_option_chain(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> list[OptionQuote]:

        expiry = expiry_date or date.today()

        return [
            OptionQuote(
                trading_symbol=f"{underlying_symbol}_DEMO_CE",
                exchange="DEMO",
                underlying_symbol=underlying_symbol,
                expiry_date=expiry,
                strike_price=Decimal("25000"),
                option_type="CE",
                ltp=Decimal("150"),
                previous_close=Decimal("140"),
                change=Decimal("10"),
                change_percent=Decimal("7.14"),
                volume=100000,
                open_interest=500000,
                oi_change=50000,
                bid_price=Decimal("149.5"),
                ask_price=Decimal("150.5"),
                iv=Decimal("14.5"),
                timestamp=datetime.now(timezone.utc),
            ),
            OptionQuote(
                trading_symbol=f"{underlying_symbol}_DEMO_PE",
                exchange="DEMO",
                underlying_symbol=underlying_symbol,
                expiry_date=expiry,
                strike_price=Decimal("25000"),
                option_type="PE",
                ltp=Decimal("130"),
                previous_close=Decimal("135"),
                change=Decimal("-5"),
                change_percent=Decimal("-3.70"),
                volume=90000,
                open_interest=450000,
                oi_change=-20000,
                bid_price=Decimal("129.5"),
                ask_price=Decimal("130.5"),
                iv=Decimal("15.2"),
                timestamp=datetime.now(timezone.utc),
            ),
        ]

    async def get_underlying_price(
        self,
        underlying_symbol: str,
    ) -> float | None:

        prices = {
            "NIFTY": 25000.0,
            "BANKNIFTY": 56000.0,
            "SENSEX": 81000.0,
            "GOLD": 75000.0,
            "SILVER": 90000.0,
        }

        return prices.get(underlying_symbol)

    async def health_check(self) -> bool:
        return True
