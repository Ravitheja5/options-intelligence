from abc import ABC, abstractmethod
from datetime import date

from app.services.market_data.schemas import OptionQuote


class MarketDataProvider(ABC):

    @abstractmethod
    async def get_option_chain(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> list[OptionQuote]:
        """
        Return normalized option-chain quotes.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_underlying_price(
        self,
        underlying_symbol: str,
    ) -> float | None:
        """
        Return the latest underlying price.
        """
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check whether the market-data provider is available.
        """
        raise NotImplementedError
