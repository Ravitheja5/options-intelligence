from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class SupportResistanceMetrics:
    support: Decimal | None
    resistance: Decimal | None

    top_supports: list[Decimal]
    top_resistances: list[Decimal]


def calculate_support_resistance(
    options,
    top_levels: int = 3,
) -> SupportResistanceMetrics:
    """
    Calculate support and resistance levels using Open Interest.

    Highest PE OI = Support
    Highest CE OI = Resistance
    """

    put_options = [
        option
        for option in options
        if option.option_type.upper() == "PE"
        and option.open_interest is not None
    ]

    call_options = [
        option
        for option in options
        if option.option_type.upper() == "CE"
        and option.open_interest is not None
    ]

    sorted_puts = sorted(
        put_options,
        key=lambda option: option.open_interest,
        reverse=True,
    )

    sorted_calls = sorted(
        call_options,
        key=lambda option: option.open_interest,
        reverse=True,
    )

    top_supports = [
        option.strike_price
        for option in sorted_puts[:top_levels]
    ]

    top_resistances = [
        option.strike_price
        for option in sorted_calls[:top_levels]
    ]

    support = (
        top_supports[0]
        if top_supports
        else None
    )

    resistance = (
        top_resistances[0]
        if top_resistances
        else None
    )

    return SupportResistanceMetrics(
        support=support,
        resistance=resistance,
        top_supports=top_supports,
        top_resistances=top_resistances,
    )
