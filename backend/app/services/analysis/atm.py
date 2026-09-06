from decimal import Decimal


def calculate_atm_strike(
    underlying_price: Decimal | None,
    strikes: list[Decimal],
) -> Decimal | None:
    """
    Find the strike price closest to
    the current underlying price.
    """

    if underlying_price is None:
        return None

    if not strikes:
        return None

    valid_strikes = [
        strike
        for strike in strikes
        if strike is not None
    ]

    if not valid_strikes:
        return None

    return min(
        valid_strikes,
        key=lambda strike: abs(
            strike - underlying_price
        ),
    )