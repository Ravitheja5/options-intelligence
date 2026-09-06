from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class OptionContract(Base):
    __tablename__ = "option_contracts"

    id: Mapped[int] = mapped_column(primary_key=True)

    underlying_id: Mapped[int] = mapped_column(
        ForeignKey("underlyings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    exchange: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    trading_symbol: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    expiry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    strike_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        index=True,
    )

    option_type: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        index=True,
    )

    lot_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    tick_size: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "underlying_id",
            "expiry_date",
            "strike_price",
            "option_type",
            name="uq_option_contract",
        ),
    )
