from datetime import date

from app.services.market_data.ingestion import ingest_option_chain
from app.services.strategies.runner import StrategyRunner


class MarketPipeline:

    # ========================================================
    # SINGLE UNDERLYING PIPELINE
    # ========================================================

    async def run(
        self,
        underlying_symbol: str,
        expiry_date: date,
    ):

        symbol = underlying_symbol.upper().strip()

        # ========================================================
        # STEP 1: FETCH + SAVE REAL MARKET DATA
        # ========================================================

        saved_count = await ingest_option_chain(
            symbol,
            expiry_date,
        )

        # ========================================================
        # STEP 2: RUN STRATEGIES
        # ========================================================

        strategy_runner = StrategyRunner()

        signals = strategy_runner.run(
            underlying_symbol=symbol,
            expiry_date=expiry_date,
        )

        # ========================================================
        # RESULT
        # ========================================================

        return {
            "underlying_symbol": symbol,
            "expiry_date": expiry_date,
            "quotes_saved": saved_count,
            "signals_count": len(signals),
            "signals": signals,
        }

    # ========================================================
    # MULTI UNDERLYING PIPELINE
    # ========================================================

    async def run_multiple(
        self,
        markets: list[dict],
    ):

        results = []

        total_quotes_saved = 0
        total_signals = 0

        for market in markets:

            underlying_symbol = market.get(
                "underlying_symbol"
            )

            expiry_date = market.get(
                "expiry_date"
            )

            if not underlying_symbol or not expiry_date:
                continue

            try:

                result = await self.run(
                    underlying_symbol=underlying_symbol,
                    expiry_date=expiry_date,
                )

                results.append(result)

                total_quotes_saved += result[
                    "quotes_saved"
                ]

                total_signals += result[
                    "signals_count"
                ]

            except Exception as error:

                results.append(
                    {
                        "underlying_symbol": underlying_symbol,
                        "expiry_date": expiry_date,
                        "success": False,
                        "error": str(error),
                    }
                )

        return {
            "markets_processed": len(results),
            "total_quotes_saved": total_quotes_saved,
            "total_signals": total_signals,
            "results": results,
        }