import api from "./api";

export const runMarketPipeline = async (
  underlyingSymbol: string = "NIFTY",
  expiryDate: string = "2026-09-08"
) => {
  const response = await api.post(
    "/api/v1/market/run",
    null,
    {
      params: {
        underlying_symbol: underlyingSymbol,
        expiry_date: expiryDate,
      },
    }
  );

  return response.data;
};


export const getLatestMarketData = async (
  underlyingSymbol: string = "NIFTY",
  expiryDate: string = "2026-09-08"
) => {
  const response = await api.get(
    "/api/v1/market/data",
    {
      params: {
        underlying_symbol: underlyingSymbol,
        expiry_date: expiryDate,
      },
    }
  );

  return response.data;
};


export const getOptionAnalysis = async () => {
  const response = await api.get(
    "/api/v1/analysis/options"
  );

  return response.data;
};