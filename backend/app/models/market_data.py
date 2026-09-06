from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class MarketCandle(Base):
    __tablename__ = "market_candles"

    id: Mapped[int] = mapped_column(primary_key=True)

    underlying_id: Mapped[int] = mapped_column(
        ForeignKey("underlyings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    timeframe: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    candle_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    open: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    high: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    low: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    close: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    volume: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    open_interest: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "underlying_id",
            "timeframe",
            "candle_time",
            name="uq_market_candle",
        ),
    )
