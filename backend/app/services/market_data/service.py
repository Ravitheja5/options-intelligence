from datetime import date

from app.services.market_data.base import MarketDataProvider
from app.services.market_data.providers.groww import GrowwMarketDataProvider


class MarketDataService:
    def __init__(self, provider: MarketDataProvider | None = None):
        self.provider = provider or GrowwMarketDataProvider()

    async def option_chain(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ):
        return await self.provider.get_option_chain(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

    async def underlying_price(self, underlying_symbol: str):
        return await self.provider.get_underlying_price(
            underlying_symbol
        )

    async def health(self):
        return await self.provider.health_check()


market_data_service = MarketDataService()
