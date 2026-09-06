import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv
from growwapi import GrowwAPI
from app.services.market_data.base import MarketDataProvider
from app.services.market_data.schemas import OptionQuote


load_dotenv()


class GrowwMarketDataProvider(MarketDataProvider):

    def __init__(self):

        api_key = os.getenv("GROWW_API_KEY")
        api_secret = os.getenv("GROWW_API_SECRET")

        if not api_key:
            raise RuntimeError(
                "GROWW_API_KEY is missing in .env"
            )

        if not api_secret:
            raise RuntimeError(
                "GROWW_API_SECRET is missing in .env"
            )

        print("\n========================================")
        print("INITIALIZING GROWW MARKET DATA PROVIDER")
        print("========================================")

        self.access_token = GrowwAPI.get_access_token(
            api_key=api_key,
            secret=api_secret,
        )

        self.client = GrowwAPI(
            self.access_token
        )

        print("✅ GROWW AUTHENTICATION SUCCESSFUL")

    # ============================================================
    # OPTION CHAIN
    # ============================================================

    async def get_option_chain(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> list[OptionQuote]:

        if expiry_date is None:
            raise ValueError(
                "expiry_date is required"
            )

        symbol = underlying_symbol.upper().strip()

        print("\n========================================")
        print("FETCHING OPTION CHAIN")
        print("========================================")

        print("Underlying:", symbol)
        print("Expiry:", expiry_date)
        print("\n🔍 REQUEST DETAILS")
        print("Exchange:", self.client.EXCHANGE_NSE)
        print("Underlying:", symbol)
        print("Expiry:", expiry_date.strftime("%Y-%m-%d"))

        response = self.client.get_option_chain(
            exchange=self.client.EXCHANGE_NSE,
            underlying=symbol,
            expiry_date=expiry_date.strftime(
                "%Y-%m-%d"
            ),
        )

        print("\n========== GROWW OPTION CHAIN ==========")
        print("UNDERLYING:", underlying_symbol)
        print("EXPIRY:", expiry_date)
        print("RESPONSE:", response)
        print("========================================\n")

        print("\n========================================")
        print("RAW GROWW RESPONSE")
        print("========================================")

        print(type(response))

        if isinstance(response, dict):

            print("TOP LEVEL KEYS:")
            print(response.keys())

        else:

            print(response)

        snapshot_time = datetime.now()

        quotes = self._parse_option_chain(
            response=response,
            underlying_symbol=symbol,
            expiry_date=expiry_date,
            snapshot_time=snapshot_time,
        )

        print("\n========================================")
        print("OPTION CHAIN RESULT")
        print("========================================")

        print("TOTAL QUOTES PARSED:", len(quotes))

        return quotes

    # ============================================================
    # UNDERLYING PRICE
    # ============================================================

    async def get_underlying_price(
        self,
        underlying_symbol: str,
    ) -> float | None:

        symbol = underlying_symbol.upper().strip()

        print("\n========================================")
        print("FETCHING UNDERLYING PRICE")
        print("========================================")

        print("Underlying:", symbol)

        trading_symbol = f"NSE_{symbol}"

        try:

            response = self.client.get_ltp(
                segment=self.client.SEGMENT_CASH,
                exchange_trading_symbols=(
                    trading_symbol,
                ),
            )

            print("LTP RESPONSE:")
            print(response)

            if not response:
                return None

            value = response.get(
                trading_symbol
            )

            if value is None:

                value = next(
                    iter(response.values()),
                    None,
                )

            if value is None:
                return None

            # Sometimes API may return dict
            if isinstance(value, dict):

                value = (
                    value.get("ltp")
                    or value.get("last_price")
                    or value.get("price")
                )

            if value is None:
                return None

            return float(value)

        except Exception as error:

            print(
                "❌ UNDERLYING PRICE ERROR:",
                error,
            )

            return None

    # ============================================================
    # HEALTH CHECK
    # ============================================================

    async def health_check(self) -> bool:

        try:

            self.client.get_user_profile()

            return True

        except Exception as error:

            print(
                "❌ GROWW HEALTH CHECK FAILED:",
                error,
            )

            return False

    # ============================================================
    # OPTION CHAIN PARSER
    # ============================================================

    def _parse_option_chain(
        self,
        response: Any,
        underlying_symbol: str,
        expiry_date: date,
        snapshot_time: datetime,
    ) -> list[OptionQuote]:

        quotes: list[OptionQuote] = []

        if not isinstance(response, dict):

            print(
                "❌ RESPONSE IS NOT A DICTIONARY"
            )

            return quotes

        # ========================================================
        # FIND ACTUAL PAYLOAD
        # ========================================================

        payload = response

        if isinstance(
            response.get("payload"),
            dict,
        ):
            payload = response["payload"]

        elif isinstance(
            response.get("data"),
            dict,
        ):
            payload = response["data"]

        elif isinstance(
            response.get("result"),
            dict,
        ):
            payload = response["result"]

        print("\nPAYLOAD KEYS:")

        if isinstance(payload, dict):
            print(payload.keys())

        # ========================================================
        # FIND STRIKES
        # ========================================================

        strikes = None

        possible_keys = [
            "strikes",
            "strike_data",
            "option_chain",
            "options",
        ]

        for key in possible_keys:

            value = payload.get(key)

            if value is not None:

                strikes = value

                print(
                    f"FOUND OPTION DATA KEY: {key}"
                )

                break

        # ========================================================
        # CASE 1 — STRIKES IS DICTIONARY
        # ========================================================

        if isinstance(strikes, dict):

            for strike, strike_data in strikes.items():

                self._process_strike(
                    quotes=quotes,
                    strike=strike,
                    strike_data=strike_data,
                    underlying_symbol=underlying_symbol,
                    expiry_date=expiry_date,
                    snapshot_time=snapshot_time,
                )

        # ========================================================
        # CASE 2 — STRIKES IS LIST
        # ========================================================

        elif isinstance(strikes, list):

            print(
                "PROCESSING OPTION DATA AS LIST"
            )

            for item in strikes:

                if not isinstance(item, dict):
                    continue

                strike = (
                    item.get("strike")
                    or item.get("strike_price")
                )

                if strike is None:
                    continue

                self._process_strike(
                    quotes=quotes,
                    strike=strike,
                    strike_data=item,
                    underlying_symbol=underlying_symbol,
                    expiry_date=expiry_date,
                    snapshot_time=snapshot_time,
                )

        # ========================================================
        # FALLBACK — RESPONSE ITSELF MAY CONTAIN STRIKES
        # ========================================================

        elif isinstance(payload, dict):

            numeric_keys_found = False

            for key, value in payload.items():

                try:

                    Decimal(str(key))

                    numeric_keys_found = True

                    self._process_strike(
                        quotes=quotes,
                        strike=key,
                        strike_data=value,
                        underlying_symbol=underlying_symbol,
                        expiry_date=expiry_date,
                        snapshot_time=snapshot_time,
                    )

                except Exception:

                    continue

            if not numeric_keys_found:

                print(
                    "❌ COULD NOT FIND STRIKES "
                    "IN GROWW RESPONSE"
                )

        print(
            "\n✅ TOTAL OPTIONS CREATED:",
            len(quotes),
        )

        return quotes

    # ============================================================
    # PROCESS SINGLE STRIKE
    # ============================================================

    def _process_strike(
        self,
        quotes: list[OptionQuote],
        strike: Any,
        strike_data: Any,
        underlying_symbol: str,
        expiry_date: date,
        snapshot_time: datetime,
    ):

        if not isinstance(strike_data, dict):
            return

        try:

            strike_price = Decimal(
                str(strike)
            )

        except Exception:

            strike_price = self._decimal(
                strike_data.get("strike")
                or strike_data.get(
                    "strike_price"
                )
            )

            if strike_price is None:
                return

        # ========================================================
        # FIND CE AND PE
        # ========================================================

        call_data = (
            strike_data.get("CE")
            or strike_data.get("ce")
            or strike_data.get("CALL")
            or strike_data.get("call")
        )

        put_data = (
            strike_data.get("PE")
            or strike_data.get("pe")
            or strike_data.get("PUT")
            or strike_data.get("put")
        )

        # ========================================================
        # PROCESS CALL
        # ========================================================

        if isinstance(call_data, dict):

            quote = self._create_option_quote(
                option_data=call_data,
                strike_price=strike_price,
                option_type="CE",
                underlying_symbol=underlying_symbol,
                expiry_date=expiry_date,
                snapshot_time=snapshot_time,
            )

            if quote:

                quotes.append(quote)

        # ========================================================
        # PROCESS PUT
        # ========================================================

        if isinstance(put_data, dict):

            quote = self._create_option_quote(
                option_data=put_data,
                strike_price=strike_price,
                option_type="PE",
                underlying_symbol=underlying_symbol,
                expiry_date=expiry_date,
                snapshot_time=snapshot_time,
            )

            if quote:

                quotes.append(quote)

    # ============================================================
    # CREATE OPTION QUOTE
    # ============================================================

    def _create_option_quote(
        self,
        option_data: dict,
        strike_price: Decimal,
        option_type: str,
        underlying_symbol: str,
        expiry_date: date,
        snapshot_time: datetime,
    ) -> OptionQuote | None:

        try:

            greeks = (
                option_data.get("greeks")
                or {}
            )

            if not isinstance(greeks, dict):
                greeks = {}

            # ====================================================
            # TRADING SYMBOL
            # ====================================================

            trading_symbol = (
                option_data.get("trading_symbol")
                or option_data.get(
                    "exchange_trading_symbol"
                )
                or option_data.get("symbol")
            )

            # Generate fallback symbol if API doesn't provide it
            if not trading_symbol:

                trading_symbol = (
                    f"{underlying_symbol}_"
                    f"{expiry_date.strftime('%Y%m%d')}_"
                    f"{int(strike_price)}_"
                    f"{option_type}"
                )

            # ====================================================
            # LTP
            # ====================================================

            ltp = self._decimal(
                option_data.get("ltp")
                or option_data.get(
                    "last_price"
                )
                or option_data.get("price")
            )

            # LTP is mandatory for database snapshot
            if ltp is None:

                print(
                    "⚠️ SKIPPING OPTION - LTP MISSING:",
                    trading_symbol,
                )

                return None

            # ====================================================
            # CREATE QUOTE
            # ====================================================

            quote = OptionQuote(

                trading_symbol=str(
                    trading_symbol
                ),

                exchange=str(
                    option_data.get(
                        "exchange",
                        "NSE",
                    )
                ),

                underlying_symbol=underlying_symbol,

                expiry_date=expiry_date,

                strike_price=strike_price,

                option_type=option_type,

                # MARKET DATA

                ltp=ltp,

                previous_close=self._decimal(
                    option_data.get(
                        "previous_close"
                    )
                    or option_data.get(
                        "close"
                    )
                ),

                change=self._decimal(
                    option_data.get("change")
                ),

                change_percent=self._decimal(
                    option_data.get(
                        "change_percent"
                    )
                    or option_data.get(
                        "percent_change"
                    )
                ),

                volume=self._int(
                    option_data.get("volume")
                )
                or 0,

                open_interest=self._int(
                    option_data.get(
                        "open_interest"
                    )
                    or option_data.get("oi")
                )
                or 0,

                oi_change=self._int(
                    option_data.get("oi_change")
                    or option_data.get(
                        "change_oi"
                    )
                    or option_data.get(
                        "change_in_oi"
                    )
                )
                or 0,

                bid_price=self._decimal(
                    option_data.get(
                        "bid_price"
                    )
                    or option_data.get("bid")
                ),

                ask_price=self._decimal(
                    option_data.get(
                        "ask_price"
                    )
                    or option_data.get("ask")
                ),

                # IMPLIED VOLATILITY

                iv=self._decimal(
                    greeks.get("iv")
                    or option_data.get("iv")
                    or option_data.get(
                        "implied_volatility"
                    )
                ),

                # GREEKS

                delta=self._decimal(
                    greeks.get("delta")
                    or option_data.get("delta")
                ),

                gamma=self._decimal(
                    greeks.get("gamma")
                    or option_data.get("gamma")
                ),

                theta=self._decimal(
                    greeks.get("theta")
                    or option_data.get("theta")
                ),

                vega=self._decimal(
                    greeks.get("vega")
                    or option_data.get("vega")
                ),

                rho=self._decimal(
                    greeks.get("rho")
                    or option_data.get("rho")
                ),

                timestamp=snapshot_time,
            )

            return quote

        except Exception as error:

            print(
                "❌ FAILED TO CREATE OPTION QUOTE:",
                error,
            )

            return None

    # ============================================================
    # DECIMAL HELPER
    # ============================================================

    @staticmethod
    def _decimal(
        value: Any,
    ) -> Decimal | None:

        if value is None:
            return None

        try:

            return Decimal(
                str(value)
            )

        except (
            ValueError,
            TypeError,
        ):

            return None

    # ============================================================
    # INTEGER HELPER
    # ============================================================

    @staticmethod
    def _int(
        value: Any,
    ) -> int | None:

        if value is None:
            return None

        try:

            return int(
                float(value)
            )

        except (
            ValueError,
            TypeError,
        ):

            return None