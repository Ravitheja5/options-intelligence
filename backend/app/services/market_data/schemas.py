from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OptionQuote(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trading_symbol: str
    exchange: str
    underlying_symbol: str
    expiry_date: date
    strike_price: Decimal
    option_type: str

    # Market data
    ltp: Decimal | None = None
    previous_close: Decimal | None = None
    change: Decimal | None = None
    change_percent: Decimal | None = None

    volume: int | None = None
    open_interest: int | None = None
    oi_change: int | None = None

    bid_price: Decimal | None = None
    ask_price: Decimal | None = None

    # Implied volatility
    iv: Decimal | None = None

    # Option Greeks
    delta: Decimal | None = None
    gamma: Decimal | None = None
    theta: Decimal | None = None
    vega: Decimal | None = None
    rho: Decimal | None = None

    # Timestamp
    timestamp: datetime