export interface Underlying {
  symbol: string;
  name?: string;
  price?: number;
}

export interface Option {
  trading_symbol: string;
  underlying_symbol: string;
  strike_price: number;
  option_type: string;
  expiry_date: string;

  last_price?: number;
  open_interest?: number;
  change_in_oi?: number;

  volume?: number;

  implied_volatility?: number;
}

export interface OptionAnalysis {
  trading_symbol: string;

  signal: string;
  score: number;

  reasons: string[];

  oi_buildup?: string;
  liquidity_score?: number;
  data_quality_score?: number;

  moneyness?: string;

  price_change_percent?: number;
}
