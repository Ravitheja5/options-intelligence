from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OptionContractResponse(BaseModel):
    id: int
    underlying_id: int
    exchange: str
    trading_symbol: str
    expiry_date: date
    strike_price: Decimal
    option_type: str
    lot_size: int
    tick_size: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
