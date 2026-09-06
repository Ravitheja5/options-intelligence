from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PCRMetrics:
    total_call_oi: int
    total_put_oi: int

    total_call_volume: int
    total_put_volume: int

    oi_pcr: Decimal | None
    volume_pcr: Decimal | None


def calculate_pcr(
    put_value: int,
    call_value: int,
) -> Decimal | None:
    """
    Calculate Put-Call Ratio.

    PCR = Put / Call
    """

    if call_value <= 0:
        return None

    return (
        Decimal(put_value)
        / Decimal(call_value)
    ).quantize(Decimal("0.0001"))


def calculate_pcr_metrics(
    options,
) -> PCRMetrics:
    """
    Calculate PCR using analyzed option metrics.
    """

    total_call_oi = 0
    total_put_oi = 0

    total_call_volume = 0
    total_put_volume = 0

    for option in options:

        option_type = option.option_type.upper()

        open_interest = option.open_interest or 0
        volume = option.volume or 0

        if option_type == "CE":

            total_call_oi += open_interest
            total_call_volume += volume

        elif option_type == "PE":

            total_put_oi += open_interest
            total_put_volume += volume

    oi_pcr = calculate_pcr(
        put_value=total_put_oi,
        call_value=total_call_oi,
    )

    volume_pcr = calculate_pcr(
        put_value=total_put_volume,
        call_value=total_call_volume,
    )

    return PCRMetrics(
        total_call_oi=total_call_oi,
        total_put_oi=total_put_oi,

        total_call_volume=total_call_volume,
        total_put_volume=total_put_volume,

        oi_pcr=oi_pcr,
        volume_pcr=volume_pcr,
    )
