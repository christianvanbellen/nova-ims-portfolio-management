"""Download, align and audit the price panel; build the return frames.

Covers workstream A tasks A2-A6. Nothing is written to disk: prices are pulled
from Yahoo Finance on every run and the extraction date is carried on the
`Panel` object so every table and figure can quote it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd
import yfinance as yf

from . import config as cfg


# --------------------------------------------------------------------------- #
# A2 -- download
# --------------------------------------------------------------------------- #

def download_raw(tickers: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame, date]:
    """Download the full available history for `tickers`.

    Returns (close, volume, extraction_date). Prices are `auto_adjust=True`, so
    they are adjusted for splits and dividends (definitions SS5).
    """
    tickers = list(tickers or cfg.ALL_TICKERS)
    raw = yf.download(
        tickers,
        period="max",
        auto_adjust=True,
        progress=False,
        threads=False,
        group_by="column",
    )
    if raw.empty:
        raise RuntimeError("Yahoo Finance returned no data -- check the network and retry.")

    close = raw["Close"].reindex(columns=tickers)
    volume = raw["Volume"].reindex(columns=tickers)
    return close, volume, date.today()


# --------------------------------------------------------------------------- #
# A3 -- calendar and alignment
# --------------------------------------------------------------------------- #

@dataclass
class Panel:
    """The aligned panel plus every number the data-quality tables need."""

    prices: pd.DataFrame          # dates x tickers, NYSE calendar, gaps filled <= FFILL_LIMIT
    prices_raw: pd.DataFrame      # same index, before any forward-fill
    volume: pd.DataFrame          # same index
    risk_free: pd.Series          # ^IRX, annualised percent
    calendar: pd.DatetimeIndex    # NYSE sessions in the panel period
    extraction_date: date
    full_history: pd.DataFrame = field(repr=False)   # untrimmed close, for A4
    full_volume: pd.DataFrame = field(repr=False)    # untrimmed volume, for A4
    dropped_offcalendar: dict[str, int] = field(default_factory=dict)
    fills: dict[str, int] = field(default_factory=dict)
    unpatched_gaps: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def assets(self) -> list[str]:
        return [t for t in cfg.ASSET_ORDER if t in self.prices.columns]

    @property
    def full_panel_start(self) -> pd.Timestamp:
        """First date on which every asset in the universe has a price."""
        return self.prices[self.assets].dropna().index[0]


def _longest_interior_nan_run(series: pd.Series) -> int:
    """Longest run of consecutive missing sessions after the first observation."""
    first = series.first_valid_index()
    if first is None:
        return 0
    flags = series.loc[first:].isna().to_numpy()
    longest = run = 0
    for flag in flags:
        run = run + 1 if flag else 0
        longest = max(longest, run)
    return longest


def build_panel(
    close: pd.DataFrame,
    volume: pd.DataFrame,
    extraction_date: date,
    start: str = cfg.PANEL_START,
) -> Panel:
    """Reindex every series onto the NYSE calendar and patch short interior gaps.

    The calendar is the set of dates `SPY` trades (definitions SS4). Pre-entry
    cells stay NaN -- never zero- or back-filled. Interior gaps are
    forward-filled up to `FFILL_LIMIT` sessions; anything longer is recorded in
    `unpatched_gaps` and left as NaN.
    """
    calendar = close[cfg.CALENDAR_TICKER].dropna().index
    calendar = calendar[calendar >= pd.Timestamp(start)]

    tradables = cfg.ASSET_ORDER + list(cfg.BENCHMARKS)

    # Observations that exist but fall outside NYSE sessions (weekend prints of
    # anything that trades every day). Counted, then discarded by the reindex.
    dropped = {}
    for ticker in tradables:
        observed = close[ticker].dropna().index
        observed = observed[observed >= pd.Timestamp(start)]
        dropped[ticker] = int(len(observed) - len(observed.intersection(calendar)))

    prices_raw = close.reindex(calendar)[tradables]

    # Forward-fill interior gaps only, bounded by FFILL_LIMIT.
    prices = prices_raw.copy()
    fills: dict[str, int] = {}
    gap_rows = []
    for ticker in tradables:
        column = prices_raw[ticker]
        first = column.first_valid_index()
        if first is None:
            fills[ticker] = 0
            continue
        interior = column.loc[first:]
        filled = interior.ffill(limit=cfg.FFILL_LIMIT)
        fills[ticker] = int(interior.isna().sum() - filled.isna().sum())
        prices.loc[first:, ticker] = filled

        # Anything still missing after the fill is a gap we report rather than patch.
        if filled.isna().any():
            flags = filled.isna()
            block = (flags != flags.shift()).cumsum()[flags]
            for _, dates in filled.index.to_series()[flags].groupby(block):
                gap_rows.append(
                    {
                        "ticker": ticker,
                        "gap_start": dates.iloc[0],
                        "gap_end": dates.iloc[-1],
                        "sessions": len(dates),
                    }
                )

    risk_free = close[cfg.RISK_FREE_TICKER].reindex(calendar).ffill(limit=cfg.FFILL_LIMIT)

    return Panel(
        prices=prices,
        prices_raw=prices_raw,
        volume=volume.reindex(calendar)[tradables],
        risk_free=risk_free,
        calendar=calendar,
        extraction_date=extraction_date,
        full_history=close,
        full_volume=volume,
        dropped_offcalendar=dropped,
        fills=fills,
        unpatched_gaps=pd.DataFrame(gap_rows, columns=["ticker", "gap_start", "gap_end", "sessions"]),
    )


# --------------------------------------------------------------------------- #
# A4 -- Table 1.1, data availability
# --------------------------------------------------------------------------- #

def availability_table(panel: Panel, tickers: list[str] | None = None) -> pd.DataFrame:
    """Table 1.1 -- history and liquidity per asset, over each asset's full history.

    Every column, median volume included, is measured over the asset's own full
    history rather than the panel, because the question the table answers is
    whether the asset clears the brief's 15-year minimum. Measured this way the
    table reconciles with definitions SS3.

    Liquidity is the exception: `Median $ volume` is measured over the *panel*,
    because the question there is whether the asset is tradable in the period
    the backtest uses, and dollars -- unlike shares -- compare across rows. It
    is adjusted close times volume, so it slightly understates early-panel
    turnover for assets that pay distributions.
    """
    tickers = tickers or panel.assets
    meta = {**cfg.UNIVERSE, **cfg.BENCHMARKS}
    asof = pd.Timestamp(panel.extraction_date)
    in_panel = panel.full_history.index >= panel.calendar[0]

    rows = []
    for ticker in tickers:
        history = panel.full_history[ticker].dropna()
        first = history.index[0]
        years = (asof - first).days / 365.25
        obs_per_year = len(history) / years
        dollar_volume = (panel.full_history[ticker] * panel.full_volume[ticker])[in_panel]
        median_dollar_volume = dollar_volume[dollar_volume > 0].median() / 1e6
        info = meta.get(ticker, {})
        rows.append(
            {
                "Ticker": ticker,
                "Name": info.get("name", ticker),
                "Sector": info.get("sector", "Benchmark"),
                "Asset class": info.get("asset_class", "Benchmark"),
                "Instrument": info.get("instrument", "ETF" if ticker == "SPY" else "Index"),
                "First obs.": first.date().isoformat(),
                "Years": years,
                "Obs./yr": obs_per_year,
                "Median $ volume (m)": median_dollar_volume,
                f"Meets {cfg.MIN_YEARS_REQUIRED}y": "Yes" if years >= cfg.MIN_YEARS_REQUIRED else "No",
            }
        )
    return pd.DataFrame(rows).set_index("Ticker")


# --------------------------------------------------------------------------- #
# A5 -- Table 1.2, data quality
# --------------------------------------------------------------------------- #

def quality_table(panel: Panel, tickers: list[str] | None = None) -> pd.DataFrame:
    """Table 1.2 -- missing and stale observations per asset, within the panel.

    `% zero-return days` is measured on the final, filled series, because that is
    what the analysis consumes; forward-filled sessions therefore show up here as
    zero returns, which is the honest reading.

    `Days |r| > X%` counts daily log returns beyond `EXTREME_MOVE` -- the screen
    for a corporate action the adjustment missed, which shows up as a one-day
    crash or jump. `extreme_moves` lists them so each can be checked.
    """
    tickers = tickers or panel.assets
    rows = []
    for ticker in tickers:
        raw = panel.prices_raw[ticker]
        first = raw.first_valid_index()
        interior_raw = raw.loc[first:]
        missing = int(interior_raw.isna().sum())

        final = panel.prices[ticker].loc[first:]
        log_returns = np.log(final).diff().dropna()
        zero_share = float((log_returns.abs() < 1e-12).mean() * 100)

        n_filled = panel.fills.get(ticker, 0)
        off_calendar = panel.dropped_offcalendar.get(ticker, 0)

        treatments = []
        if off_calendar:
            treatments.append(f"{off_calendar:,} off-calendar obs. dropped")
        if n_filled:
            treatments.append(f"{n_filled} session(s) forward-filled")
        if missing - n_filled > 0:
            treatments.append(f"{missing - n_filled} left as NaN")
        if not treatments:
            treatments.append("None required")

        rows.append(
            {
                "Ticker": ticker,
                "Panel start": first.date().isoformat(),
                "Obs.": int(final.notna().sum()),
                "Missing obs.": missing,
                "Longest gap (sessions)": _longest_interior_nan_run(interior_raw),
                "% zero-return days": zero_share,
                f"Days |r| > {cfg.EXTREME_MOVE:.0%}": int((log_returns.abs() > cfg.EXTREME_MOVE).sum()),
                "Treatment applied": "; ".join(treatments),
            }
        )
    return pd.DataFrame(rows).set_index("Ticker")


def extreme_moves(panel: Panel, tickers: list[str] | None = None) -> pd.DataFrame:
    """Every session on which an asset's daily log return exceeds `EXTREME_MOVE`
    in absolute value, with how many other assets moved that far the same day.

    A move shared with many others is a market event. A lone one is either
    news or a data fault, and is checked against the corporate-action log.
    """
    tickers = tickers or panel.assets
    log_returns = np.log(panel.prices[tickers]).diff()
    flags = log_returns.abs() > cfg.EXTREME_MOVE
    same_day = flags.sum(axis=1)
    rows = [
        {
            "Date": day.date().isoformat(),
            "Ticker": ticker,
            "Log return %": log_returns.at[day, ticker] * 100,
            "Assets past threshold that day": int(same_day.at[day]),
        }
        for day, ticker in flags.stack().loc[lambda x: x].index
    ]
    return pd.DataFrame(rows, columns=["Date", "Ticker", "Log return %", "Assets past threshold that day"])


# --------------------------------------------------------------------------- #
# A5b -- Table 1.3, dividend and adjustment effect
# --------------------------------------------------------------------------- #

def download_unadjusted(tickers: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Download the price-only history for `tickers`, plus their corporate actions.

    Returns (close, dividends, splits). With `auto_adjust=False` Yahoo's `Close`
    is still restated for splits but *not* for distributions, so comparing it with
    the adjusted close isolates exactly what the dividend adjustment contributes.
    """
    tickers = list(tickers or cfg.ASSET_ORDER + list(cfg.BENCHMARKS))
    raw = yf.download(
        tickers,
        period="max",
        auto_adjust=False,
        actions=True,
        progress=False,
        threads=False,
        group_by="column",
    )
    if raw.empty:
        raise RuntimeError("Yahoo Finance returned no data -- check the network and retry.")

    close = raw["Close"].reindex(columns=tickers)
    dividends = raw["Dividends"].reindex(columns=tickers).fillna(0.0)
    splits = raw["Stock Splits"].reindex(columns=tickers).fillna(0.0)
    return close, dividends, splits


def adjustment_table(
    panel: Panel,
    close_unadjusted: pd.DataFrame,
    dividends: pd.DataFrame,
    splits: pd.DataFrame,
    tickers: list[str] | None = None,
) -> pd.DataFrame:
    """Table 1.3 -- annualised total return (adjusted close) against price return
    (split-adjusted only), over each asset's own span within the panel.

    The gap between the two is what distributions contributed. The unadjusted
    series is put on the panel calendar with the same bounded forward-fill as the
    adjusted one, so both are measured on identical dates.
    """
    tickers = tickers or (panel.assets + [cfg.PERFORMANCE_BENCHMARK, "^GSPC"])
    meta = {**cfg.UNIVERSE, **cfg.BENCHMARKS}

    rows = []
    for ticker in tickers:
        adjusted = panel.prices[ticker]
        unadjusted = close_unadjusted[ticker].reindex(panel.calendar).ffill(limit=cfg.FFILL_LIMIT)
        both = pd.concat([adjusted, unadjusted], axis=1, keys=["adj", "raw"]).dropna()
        first, last = both.index[0], both.index[-1]
        years = (last - first).days / 365.25

        total = (both["adj"].iloc[-1] / both["adj"].iloc[0]) ** (1 / years) - 1
        price = (both["raw"].iloc[-1] / both["raw"].iloc[0]) ** (1 / years) - 1

        window = slice(first + pd.Timedelta(days=1), last)
        n_distributions = int((dividends[ticker].loc[window] > 0).sum())
        n_splits = int((splits[ticker].loc[window] > 0).sum())

        info = meta.get(ticker, {})
        rows.append(
            {
                "Ticker": ticker,
                "Instrument": info.get("instrument", "ETF" if ticker == "SPY" else "Index"),
                "From": first.date().isoformat(),
                "Total return %/yr": total * 100,
                "Price return %/yr": price * 100,
                "Distributions pp/yr": (total - price) * 100,
                "Distribution events": n_distributions,
                "Split / spin-off events": n_splits,
            }
        )
    return pd.DataFrame(rows).set_index("Ticker")


def corporate_actions(panel: Panel, splits: pd.DataFrame, tickers: list[str] | None = None) -> pd.DataFrame:
    """Every split-type adjustment inside the panel, classified.

    Yahoo books a spin-off as a fractional "split": the ratio is the parent's
    pre-spin price over its post-spin price, so the adjusted series carries no
    artificial crash. A whole-number ratio is a genuine split. The log return on
    the event date is shown so the absence of a crash can be checked directly.
    """
    tickers = tickers or panel.assets
    window = splits.loc[panel.calendar[0] + pd.Timedelta(days=1): panel.calendar[-1], tickers]
    log_returns = np.log(panel.prices[tickers]).diff()
    rows = []
    for day, ticker in window.stack().loc[lambda x: x > 0].index:
        ratio = float(splits.at[day, ticker])
        rows.append(
            {
                "Date": day.date().isoformat(),
                "Ticker": ticker,
                "Ratio": ratio,
                "Type": "Split" if abs(ratio - round(ratio)) < 1e-6 else "Spin-off (price factor)",
                "Adjusted log return % that day": log_returns.at[day, ticker] * 100
                if day in log_returns.index else np.nan,
            }
        )
    return pd.DataFrame(rows, columns=["Date", "Ticker", "Ratio", "Type", "Adjusted log return % that day"])


# --------------------------------------------------------------------------- #
# A6 -- return frames
# --------------------------------------------------------------------------- #

def build_returns(panel: Panel, tickers: list[str] | None = None) -> dict[tuple[str, str], pd.DataFrame]:
    """Six return frames, keyed `(frequency, kind)` for frequency in daily/weekly/
    monthly and kind in log/simple.

    Weekly and monthly log returns are the *sum* of daily log returns over the
    period (definitions SS5); the simple frames are the equivalent compounded
    figure, `exp(sum) - 1`, so the two kinds describe the same price moves.
    """
    tickers = tickers or (panel.assets + [cfg.PERFORMANCE_BENCHMARK])
    prices = panel.prices[tickers]
    daily_log = np.log(prices).diff()

    frames: dict[tuple[str, str], pd.DataFrame] = {}
    for frequency, rule in cfg.FREQUENCIES.items():
        if rule is None:
            log_returns = daily_log.iloc[1:]
        else:
            # min_count=1 keeps pre-entry periods NaN instead of summing to zero.
            log_returns = daily_log.resample(rule).sum(min_count=1)
        frames[(frequency, "log")] = log_returns
        frames[(frequency, "simple")] = np.expm1(log_returns)
    return frames
