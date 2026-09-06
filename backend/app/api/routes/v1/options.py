from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.option_contract import OptionContract
from app.models.underlying import Underlying
from app.schemas.option import OptionContractResponse


router = APIRouter(
    prefix="/options",
    tags=["Options"],
)


@router.get(
    "",
    response_model=list[OptionContractResponse],
)
def list_options(
    symbol: str | None = None,
    expiry_date: date | None = None,
    option_type: str | None = None,
    strike_price: Decimal | None = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    query = select(OptionContract)

    if symbol:
        query = query.join(
            Underlying,
            OptionContract.underlying_id == Underlying.id,
        ).where(
            Underlying.symbol == symbol.upper()
        )

    if expiry_date:
        query = query.where(
            OptionContract.expiry_date == expiry_date
        )

    if option_type:
        query = query.where(
            OptionContract.option_type == option_type.upper()
        )

    if strike_price is not None:
        query = query.where(
            OptionContract.strike_price == strike_price
        )

    if active_only:
        query = query.where(
            OptionContract.is_active.is_(True)
        )

    query = query.order_by(
        OptionContract.expiry_date,
        OptionContract.strike_price,
        OptionContract.option_type,
    )

    return db.scalars(query).all()


@router.get(
    "/{trading_symbol}",
    response_model=OptionContractResponse,
)
def get_option(
    trading_symbol: str,
    db: Session = Depends(get_db),
):
    query = select(OptionContract).where(
        OptionContract.trading_symbol == trading_symbol
    )

    option = db.scalar(query)

    if option is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail=f"Option '{trading_symbol}' not found",
        )

    return option
