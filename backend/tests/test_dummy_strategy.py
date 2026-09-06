from decimal import Decimal

from app.services.analysis.metrics import build_option_metrics
from app.services.strategies.implementations.oi_momentum import (
    OIMomentumStrategy,
)


def main():

    # =========================================================
    # DUMMY PROFITABLE OPTION
    # =========================================================

    option = build_option_metrics(

        # CONTRACT
        trading_symbol="NIFTY08SEP24800CE",
        option_type="CE",
        strike_price=Decimal("24800"),

        # UNDERLYING
        underlying_price=Decimal("24800"),
        atm_strike=Decimal("24800"),
        moneyness="ATM",

        # PRICE
        last_price=Decimal("150"),
        previous_price=Decimal("120"),

        # HIGH VOLUME
        volume=500000,

        # OPEN INTEREST
        open_interest=100000,
        previous_open_interest=85000,

        # IV
        implied_volatility=Decimal("15.50"),

        # GREEKS
        delta=Decimal("0.65"),
        gamma=Decimal("0.02"),
        theta=Decimal("-8.50"),
        vega=Decimal("12.00"),
    )

    # =========================================================
    # PRINT OPTION METRICS
    # =========================================================

    print()
    print("=" * 60)
    print("DUMMY OPTION ANALYSIS")
    print("=" * 60)

    print(f"Symbol: {option.trading_symbol}")
    print(f"Option Type: {option.option_type}")
    print(f"Strike: {option.strike_price}")
    print()

    print("PRICE ANALYSIS")
    print(f"LTP: {option.last_price}")
    print(f"Previous Price: {option.previous_price}")
    print(f"Price Change: {option.price_change}")
    print(
        f"Price Change %: "
        f"{option.price_change_percent}"
    )

    print()
    print("OI ANALYSIS")
    print(f"Open Interest: {option.open_interest}")
    print(
        f"Previous OI: "
        f"{option.previous_open_interest}"
    )
    print(f"OI Change: {option.oi_change}")
    print(
        f"OI Change %: "
        f"{option.oi_change_percent}"
    )
    print(f"OI Buildup: {option.oi_buildup}")

    print()
    print("QUALITY")
    print(f"Liquidity Score: {option.liquidity_score}")
    print(
        f"Data Quality Score: "
        f"{option.data_quality_score}"
    )

    print()
    print("TRADING SIGNAL ENGINE")
    print(f"Signal: {option.trading_signal}")
    print(f"Signal Score: {option.signal_score}")

    print("Reasons:")

    for reason in option.signal_reasons:
        print(f"  ✅ {reason}")

    # =========================================================
    # RUN STRATEGY
    # =========================================================

    strategy = OIMomentumStrategy()

    strategy_signal = strategy.evaluate(option)

    print()
    print("=" * 60)
    print("OI MOMENTUM STRATEGY RESULT")
    print("=" * 60)

    if strategy_signal is None:

        print("❌ NO STRATEGY SIGNAL GENERATED")

    else:

        print("🔥 STRATEGY SIGNAL GENERATED")

        print(
            f"Strategy: "
            f"{strategy_signal.strategy_name}"
        )

        print(
            f"Signal: "
            f"{strategy_signal.signal}"
        )

        print(
            f"Score: "
            f"{strategy_signal.score}"
        )

        print(
            f"Reason: "
            f"{strategy_signal.reason}"
        )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
