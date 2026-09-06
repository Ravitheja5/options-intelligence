from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class TradeJournal(Base):
    __tablename__ = "trade_journal"

    id: Mapped[int] = mapped_column(primary_key=True)

    trade_id: Mapped[int] = mapped_column(
        ForeignKey("trades.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    setup_quality: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    confidence: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    market_condition: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    entry_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    exit_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    what_went_well: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    what_went_wrong: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    lesson: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    mistake: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    followed_plan: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    emotional_state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    tags: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    review_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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
