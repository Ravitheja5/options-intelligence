export interface TradingSignal {
  strategy_name: string;
  trading_symbol: string;
  option_type: string;
  strike_price: number;
  signal: string;
  score: number;
  reason: string;
  last_price: number | null;
  volume: number | null;
  open_interest: number | null;
  oi_change: number | null;
  liquidity_score: number | null;
  moneyness: string;
}

interface SignalsResponse {
  success: boolean;
  underlying_symbol: string;
  total_signals: number;
  signals: TradingSignal[];
}

const API_BASE_URL = "http://127.0.0.1:8000";

export async function getTradingSignals(
  underlyingSymbol: string = "NIFTY"
): Promise<SignalsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/signals?underlying_symbol=${underlyingSymbol}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch trading signals");
  }

  return response.json();
}