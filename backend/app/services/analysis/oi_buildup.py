from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OIBuildupMetrics:
    classification: str
    price_change: Decimal | None
    oi_change: int | None


def classify_oi_buildup(
    price_change: Decimal | None,
    oi_change: int | None,
) -> str:
    """
    Classify option activity using
    price movement and Open Interest movement.
    """

    if price_change is None or oi_change is None:
        return "INSUFFICIENT_DATA"

    if price_change == 0 and oi_change == 0:
        return "NO_CHANGE"

    # Price ↑ + OI ↑
    if price_change > 0 and oi_change > 0:
        return "LONG_BUILDUP"

    # Price ↓ + OI ↑
    if price_change < 0 and oi_change > 0:
        return "SHORT_BUILDUP"

    # Price ↑ + OI ↓
    if price_change > 0 and oi_change < 0:
        return "SHORT_COVERING"

    # Price ↓ + OI ↓
    if price_change < 0 and oi_change < 0:
        return "LONG_UNWINDING"

    return "NEUTRAL"


def calculate_oi_buildup(
    last_price: Decimal | None,
    previous_price: Decimal | None,
    open_interest: int | None,
    previous_open_interest: int | None,
) -> OIBuildupMetrics:
    """
    Calculate price change, OI change,
    and OI buildup classification.
    """

    price_change = None
    oi_change = None

    if (
        last_price is not None
        and previous_price is not None
    ):
        price_change = last_price - previous_price

    if (
        open_interest is not None
        and previous_open_interest is not None
    ):
        oi_change = (
            open_interest
            - previous_open_interest
        )

    classification = classify_oi_buildup(
        price_change=price_change,
        oi_change=oi_change,
    )

    return OIBuildupMetrics(
        classification=classification,
        price_change=price_change,
        oi_change=oi_change,
    )
