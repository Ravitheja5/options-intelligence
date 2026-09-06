from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.services.analysis.oi_buildup import (
    calculate_oi_buildup,
)

from app.services.analysis.trading_signal import (
    calculate_trading_signal,
)


@dataclass(frozen=True)
class OptionMetrics:
    trading_symbol: str
    option_type: str
    strike_price: Decimal

    underlying_price: Decimal | None
    atm_strike: Decimal | None
    moneyness: str

    last_price: Decimal | None
    previous_price: Decimal | None
    price_change: Decimal | None
    price_change_percent: Decimal | None

    volume: int | None

    open_interest: int | None
    previous_open_interest: int | None
    oi_change: int | None
    oi_change_percent: Decimal | None

    oi_buildup: str

    implied_volatility: Decimal | None

    delta: Decimal | None
    gamma: Decimal | None
    theta: Decimal | None
    vega: Decimal | None

    strike_distance: Decimal | None
    strike_distance_percent: Decimal | None

    liquidity_score: Decimal
    data_quality_score: Decimal

    trading_signal: str
    signal_score: int
    signal_reasons: list[str]


def calculate_strike_distance(
    strike_price: Decimal,
    underlying_price: Decimal | None,
) -> Decimal | None:

    if underlying_price is None:
        return None

    return abs(strike_price - underlying_price)


def calculate_strike_distance_percent(
    strike_price: Decimal,
    underlying_price: Decimal | None,
) -> Decimal | None:

    if underlying_price is None or underlying_price <= 0:
        return None

    distance = calculate_strike_distance(
        strike_price,
        underlying_price,
    )

    if distance is None:
        return None

    return (
        distance / underlying_price
    ) * Decimal("100")


def calculate_price_change(
    last_price: Decimal | None,
    previous_price: Decimal | None,
) -> Decimal | None:

    if last_price is None or previous_price is None:
        return None

    return last_price - previous_price


def calculate_price_change_percent(
    last_price: Decimal | None,
    previous_price: Decimal | None,
) -> Decimal | None:

    if (
        last_price is None
        or previous_price is None
        or previous_price <= 0
    ):
        return None

    change = last_price - previous_price

    return (
        change / previous_price
    ) * Decimal("100")


def calculate_oi_change(
    open_interest: int | None,
    previous_open_interest: int | None,
) -> int | None:

    if (
        open_interest is None
        or previous_open_interest is None
    ):
        return None

    return open_interest - previous_open_interest


def calculate_oi_change_percent(
    open_interest: int | None,
    previous_open_interest: int | None,
) -> Decimal | None:

    if (
        open_interest is None
        or previous_open_interest is None
        or previous_open_interest <= 0
    ):
        return None

    change = open_interest - previous_open_interest

    return (
        Decimal(change)
        / Decimal(previous_open_interest)
    ) * Decimal("100")


def calculate_liquidity_score(
    volume: int | None,
    open_interest: int | None,
) -> Decimal:

    volume_value = max(volume or 0, 0)
    oi_value = max(open_interest or 0, 0)

    if volume_value == 0 and oi_value == 0:
        return Decimal("0")

    volume_component = min(
        Decimal(volume_value) / Decimal("10000"),
        Decimal("1"),
    )

    oi_component = min(
        Decimal(oi_value) / Decimal("100000"),
        Decimal("1"),
    )

    score = (
        volume_component * Decimal("50")
        + oi_component * Decimal("50")
    )

    return score.quantize(Decimal("0.01"))


def calculate_data_quality_score(
    last_price: Decimal | None,
    volume: int | None,
    open_interest: int | None,
    implied_volatility: Decimal | None,
    delta: Decimal | None,
) -> Decimal:

    checks = [
        last_price is not None,
        volume is not None,
        open_interest is not None,
        implied_volatility is not None,
        delta is not None,
    ]

    available = sum(checks)

    return (
        Decimal(available)
        / Decimal(len(checks))
        * Decimal("100")
    ).quantize(Decimal("0.01"))


def build_option_metrics(
    trading_symbol: str,
    option_type: str,
    strike_price: Decimal,

    underlying_price: Decimal | None,
    atm_strike: Decimal | None,
    moneyness: str,

    last_price: Decimal | None,
    previous_price: Decimal | None,

    volume: int | None,

    open_interest: int | None,
    previous_open_interest: int | None,

    implied_volatility: Decimal | None,

    delta: Decimal | None,
    gamma: Decimal | None,
    theta: Decimal | None,
    vega: Decimal | None,
) -> OptionMetrics:

    price_change = calculate_price_change(
        last_price,
        previous_price,
    )

    price_change_percent = calculate_price_change_percent(
        last_price,
        previous_price,
    )

    oi_change = calculate_oi_change(
        open_interest,
        previous_open_interest,
    )

    oi_change_percent = calculate_oi_change_percent(
        open_interest,
        previous_open_interest,
    )

    oi_buildup_metrics = calculate_oi_buildup(
        last_price=last_price,
        previous_price=previous_price,
        open_interest=open_interest,
        previous_open_interest=previous_open_interest,
    )

    strike_distance = calculate_strike_distance(
        strike_price,
        underlying_price,
    )

    strike_distance_percent = (
        calculate_strike_distance_percent(
            strike_price,
            underlying_price,
        )
    )

    liquidity_score = calculate_liquidity_score(
        volume,
        open_interest,
    )

    data_quality_score = calculate_data_quality_score(
        last_price,
        volume,
        open_interest,
        implied_volatility,
        delta,
    )

    # Temporary metrics object for signal calculation
    # Signal needs all calculated values.
    temp_option = OptionMetrics(
        trading_symbol=trading_symbol,
        option_type=option_type.upper(),
        strike_price=strike_price,

        underlying_price=underlying_price,
        atm_strike=atm_strike,
        moneyness=moneyness,

        last_price=last_price,
        previous_price=previous_price,
        price_change=price_change,
        price_change_percent=price_change_percent,

        volume=volume,

        open_interest=open_interest,
        previous_open_interest=previous_open_interest,
        oi_change=oi_change,
        oi_change_percent=oi_change_percent,

        oi_buildup=oi_buildup_metrics.classification,

        implied_volatility=implied_volatility,

        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,

        strike_distance=strike_distance,
        strike_distance_percent=strike_distance_percent,

        liquidity_score=liquidity_score,
        data_quality_score=data_quality_score,

        trading_signal="NEUTRAL",
        signal_score=0,
        signal_reasons=[],
    )

    signal_metrics = calculate_trading_signal(
        temp_option
    )

    return OptionMetrics(
        trading_symbol=trading_symbol,
        option_type=option_type.upper(),
        strike_price=strike_price,

        underlying_price=underlying_price,
        atm_strike=atm_strike,
        moneyness=moneyness,

        last_price=last_price,
        previous_price=previous_price,
        price_change=price_change,
        price_change_percent=price_change_percent,

        volume=volume,

        open_interest=open_interest,
        previous_open_interest=previous_open_interest,
        oi_change=oi_change,
        oi_change_percent=oi_change_percent,

        oi_buildup=oi_buildup_metrics.classification,

        implied_volatility=implied_volatility,

        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,

        strike_distance=strike_distance,
        strike_distance_percent=strike_distance_percent,

        liquidity_score=liquidity_score,
        data_quality_score=data_quality_score,

        trading_signal=signal_metrics.signal,
        signal_score=signal_metrics.score,
        signal_reasons=signal_metrics.reasons,
    )