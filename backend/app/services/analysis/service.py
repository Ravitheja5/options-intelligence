from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.option_chain_snapshot import OptionChainSnapshot
from app.models.option_contract import OptionContract
from app.models.underlying import Underlying

from app.services.analysis.atm import calculate_atm_strike

from app.services.analysis.moneyness import (
    classify_moneyness,
)
from app.services.analysis.recommendation import (
    TradingRecommendation,
    calculate_trading_recommendation,
)

from app.services.analysis.metrics import (
    OptionMetrics,
    build_option_metrics,
)

from app.services.analysis.pcr import (
    PCRMetrics,
    calculate_pcr_metrics,
)

from app.services.analysis.support_resistance import (
    SupportResistanceMetrics,
    calculate_support_resistance,
)

from app.services.analysis.max_pain import (
    MaxPainMetrics,
    calculate_max_pain,
)

from app.services.analysis.sentiment import (
    MarketSentimentMetrics,
    calculate_market_sentiment,
)


class AnalysisService:

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # SNAPSHOTS
    # =========================================================

    def get_latest_snapshots(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> list[
        tuple[
            OptionContract,
            OptionChainSnapshot,
            OptionChainSnapshot | None,
        ]
    ]:

        symbol = underlying_symbol.upper().strip()

        query = (
            select(
                OptionContract,
                OptionChainSnapshot,
            )
            .join(
                OptionChainSnapshot,
                OptionChainSnapshot.option_contract_id
                == OptionContract.id,
            )
            .join(
                Underlying,
                Underlying.id
                == OptionContract.underlying_id,
            )
            .where(
                Underlying.symbol == symbol,
                Underlying.is_active.is_(True),
                OptionContract.is_active.is_(True),
            )
        )

        if expiry_date is not None:
            query = query.where(
                OptionContract.expiry_date == expiry_date
            )

        query = query.order_by(
            OptionChainSnapshot.option_contract_id,
            OptionChainSnapshot.snapshot_time.desc(),
        )

        rows = self.db.execute(query).all()

        snapshots_by_contract: dict[
            int,
            list[OptionChainSnapshot],
        ] = {}

        contracts_by_id: dict[
            int,
            OptionContract,
        ] = {}

        for contract, snapshot in rows:

            contracts_by_id[contract.id] = contract

            snapshots_by_contract.setdefault(
                contract.id,
                [],
            )

            if len(
                snapshots_by_contract[contract.id]
            ) < 2:
                snapshots_by_contract[
                    contract.id
                ].append(snapshot)

        result = []

        for contract_id, snapshots in (
            snapshots_by_contract.items()
        ):

            contract = contracts_by_id[contract_id]

            latest_snapshot = snapshots[0]

            previous_snapshot = (
                snapshots[1]
                if len(snapshots) > 1
                else None
            )

            result.append(
                (
                    contract,
                    latest_snapshot,
                    previous_snapshot,
                )
            )

        return result

    # =========================================================
    # OPTION CHAIN ANALYSIS
    # =========================================================

    def analyze_option_chain(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> list[OptionMetrics]:

        rows = self.get_latest_snapshots(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        if not rows:
            return []

        underlying_price: Decimal | None = None

        for _, snapshot, _ in rows:

            if snapshot.underlying_price is not None:
                underlying_price = snapshot.underlying_price
                break

        strikes = sorted(
            {
                contract.strike_price
                for contract, _, _ in rows
                if contract.strike_price is not None
            }
        )

        atm_strike = calculate_atm_strike(
            underlying_price=underlying_price,
            strikes=strikes,
        )

        metrics: list[OptionMetrics] = []

        for (
            contract,
            latest_snapshot,
            previous_snapshot,
        ) in rows:

            previous_price = None
            previous_open_interest = None

            if previous_snapshot is not None:

                previous_price = (
                    previous_snapshot.last_price
                )

                previous_open_interest = (
                    previous_snapshot.open_interest
                )

            if atm_strike is not None:

                moneyness = classify_moneyness(
                    option_type=contract.option_type,
                    strike_price=contract.strike_price,
                    atm_strike=atm_strike,
                )

            else:
                moneyness = "UNKNOWN"

            metric = build_option_metrics(
                trading_symbol=contract.trading_symbol,
                option_type=contract.option_type,
                strike_price=contract.strike_price,

                underlying_price=(
                    latest_snapshot.underlying_price
                ),

                atm_strike=atm_strike,
                moneyness=moneyness,

                last_price=latest_snapshot.last_price,
                previous_price=previous_price,

                volume=latest_snapshot.volume,

                open_interest=(
                    latest_snapshot.open_interest
                ),

                previous_open_interest=(
                    previous_open_interest
                ),

                implied_volatility=(
                    latest_snapshot.implied_volatility
                ),

                delta=latest_snapshot.delta,
                gamma=latest_snapshot.gamma,
                theta=latest_snapshot.theta,
                vega=latest_snapshot.vega,
            )

            metrics.append(metric)

        return metrics

    # =========================================================
    # PCR
    # =========================================================

    def get_pcr_metrics(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> PCRMetrics | None:

        options = self.analyze_option_chain(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        if not options:
            return None

        return calculate_pcr_metrics(options)

    # =========================================================
    # SUPPORT / RESISTANCE
    # =========================================================

    def get_support_resistance(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> SupportResistanceMetrics | None:

        options = self.analyze_option_chain(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        if not options:
            return None

        return calculate_support_resistance(options)

    # =========================================================
    # MAX PAIN
    # =========================================================

    def get_max_pain(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> MaxPainMetrics | None:

        options = self.analyze_option_chain(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        if not options:
            return None

        return calculate_max_pain(options)

    # =========================================================
    # MARKET SENTIMENT
    # =========================================================

    def get_market_sentiment(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> MarketSentimentMetrics | None:

        options = self.analyze_option_chain(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        if not options:
            return None

        pcr = calculate_pcr_metrics(
            options
        )

        support_resistance = (
            calculate_support_resistance(
                options
            )
        )

        max_pain = calculate_max_pain(
            options
        )

        underlying_price = (
            options[0].underlying_price
        )

        return calculate_market_sentiment(
            options=options,
            pcr=pcr,
            support_resistance=support_resistance,
            max_pain=max_pain,
            underlying_price=underlying_price,
        )

    def get_trading_recommendation(
        self,
        underlying_symbol: str,
        expiry_date: date | None = None,
    ) -> TradingRecommendation:

        pcr = self.get_pcr_metrics(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        support_resistance = self.get_support_resistance(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        market_sentiment = self.get_market_sentiment(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        options = self.analyze_option_chain(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
        )

        underlying_price = None

        if options:
            underlying_price = options[0].underlying_price

        return calculate_trading_recommendation(
            market_sentiment=market_sentiment,
            pcr=pcr,
            support_resistance=support_resistance,
            underlying_price=underlying_price,
        )