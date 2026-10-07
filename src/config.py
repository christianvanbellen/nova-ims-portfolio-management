"""Single source of truth for the investable universe and every fixed convention.

Mirrors `docs/project-definitions.md`. If a convention changes, change the
definitions file first, then this module -- nothing else hardcodes a ticker.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# 1. Investable universe (definitions SS1)
# --------------------------------------------------------------------------- #

#: Sector groups, in the fixed order used in every table and figure. Each takes
#: one slot of the validated categorical palette, in its validated order: with
#: more assets than the palette has slots, colour encodes the *sector*, and
#: figures that need per-asset identity use small multiples and direct labels.
SECTORS: dict[str, dict[str, str]] = {
    "Technology": {"color": "#2a78d6"},                 # blue
    "Healthcare": {"color": "#eb6834"},                 # orange
    "Financials": {"color": "#1baf7a"},                 # aqua
    "Consumer staples": {"color": "#eda100"},           # yellow
    "Real assets & defensive": {"color": "#e87ba4"},    # magenta
}
SECTOR_ORDER: list[str] = list(SECTORS)


def _stock(name: str, sector: str, industry: str, cost_bp: float = 3.0) -> dict:
    return {
        "name": name,
        "sector": sector,
        "asset_class": f"Equity -- {industry}",
        "instrument": "Common stock",
        "proxy_for": None,
        "cost_bp": cost_bp,
    }


def _fund(name: str, asset_class: str, instrument: str, cost_bp: float) -> dict:
    return {
        "name": name,
        "sector": "Real assets & defensive",
        "asset_class": asset_class,
        "instrument": instrument,
        "proxy_for": None,
        "cost_bp": cost_bp,
    }


#: The assets strategies may allocate to, grouped by sector. Dict order is the
#: fixed asset order. Each entry is self-contained -- sector, labels and one-way
#: cost -- so adding or swapping an asset is a one-entry edit. `proxy_for` is
#: set when a series is not itself a holding (a futures splice, a spot rate);
#: anything carrying it is labelled as a proxy wherever it appears.
UNIVERSE: dict[str, dict] = {
    "AAPL": _stock("Apple", "Technology", "technology hardware"),
    "MSFT": _stock("Microsoft", "Technology", "software"),
    "ORCL": _stock("Oracle", "Technology", "software"),
    "AMZN": _stock("Amazon.com", "Technology", "internet retail and cloud"),
    "INTC": _stock("Intel", "Technology", "semiconductors"),
    "JNJ": _stock("Johnson & Johnson", "Healthcare", "pharmaceuticals"),
    "PFE": _stock("Pfizer", "Healthcare", "pharmaceuticals"),
    "MRK": _stock("Merck & Co.", "Healthcare", "pharmaceuticals"),
    "UNH": _stock("UnitedHealth Group", "Healthcare", "managed care"),
    "ABT": _stock("Abbott Laboratories", "Healthcare", "medical devices"),
    "JPM": _stock("JPMorgan Chase", "Financials", "banks"),
    "BAC": _stock("Bank of America", "Financials", "banks"),
    "WFC": _stock("Wells Fargo", "Financials", "banks"),
    "GS": _stock("Goldman Sachs", "Financials", "investment banking"),
    "AXP": _stock("American Express", "Financials", "consumer finance"),
    "PG": _stock("Procter & Gamble", "Consumer staples", "household products"),
    "KO": _stock("Coca-Cola", "Consumer staples", "beverages"),
    "PEP": _stock("PepsiCo", "Consumer staples", "beverages"),
    "WMT": _stock("Walmart", "Consumer staples", "food and staples retail"),
    "CL": _stock("Colgate-Palmolive", "Consumer staples", "household products"),
    "GLD": _fund("SPDR Gold Shares", "Commodity -- gold", "ETF (physically backed trust)", 2.0),
    "SLV": _fund("iShares Silver Trust", "Commodity -- silver", "ETF (physically backed trust)", 3.0),
    "TLT": _fund("iShares 20+ Year Treasury Bond ETF", "Government bonds -- long duration", "ETF", 2.0),
    "VNQ": _fund("Vanguard Real Estate Index Fund ETF", "Real estate / REITs", "ETF", 2.0),
    "XOM": _stock("Exxon Mobil", "Real assets & defensive", "energy"),
}

#: Fixed asset order for every table and figure: sector by sector.
ASSET_ORDER: list[str] = list(UNIVERSE)

#: Asset tickers per sector, in the fixed order.
SECTOR_ASSETS: dict[str, list[str]] = {
    sector: [t for t in ASSET_ORDER if UNIVERSE[t]["sector"] == sector] for sector in SECTOR_ORDER
}

#: The single share the stylised-facts section analyses (definitions SS1).
STYLISED_FACTS_TICKER = "JPM"

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
FFILL_LIMIT = 3  # interior gaps longer than this are reported, not patched
EXTREME_MOVE = 0.15  # |daily log return| screened for missed corporate actions
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

#: One-way cost in basis points of traded notional, read off the universe.
COSTS_BP: dict[str, float] = {t: info["cost_bp"] for t, info in UNIVERSE.items()}
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

#: One fixed colour per asset: its sector's colour (see `SECTORS`).
ASSET_COLORS: dict[str, str] = {t: SECTORS[info["sector"]]["color"] for t, info in UNIVERSE.items()}

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
