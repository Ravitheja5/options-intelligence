from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UnderlyingResponse(BaseModel):
    id: int
    symbol: str
    name: str
    exchange: str
    segment: str
    underlying_type: str
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
