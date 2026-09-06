from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MaxPainMetrics:
    max_pain_strike: Decimal | None
    minimum_pain: Decimal | None


def calculate_max_pain(options) -> MaxPainMetrics:
    """
    Calculate Max Pain using option Open Interest.

    For every possible strike:
    - Calculate CE writer payout
    - Calculate PE writer payout
    - Total payout

    Strike with minimum total payout = Max Pain.
    """

    strikes = sorted(
        {
            option.strike_price
            for option in options
            if option.strike_price is not None
        }
    )

    if not strikes:
        return MaxPainMetrics(
            max_pain_strike=None,
            minimum_pain=None,
        )

    minimum_pain: Decimal | None = None
    max_pain_strike: Decimal | None = None

    for settlement_price in strikes:

        total_pain = Decimal("0")

        for option in options:

            if (
                option.strike_price is None
                or option.open_interest is None
            ):
                continue

            strike = option.strike_price
            oi = Decimal(option.open_interest)

            option_type = option.option_type.upper()

            # --------------------------------------------
            # CALL OPTION PAIN
            # --------------------------------------------

            if option_type == "CE":

                intrinsic_value = max(
                    settlement_price - strike,
                    Decimal("0"),
                )

                total_pain += intrinsic_value * oi

            # --------------------------------------------
            # PUT OPTION PAIN
            # --------------------------------------------

            elif option_type == "PE":

                intrinsic_value = max(
                    strike - settlement_price,
                    Decimal("0"),
                )

                total_pain += intrinsic_value * oi

        # --------------------------------------------
        # Find minimum pain
        # --------------------------------------------

        if (
            minimum_pain is None
            or total_pain < minimum_pain
        ):

            minimum_pain = total_pain
            max_pain_strike = settlement_price

    return MaxPainMetrics(
        max_pain_strike=max_pain_strike,
        minimum_pain=minimum_pain,
    )
