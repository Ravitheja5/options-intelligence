from decimal import Decimal


def classify_moneyness(
    option_type: str,
    strike_price: Decimal,
    atm_strike: Decimal,
) -> str:
    """
    Classify an option as ITM, ATM, or OTM.
    """

    option_type = option_type.upper()

    if strike_price == atm_strike:
        return "ATM"

    if option_type == "CE":

        if strike_price < atm_strike:
            return "ITM"

        return "OTM"

    if option_type == "PE":

        if strike_price > atm_strike:
            return "ITM"

        return "OTM"

    return "UNKNOWN"
