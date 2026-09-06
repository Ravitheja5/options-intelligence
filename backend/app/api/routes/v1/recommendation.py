from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analysis.service import AnalysisService


router = APIRouter(
    prefix="/recommendation",
    tags=["Trading Recommendation"],
)


@router.get("")
def get_trading_recommendation(
    underlying_symbol: str = Query(
        default="NIFTY",
        description="Underlying symbol",
    ),
    expiry_date: date | None = Query(
        default=None,
        description="Option expiry date",
    ),
    db: Session = Depends(get_db),
):

    service = AnalysisService(db)

    recommendation = service.get_trading_recommendation(
        underlying_symbol=underlying_symbol.upper(),
        expiry_date=expiry_date,
    )

    return {
        "success": True,
        "underlying_symbol": underlying_symbol.upper(),
        "expiry_date": expiry_date,

        "recommendation": recommendation.recommendation,

        "confidence_score": float(
            recommendation.confidence_score
        ),

        "reasons": recommendation.reasons,
    }