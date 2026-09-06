from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.underlying import Underlying
from app.schemas.underlying import UnderlyingResponse


router = APIRouter(
    prefix="/underlyings",
    tags=["Underlyings"],
)


@router.get(
    "",
    response_model=list[UnderlyingResponse],
)
def list_underlyings(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    query = select(Underlying)

    if active_only:
        query = query.where(Underlying.is_active.is_(True))

    query = query.order_by(Underlying.symbol)

    return db.scalars(query).all()


@router.get(
    "/{symbol}",
    response_model=UnderlyingResponse,
)
def get_underlying(
    symbol: str,
    db: Session = Depends(get_db),
):
    query = select(Underlying).where(
        Underlying.symbol == symbol.upper()
    )

    underlying = db.scalar(query)

    if underlying is None:
        raise HTTPException(
            status_code=404,
            detail=f"Underlying '{symbol}' not found",
        )

    return underlying
