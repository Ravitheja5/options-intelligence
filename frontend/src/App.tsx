import { useEffect, useMemo, useState } from "react";
import "./App.css";

import {
  getLatestMarketData,
  runMarketPipeline,
} from "./services/marketService";

type Page =
  | "dashboard"
  | "signals"
  | "market"
  | "analysis"
  | "chain";

interface MarketRecord {
  type?: string;
  option_type?: string;
  strike?: number;
  expiry?: string;
  ltp?: number;
  oi?: number;
  change_oi?: number;
  volume?: number;
  iv?: number;
  [key: string]: any;
}

function App() {
  const [activePage, setActivePage] =
    useState<Page>("dashboard");

  const [marketData, setMarketData] =
    useState<MarketRecord[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [pipelineLoading, setPipelineLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [selectedUnderlying, setSelectedUnderlying] =
    useState("BANKNIFTY");

  /* ===============================
     LOAD MARKET DATA
  =============================== */

  const loadMarketData = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await getLatestMarketData(
        selectedUnderlying
      );

      console.log(
        "MARKET DATA RESPONSE:",
        response
      );

      let records: any[] = [];

      // Backend response:
      // {
      //   success: true,
      //   data: {
      //     option_chain: [...]
      //   }
      // }

      if (
        response?.success === true &&
        Array.isArray(
          response?.data?.option_chain
        )
      ) {
        records = response.data.option_chain;
      }

      setMarketData(records);

      console.log(
        "OPTIONS LOADED:",
        records.length
      );

    } catch (err: any) {
      console.error(
        "MARKET DATA ERROR:",
        err
      );

      setError(
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to load market data"
      );

      setMarketData([]);

    } finally {
      setLoading(false);
    }
  };

  /* ===============================
     RUN PIPELINE
  =============================== */

  const handleRunPipeline = async () => {
    try {
      setPipelineLoading(true);
      setError("");

      await runMarketPipeline(
        selectedUnderlying
      );

      await new Promise((resolve) =>
        setTimeout(resolve, 1000)
      );

      await loadMarketData();

      setActivePage("market");

    } catch (err: any) {
      console.error(err);

      setError(
        err?.response?.data?.detail ||
        err?.message ||
        "Pipeline execution failed"
      );

    } finally {
      setPipelineLoading(false);
    }
  };

  useEffect(() => {
    loadMarketData();
  }, []);

  /* ===============================
     NORMALIZE DATA
  =============================== */

  const normalizedData = useMemo(() => {
    return marketData.map((item: any) => ({
      ...item,

      type:
        item.type ||
        item.option_type ||
        item.instrument_type ||
        "",

      strike: Number(
        item.strike ||
          item.strike_price ||
          0
      ),

      expiry:
        item.expiry ||
        item.expiry_date ||
        "-",

      ltp: Number(
        item.ltp ||
          item.last_price ||
          item.price ||
          0
      ),

      oi: Number(
        item.oi ||
          item.open_interest ||
          0
      ),

      changeOI: Number(
        item.change_oi ||
          item.change_in_oi ||
          item.oi_change ||
          0
      ),

      volume: Number(item.volume || 0),

      iv: Number(
        item.iv ||
          item.implied_volatility ||
          0
      ),
    }));
  }, [marketData]);

  /* ===============================
     MARKET STATS
  =============================== */

  const totalContracts =
    normalizedData.length;

  const callContracts =
    normalizedData.filter(
      (item) =>
        String(item.type).toUpperCase() === "CE" ||
        String(item.type)
          .toUpperCase()
          .includes("CALL")
    );

  const putContracts =
    normalizedData.filter(
      (item) =>
        String(item.type).toUpperCase() === "PE" ||
        String(item.type)
          .toUpperCase()
          .includes("PUT")
    );

  const totalVolume =
    normalizedData.reduce(
      (total, item) =>
        total + Number(item.volume || 0),
      0
    );

  const totalOI =
    normalizedData.reduce(
      (total, item) =>
        total + Number(item.oi || 0),
      0
    );

  const bullishScore =
    callContracts.length +
    normalizedData.filter(
      (item) => item.changeOI > 0
    ).length;

  const bearishScore =
    putContracts.length;

  let marketSentiment = "NEUTRAL";

  if (bullishScore > bearishScore * 1.2) {
    marketSentiment = "BULLISH";
  } else if (
    bearishScore > bullishScore * 1.2
  ) {
    marketSentiment = "BEARISH";
  }

  /* ===============================
     HELPERS
  =============================== */

  const formatNumber = (value: number) =>
    new Intl.NumberFormat("en-IN").format(
      Number(value || 0)
    );

  const formatPrice = (value: number) =>
    `₹${Number(value || 0).toLocaleString(
      "en-IN",
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }
    )}`;

  const getOptionType = (item: any) => {
    const type = String(
      item.type ||
        item.option_type ||
        ""
    ).toUpperCase();

    if (
      type === "CE" ||
      type.includes("CALL")
    ) {
      return "CE";
    }

    if (
      type === "PE" ||
      type.includes("PUT")
    ) {
      return "PE";
    }

    return type || "-";
  };

  /* ===============================
     DASHBOARD
  =============================== */

  const renderDashboard = () => (
    <div className="terminal-page">

      <div className="terminal-header">
        <div>
          <div className="terminal-label">
            MARKET INTELLIGENCE
          </div>

          <h1>Options Trading Terminal</h1>

          <p>
            Live options market monitoring,
            open interest analysis and trading signals.
          </p>
        </div>

        <div className="header-actions">

          <select
            value={selectedUnderlying}
            onChange={(e) =>
              setSelectedUnderlying(e.target.value)
            }
            className="underlying-select"
          >
            <option>BANKNIFTY</option>
            <option>NIFTY</option>
            <option>FINNIFTY</option>
            <option>SENSEX</option>
          </select>

          <button
            className="run-button"
            onClick={handleRunPipeline}
            disabled={pipelineLoading}
          >
            {pipelineLoading
              ? "Running..."
              : "▶ Run Pipeline"}
          </button>

        </div>
      </div>

      <div className="market-strip">

        <div className="market-strip-item">
          <span>UNDERLYING</span>
          <strong>{selectedUnderlying}</strong>
        </div>

        <div className="market-strip-item">
          <span>CONTRACTS</span>
          <strong>
            {formatNumber(totalContracts)}
          </strong>
        </div>

        <div className="market-strip-item">
          <span>TOTAL OI</span>
          <strong>
            {formatNumber(totalOI)}
          </strong>
        </div>

        <div className="market-strip-item">
          <span>VOLUME</span>
          <strong>
            {formatNumber(totalVolume)}
          </strong>
        </div>

        <div className="market-strip-item sentiment-item">
          <span>MARKET BIAS</span>

          <strong
            className={
              marketSentiment === "BULLISH"
                ? "green"
                : marketSentiment === "BEARISH"
                ? "red"
                : "yellow"
            }
          >
            {marketSentiment}
          </strong>
        </div>

      </div>

      <div className="terminal-grid">

        <div className="terminal-panel">

          <div className="panel-header">
            <div>
              <span className="panel-label">
                MARKET SUMMARY
              </span>

              <h2>
                Current Market Snapshot
              </h2>
            </div>

            <button
              className="ghost-button"
              onClick={() =>
                setActivePage("market")
              }
            >
              View Data →
            </button>
          </div>

          <div className="summary-metrics">

            <div className="metric">
              <span>CALL CONTRACTS</span>
              <strong className="green">
                {formatNumber(
                  callContracts.length
                )}
              </strong>
            </div>

            <div className="metric">
              <span>PUT CONTRACTS</span>
              <strong className="red">
                {formatNumber(
                  putContracts.length
                )}
              </strong>
            </div>

            <div className="metric">
              <span>DATA STATUS</span>
              <strong className="yellow">
                {totalContracts > 0
                  ? "LIVE DATA"
                  : "NO DATA"}
              </strong>
            </div>

          </div>
        </div>

        <div className="terminal-panel">

          <span className="panel-label">
            TRADING SIGNAL
          </span>

          <div className="sentiment-main">

            <div
              className={`sentiment-circle ${marketSentiment.toLowerCase()}`}
            >
              {marketSentiment === "BULLISH"
                ? "▲"
                : marketSentiment === "BEARISH"
                ? "▼"
                : "●"}
            </div>

            <div>
              <h2
                className={
                  marketSentiment === "BULLISH"
                    ? "green"
                    : marketSentiment === "BEARISH"
                    ? "red"
                    : "yellow"
                }
              >
                {marketSentiment}
              </h2>

              <p>
                Based on options activity
                and open interest analysis.
              </p>
            </div>

          </div>

          <button
            className="analysis-button"
            onClick={() =>
              setActivePage("analysis")
            }
          >
            Open Market Analysis →
          </button>

        </div>

      </div>

      <div className="terminal-panel action-terminal">

        <div className="panel-header">
          <div>
            <span className="panel-label">
              QUICK ACCESS
            </span>

            <h2>Trading Workspace</h2>
          </div>
        </div>

        <div className="terminal-actions">

          <button onClick={handleRunPipeline}>
            <span>⚡</span>
            <div>
              <strong>Refresh Market</strong>
              <small>Run latest pipeline</small>
            </div>
          </button>

          <button
            onClick={() =>
              setActivePage("market")
            }
          >
            <span>▦</span>
            <div>
              <strong>Market Data</strong>
              <small>View contracts</small>
            </div>
          </button>

          <button
            onClick={() =>
              setActivePage("chain")
            }
          >
            <span>◫</span>
            <div>
              <strong>Options Chain</strong>
              <small>Calls and puts</small>
            </div>
          </button>

          <button
            onClick={() =>
              setActivePage("signals")
            }
          >
            <span>⚡</span>
            <div>
              <strong>Trading Signals</strong>
              <small>Market direction</small>
            </div>
          </button>

        </div>

      </div>

    </div>
  );

  /* ===============================
     MARKET DATA
  =============================== */

  const renderMarketData = () => (
    <div className="terminal-page">

      <div className="terminal-header">

        <div>
          <div className="terminal-label">
            MARKET DATA TERMINAL
          </div>

          <h1>Options Market Data</h1>

          <p>
            Latest options contracts from
            the market pipeline.
          </p>
        </div>

        <div className="header-actions">

          <div className="live-indicator">
            <span></span>
            DATA AVAILABLE
          </div>

          <button
            className="run-button"
            onClick={handleRunPipeline}
            disabled={pipelineLoading}
          >
            {pipelineLoading
              ? "Refreshing..."
              : "↻ Refresh"}
          </button>

        </div>

      </div>

      {loading && (
        <div className="terminal-loading">
          Loading market data...
        </div>
      )}

      {!loading &&
        totalContracts === 0 && (
          <div className="terminal-empty">

            <div className="empty-icon">
              ◫
            </div>

            <h2>
              No Market Data Available
            </h2>

            <p>
              Run the market pipeline to
              fetch the latest options data.
            </p>

            <button
              className="run-button"
              onClick={handleRunPipeline}
            >
              ▶ Run Market Pipeline
            </button>

          </div>
        )}

      {totalContracts > 0 && (

        <div className="market-table-terminal">

          <div className="table-terminal-header">

            <div>
              <span className="panel-label">
                LIVE CONTRACTS
              </span>

              <h2>
                {selectedUnderlying} Options
              </h2>
            </div>

            <div className="record-count">
              {formatNumber(totalContracts)} RECORDS
            </div>

          </div>

          <div className="terminal-table-wrapper">

            <table className="terminal-table">

              <thead>
                <tr>
                  <th>TYPE</th>
                  <th>STRIKE</th>
                  <th>EXPIRY</th>
                  <th>LTP</th>
                  <th>OPEN INTEREST</th>
                  <th>CHANGE OI</th>
                  <th>VOLUME</th>
                  <th>IV</th>
                </tr>
              </thead>

              <tbody>

                {normalizedData.map(
                  (item, index) => {

                    const optionType =
                      getOptionType(item);

                    return (
                      <tr key={index}>

                        <td>
                          <span
                            className={`option-tag ${
                              optionType === "CE"
                                ? "call-tag"
                                : "put-tag"
                            }`}
                          >
                            {optionType}
                          </span>
                        </td>

                        <td className="strike-cell">
                          {formatPrice(item.strike)}
                        </td>

                        <td>{item.expiry}</td>

                        <td className="price-cell">
                          {formatPrice(item.ltp)}
                        </td>

                        <td>
                          {formatNumber(item.oi)}
                        </td>

                        <td
                          className={
                            item.changeOI > 0
                              ? "green"
                              : item.changeOI < 0
                              ? "red"
                              : ""
                          }
                        >
                          {item.changeOI > 0
                            ? "+"
                            : ""}

                          {formatNumber(
                            item.changeOI
                          )}
                        </td>

                        <td>
                          {formatNumber(item.volume)}
                        </td>

                        <td>
                          {Number(item.iv || 0).toFixed(2)}%
                        </td>

                      </tr>
                    );
                  }
                )}

              </tbody>

            </table>

          </div>

        </div>
      )}

    </div>
  );

  /* ===============================
     SIGNALS
  =============================== */

  const renderSignals = () => (
    <div className="terminal-page">

      <div className="terminal-header">
        <div>
          <div className="terminal-label">
            SIGNAL ENGINE
          </div>

          <h1>Trading Signals</h1>

          <p>
            Market direction based on options
            activity and open interest.
          </p>
        </div>
      </div>

      <div className="signals-terminal-grid">

        <div className="signal-terminal-card bullish-card">

          <div className="signal-card-top">
            <span>▲</span>
            <small>BULLISH SIGNAL</small>
          </div>

          <h2>
            {marketSentiment === "BULLISH"
              ? "ACTIVE"
              : "MONITORING"}
          </h2>

          <p>
            Call-side activity and market
            strength indicators.
          </p>

          <strong>
            Score: {bullishScore}
          </strong>

        </div>

        <div className="signal-terminal-card neutral-card">

          <div className="signal-card-top">
            <span>●</span>
            <small>MARKET STATUS</small>
          </div>

          <h2>{marketSentiment}</h2>

          <p>
            Current calculated market bias.
          </p>

          <strong>
            Contracts: {totalContracts}
          </strong>

        </div>

        <div className="signal-terminal-card bearish-card">

          <div className="signal-card-top">
            <span>▼</span>
            <small>BEARISH SIGNAL</small>
          </div>

          <h2>
            {marketSentiment === "BEARISH"
              ? "ACTIVE"
              : "MONITORING"}
          </h2>

          <p>
            Put-side activity and downside
            market indicators.
          </p>

          <strong>
            Score: {bearishScore}
          </strong>

        </div>

      </div>

    </div>
  );

  /* ===============================
     ANALYSIS
  =============================== */

  const renderAnalysis = () => {

    const maxOI = Math.max(
      ...normalizedData.map(
        (item) => item.oi
      ),
      0
    );

    return (
      <div className="terminal-page">

        <div className="terminal-header">
          <div>
            <div className="terminal-label">
              MARKET ANALYTICS
            </div>

            <h1>Options Analysis</h1>

            <p>
              Open interest and market
              structure analysis.
            </p>
          </div>
        </div>

        <div className="analysis-terminal-grid">

          <div className="terminal-panel">

            <span className="panel-label">
              MARKET BIAS
            </span>

            <h2
              className={
                marketSentiment === "BULLISH"
                  ? "green"
                  : marketSentiment === "BEARISH"
                  ? "red"
                  : "yellow"
              }
            >
              {marketSentiment}
            </h2>

            <p className="analysis-description">
              Current sentiment calculated from
              available options market records.
            </p>

          </div>

          <div className="terminal-panel">

            <span className="panel-label">
              CALL / PUT DATA
            </span>

            <div className="ratio-display">

              <div>
                <small>CALLS</small>
                <strong className="green">
                  {callContracts.length}
                </strong>
              </div>

              <div className="ratio-divider"></div>

              <div>
                <small>PUTS</small>
                <strong className="red">
                  {putContracts.length}
                </strong>
              </div>

            </div>

          </div>

        </div>

        <div className="terminal-panel oi-analysis">

          <div className="panel-header">
            <div>
              <span className="panel-label">
                OPEN INTEREST ANALYSIS
              </span>

              <h2>
                Highest OI Contracts
              </h2>
            </div>
          </div>

          <div className="oi-list">

            {[...normalizedData]
              .sort((a, b) => b.oi - a.oi)
              .slice(0, 10)
              .map((item, index) => (

                <div
                  className="oi-row"
                  key={index}
                >

                  <div className="oi-contract">

                    <span
                      className={
                        getOptionType(item) === "CE"
                          ? "green"
                          : "red"
                      }
                    >
                      {getOptionType(item)}
                    </span>

                    <strong>
                      ₹{formatNumber(item.strike)}
                    </strong>

                  </div>

                  <div className="oi-bar-container">
                    <div
                      className="oi-bar"
                      style={{
                        width: `${
                          maxOI
                            ? (item.oi / maxOI) * 100
                            : 0
                        }%`,
                      }}
                    />
                  </div>

                  <strong>
                    {formatNumber(item.oi)}
                  </strong>

                </div>

              ))}

          </div>

        </div>

      </div>
    );
  };

  /* ===============================
     OPTIONS CHAIN
  =============================== */

  const renderOptionsChain = () => {

    const strikes = Array.from(
      new Set(
        normalizedData.map(
          (item) => item.strike
        )
      )
    )
      .filter(Boolean)
      .sort((a, b) => a - b);

    return (
      <div className="terminal-page">

        <div className="terminal-header">
          <div>
            <div className="terminal-label">
              OPTIONS CHAIN
            </div>

            <h1>
              {selectedUnderlying} Chain
            </h1>

            <p>
              Call and Put contracts by strike.
            </p>
          </div>
        </div>

        {strikes.length === 0 ? (

          <div className="terminal-empty">

            <div className="empty-icon">
              ◫
            </div>

            <h2>
              Options Chain Not Available
            </h2>

            <p>
              Load market data first.
            </p>

            <button
              className="run-button"
              onClick={handleRunPipeline}
            >
              ▶ Run Pipeline
            </button>

          </div>

        ) : (

          <div className="chain-terminal">

            <div className="chain-terminal-header">

              <div className="call-chain-title">
                CALLS
              </div>

              <div className="strike-chain-title">
                STRIKE
              </div>

              <div className="put-chain-title">
                PUTS
              </div>

            </div>

            <div className="chain-columns-label">

              <span>OI &nbsp;&nbsp; LTP</span>

              <span>STRIKE PRICE</span>

              <span>LTP &nbsp;&nbsp; OI</span>

            </div>

            {strikes.map((strike) => {

              const call =
                normalizedData.find(
                  (item) =>
                    item.strike === strike &&
                    getOptionType(item) === "CE"
                );

              const put =
                normalizedData.find(
                  (item) =>
                    item.strike === strike &&
                    getOptionType(item) === "PE"
                );

              return (

                <div
                  className="chain-terminal-row"
                  key={strike}
                >

                  <div className="chain-call">

                    <span>
                      {call
                        ? formatNumber(call.oi)
                        : "-"}
                    </span>

                    <strong>
                      {call
                        ? formatPrice(call.ltp)
                        : "-"}
                    </strong>

                  </div>

                  <div className="chain-strike">
                    ₹{formatNumber(strike)}
                  </div>

                  <div className="chain-put">

                    <strong>
                      {put
                        ? formatPrice(put.ltp)
                        : "-"}
                    </strong>

                    <span>
                      {put
                        ? formatNumber(put.oi)
                        : "-"}
                    </span>

                  </div>

                </div>
              );
            })}

          </div>
        )}

      </div>
    );
  };

  const renderPage = () => {
    switch (activePage) {
      case "dashboard":
        return renderDashboard();

      case "market":
        return renderMarketData();

      case "signals":
        return renderSignals();

      case "analysis":
        return renderAnalysis();

      case "chain":
        return renderOptionsChain();

      default:
        return renderDashboard();
    }
  };

  return (
    <div className="app-shell">

      {/* SIDEBAR */}

      <aside className="terminal-sidebar">

        <div className="terminal-logo">

          <div className="logo-mark">
            ↗
          </div>

          <div>
            <h2>OPTIONS</h2>
            <span>INTELLIGENCE</span>
          </div>

        </div>

        <div className="sidebar-section-title">
          WORKSPACE
        </div>

        <nav className="terminal-navigation">

          <button
            className={
              activePage === "dashboard"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("dashboard")
            }
          >
            <span>▦</span>
            Dashboard
          </button>

          <button
            className={
              activePage === "signals"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("signals")
            }
          >
            <span>⚡</span>
            Trading Signals
          </button>

          <button
            className={
              activePage === "market"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("market")
            }
          >
            <span>▤</span>
            Market Data
          </button>

          <button
            className={
              activePage === "analysis"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("analysis")
            }
          >
            <span>◔</span>
            Analysis
          </button>

          <button
            className={
              activePage === "chain"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("chain")
            }
          >
            <span>◫</span>
            Options Chain
          </button>

        </nav>

        <div className="sidebar-bottom">

          <div className="api-status">

            <div className="api-status-dot"></div>

            <div>
              <small>BACKEND API</small>
              <strong>CONNECTED</strong>
            </div>

          </div>

          <div className="data-info">

            <span>DATA RECORDS</span>

            <strong>
              {formatNumber(totalContracts)}
            </strong>

          </div>

        </div>

      </aside>

      {/* MAIN */}

      <main className="terminal-main">

        {error && (

          <div className="terminal-error">

            <div>
              <strong>
                CONNECTION ERROR
              </strong>

              <span>{error}</span>
            </div>

            <button
              onClick={() =>
                setError("")
              }
            >
              ×
            </button>

          </div>

        )}

        {renderPage()}

      </main>

    </div>
  );
}

export default App;