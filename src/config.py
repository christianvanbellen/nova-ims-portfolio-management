"""Single source of truth for the investable universe and every fixed convention.

Mirrors `docs/project-definitions.md`. If a convention changes, change the
definitions file first, then this module -- nothing else hardcodes a ticker.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# 1. Investable universe (definitions SS1)
# --------------------------------------------------------------------------- #

#: The six assets strategies may allocate to. Order is the fixed asset order used
#: in every table and figure in the report.
UNIVERSE: dict[str, dict[str, str]] = {
    "GC=F": {
        "name": "Gold, COMEX continuous front-month",
        "asset_class": "Commodity",
        "instrument": "Futures proxy",
        "proxy_for": "Spot gold exposure; investable counterpart GLD or IAU",
    },
    "GOVT": {
        "name": "iShares US Treasury Bond ETF",
        "asset_class": "Government bonds",
        "instrument": "ETF",
        "proxy_for": None,
    },
    "TSM": {
        "name": "Taiwan Semiconductor Manufacturing",
        "asset_class": "Equity -- semiconductors",
        "instrument": "ADR",
        "proxy_for": None,
    },
    "VNQ": {
        "name": "Vanguard Real Estate Index Fund ETF",
        "asset_class": "Real estate / REITs",
        "instrument": "ETF",
        "proxy_for": None,
    },
    "RNMBY": {
        "name": "Rheinmetall AG",
        "asset_class": "Equity -- defence",
        "instrument": "ADR",
        "proxy_for": None,
    },
    "BTC-USD": {
        "name": "Bitcoin",
        "asset_class": "Cryptoasset",
        "instrument": "Spot proxy",
        "proxy_for": "Spot bitcoin; not investable via a US product before the Jan-2024 spot ETFs",
    },
}

#: Fixed asset order for every table and figure.
ASSET_ORDER: list[str] = list(UNIVERSE)

#: The single share the stylised-facts section analyses (definitions SS1).
STYLISED_FACTS_TICKER = "TSM"

# --------------------------------------------------------------------------- #
# 2. Benchmarks and risk-free (definitions SS2)
# --------------------------------------------------------------------------- #

#: Held *outside* the universe -- no strategy may allocate to these.
BENCHMARKS: dict[str, dict[str, str]] = {
    "^GSPC": {
        "name": "S&P 500 price index",
        "investable": False,
        "use": "Quoted when describing 'the market'; excludes dividends",
    },
    "SPY": {
        "name": "SPDR S&P 500 ETF Trust",
        "investable": True,
        "use": "Every performance comparison; also defines the NYSE trading calendar",
    },
}

#: The ticker whose trading days define the NYSE calendar (definitions SS4).
CALENDAR_TICKER = "SPY"

#: The benchmark used in performance tables -- total return, so not ^GSPC.
PERFORMANCE_BENCHMARK = "SPY"

#: 13-week T-bill yield, quoted as an annualised percent (definitions SS5).
RISK_FREE_TICKER = "^IRX"

#: Everything downloaded in one call.
ALL_TICKERS: list[str] = ASSET_ORDER + list(BENCHMARKS) + [RISK_FREE_TICKER]

# --------------------------------------------------------------------------- #
# 3. Panel and calendar (definitions SS4)
# --------------------------------------------------------------------------- #

PANEL_START = "2011-10-01"  # 15 years of span, per the brief
FULL_PANEL_START = "2014-09-17"  # first date all six assets have data
FFILL_LIMIT = 3  # interior gaps longer than this are reported, not patched
MIN_YEARS_REQUIRED = 15  # the brief's minimum history

# --------------------------------------------------------------------------- #
# 4. Returns (definitions SS5)
# --------------------------------------------------------------------------- #

TRADING_DAYS = 252
#: pandas resample rules. Weeks end Friday; months on the last trading day.
FREQUENCIES: dict[str, str | None] = {"daily": None, "weekly": "W-FRI", "monthly": "ME"}
FREQUENCY_ORDER: list[str] = list(FREQUENCIES)
#: Periods per year, used to annualise at each frequency.
PERIODS_PER_YEAR: dict[str, int] = {"daily": 252, "weekly": 52, "monthly": 12}

# --------------------------------------------------------------------------- #
# 5. Transaction costs (definitions SS6)
# --------------------------------------------------------------------------- #

#: One-way cost in basis points of traded notional.
COSTS_BP: dict[str, float] = {
    "GC=F": 2.0,
    "GOVT": 2.0,
    "VNQ": 3.0,
    "TSM": 5.0,
    "BTC-USD": 25.0,
    "RNMBY": 30.0,
}
COST_STRESS_MULTIPLIER = 2.0  # the robustness re-run (workstream F)

# --------------------------------------------------------------------------- #
# 6. Backtest parameters (definitions SS7)
# --------------------------------------------------------------------------- #

SEED = 20261001
N_EXPERIMENTS = 100
WINDOW_YEARS = 3
ESTIMATION_YEARS = 2
EVALUATION_YEARS = 1
SUBSET_SIZE = 4
REBALANCE_FREQ = "quarterly"
REBALANCES_PER_YEAR: dict[str, int] = {"monthly": 12, "quarterly": 4, "annual": 1}
REFIT_LOOKBACK_YEARS = 1  # trailing window for every re-estimate after the first
EXECUTION_LAG = 1  # sessions between the formation close and the trade
MV_RISK_AVERSION = 3.0  # lambda, so that MV != GMV != MSR

#: Fixed strategy order for every table and figure. EW first -- it is the benchmark.
STRATEGY_ORDER: list[str] = ["EW", "GMV", "MV", "MSR", "IV", "ERC", "MDP", "MDC"]

# --------------------------------------------------------------------------- #
# 7. Plotting (plan SS1, "Figures")
# --------------------------------------------------------------------------- #

#: One fixed colour per asset, used identically in every figure in the report.
#: Slots 1-6 of a validated categorical palette, in its validated order.
ASSET_COLORS: dict[str, str] = {
    "GC=F": "#2a78d6",    # blue
    "GOVT": "#eb6834",    # orange
    "TSM": "#1baf7a",     # aqua
    "VNQ": "#eda100",     # yellow
    "RNMBY": "#e87ba4",   # magenta
    "BTC-USD": "#008300", # green
}

#: Benchmarks read as a reference line, not a competitor: neutral grey, dashed.
BENCHMARK_COLOR = "#52514e"

#: One fixed colour per strategy. EW is the brief's benchmark, so it takes the
#: benchmark grey. The other seven take slots 1-7 of the same validated palette,
#: in order. Strategies and assets never share a figure, so reusing the slots
#: cannot confuse the two.
STRATEGY_COLORS: dict[str, str] = {
    "EW": BENCHMARK_COLOR,
    "GMV": "#2a78d6",   # blue
    "MV": "#eb6834",    # orange
    "MSR": "#1baf7a",   # aqua
    "IV": "#eda100",    # yellow
    "ERC": "#e87ba4",   # magenta
    "MDP": "#008300",   # green
    "MDC": "#4a3aa7",   # violet
}
BENCHMARK_STYLE: dict[str, object] = {"color": BENCHMARK_COLOR, "linestyle": "--", "linewidth": 1.8}

#: Diverging pair for correlation heatmaps, with a neutral grey midpoint at 0.
DIVERGING_LOW = "#2a78d6"   # blue
DIVERGING_MID = "#f0efec"   # neutral grey
DIVERGING_HIGH = "#e34948"  # red

INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID_COLOR = "#dcdbd6"
SURFACE = "#ffffff"
