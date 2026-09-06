from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Any


class MarketDataProvider(ABC):
    """
    Base interface for all market data providers.

    Every provider should implement methods required
    to fetch current and historical option market data.
    """

async def get_option_chain(
    self,
    underlying_symbol: str,
    expiry_date: date | None = None,
) -> list[OptionQuote]:

    if expiry_date is None:
        raise ValueError(
            "expiry_date is required for Groww option chain"
        )

    print("\n========================================")
    print("GROWW OPTION CHAIN REQUEST")
    print("========================================")
    print("Underlying:", underlying_symbol)
    print("Expiry:", expiry_date)

    response = self.client.get_option_chain(
        exchange=self.client.EXCHANGE_NSE,
        underlying=underlying_symbol,
        expiry_date=expiry_date.strftime("%Y-%m-%d"),
    )

    print("\n========================================")
    print("GROWW RAW RESPONSE DEBUG")
    print("========================================")
    print("Response Type:", type(response))

    if isinstance(response, dict):

        print("Top Level Keys:", list(response.keys()))

        payload = response.get("payload", response)

        print("Payload Type:", type(payload))

        if isinstance(payload, dict):

            print("Payload Keys:", list(payload.keys()))

            strikes = payload.get("strikes")

            print("Strikes:", type(strikes))

            if isinstance(strikes, dict):

                print("TOTAL STRIKES:", len(strikes))
                print(
                    "FIRST 5 STRIKES:",
                    list(strikes.keys())[:5],
                )

            else:
                print("❌ NO VALID strikes DICT FOUND")

        else:
            print("❌ PAYLOAD IS NOT A DICT")

    else:
        print("❌ RESPONSE IS NOT A DICT")
        print(response)

    snapshot_time = datetime.now()

    quotes = self._parse_option_chain(
        response=response,
        underlying_symbol=underlying_symbol,
        expiry_date=expiry_date,
        snapshot_time=snapshot_time,
    )

    print("\n========================================")
    print("PARSER RESULT")
    print("========================================")
    print("TOTAL QUOTES PARSED:", len(quotes))

    return quotes

    @abstractmethod
    def get_historical_option_chain(
        self,
        underlying_symbol: str,
        expiry_date: date,
        historical_date: date,
    ) -> dict[str, Any]:
        """
        Get historical option chain data.
        """
        raise NotImplementedError

    @abstractmethod
    def get_underlying_price(
        self,
        underlying_symbol: str,
    ) -> Decimal | None:
        """
        Get current underlying price.
        """
        raise NotImplementedError