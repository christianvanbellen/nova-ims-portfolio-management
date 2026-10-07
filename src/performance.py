"""Run the experiment grid and measure performance.

Covers workstream E tasks E1-E7 and E10. `run_grid` puts every strategy through
every experiment under each cost scenario. `results_frame` turns the runs into
the raw results frame, one row per experiment x strategy. The summary functions
reduce that frame to the report's tables. The conventions are in
`conventions_table` (Table 4.1), and the functions below implement exactly
those.

Nothing is written to disk. The grid takes a minute or two at the 10-asset
subset size, so notebooks 05-07 each rebuild it from the seed.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import backtest as bt
from . import config as cfg

#: Added to |max drawdown| in the Sterling denominator (Table 4.1).
STERLING_CUSHION = 0.10

#: Display order and labels for the metrics in the raw results frame.
METRICS = ["ann_return", "ann_vol", "sharpe", "sortino", "max_dd", "calmar", "sterling", "turnover"]
LABELS = {
    "ann_return": "Ann. return %",
    "ann_vol": "Ann. vol %",
    "sharpe": "Sharpe",
    "sortino": "Sortino",
    "max_dd": "Max DD %",
    "calmar": "Calmar",
    "sterling": "Sterling",
    "turnover": "Turnover %/yr",
}
PERCENT_METRICS = {"ann_return", "ann_vol", "max_dd", "turnover"}

#: Return bases in the results frame: before costs, after costs, after 2x costs.
BASES = ["gross", "net", "net_2x"]


# --------------------------------------------------------------------------- #
# E1 -- the grid
# --------------------------------------------------------------------------- #

@dataclass
class Grid:
    """Every run, keyed (experiment, strategy). `stressed` holds the 2x-cost runs."""

    runs: dict[tuple[int, str], bt.BacktestResult]
    stressed: dict[tuple[int, str], bt.BacktestResult]
    experiments: pd.DataFrame

    def all_runs(self) -> list[bt.BacktestResult]:
        return list(self.runs.values()) + list(self.stressed.values())


def run_grid(
    prices: pd.DataFrame,
    experiments: pd.DataFrame,
    strategies: dict[str, Callable],
    risk_free: pd.Series,
    schedule: bt.Schedule = bt.Schedule(),
) -> Grid:
    """Every strategy on every experiment, at 1x and 2x costs.

    Costs never change a weight decision, so the 1x and 2x runs trade
    identically and differ only in the cost deducted. Gross returns come from
    the 1x runs. Each weight decision is therefore computed once and replayed
    for the 2x run (`_replay`), which halves the optimisation work without
    changing a single number.
    """
    runs, stressed = {}, {}
    for i, e in experiments.iterrows():
        block = bt.experiment_prices(prices, e)
        for name, fn in strategies.items():
            replayed = _replay(fn)
            for store, costs in ((runs, bt.CostModel()), (stressed, bt.CostModel.stressed())):
                store[(i, name)] = bt.run_backtest(
                    block, replayed, costs, schedule, risk_free=risk_free, experiment=i, strategy=name
                )
    return Grid(runs=runs, stressed=stressed, experiments=experiments)


def _replay(fn: Callable) -> Callable:
    """Wrap a weight function so a repeated call on the same estimation window
    returns the first call's weights -- or raises the first call's exception
    again, so failures are logged identically. Keyed on the window's dates and
    assets; valid within one experiment, where the prices are fixed. The
    wrapper keeps `fn`'s signature as the loop sees it (`risk_free` or not).
    """
    memo: dict[tuple, tuple[bool, object]] = {}

    def lookup(key: tuple, compute: Callable[[], object]):
        if key not in memo:
            try:
                memo[key] = (True, compute())
            except Exception as exc:  # stored, and raised again below
                memo[key] = (False, exc)
        ok, value = memo[key]
        if not ok:
            raise value
        return value

    def key_of(window: pd.DataFrame) -> tuple:
        return (window.index[0], window.index[-1], tuple(window.columns))

    if bt._accepts_risk_free(fn):
        def replayed(window: pd.DataFrame, risk_free: pd.Series | None = None):
            if risk_free is None:
                return lookup(key_of(window), lambda: fn(window))
            return lookup(key_of(window) + ("rf",), lambda: fn(window, risk_free=risk_free))
        return replayed

    def replayed_plain(window: pd.DataFrame):
        return lookup(key_of(window), lambda: fn(window))
    return replayed_plain


# --------------------------------------------------------------------------- #
# E2 -- metrics, exactly as Table 4.1 states them
# --------------------------------------------------------------------------- #

def daily_risk_free(risk_free: pd.Series, dates: pd.DatetimeIndex) -> pd.Series:
    """`^IRX` (annualised percent) as a daily decimal rate on `dates`."""
    return risk_free.reindex(dates).ffill() / 100 / cfg.TRADING_DAYS


def max_drawdown(returns: pd.Series) -> float:
    """Largest peak-to-trough fall in wealth, as a negative decimal.

    Wealth starts at 1 the day before the first return, so a fall from the
    starting value counts.
    """
    wealth = np.concatenate([[1.0], np.cumprod(1 + returns.to_numpy())])
    return float((wealth / np.maximum.accumulate(wealth) - 1).min())


def metrics(returns: pd.Series, rf_daily: pd.Series) -> dict[str, float]:
    """Every return-based metric in Table 4.1 for one daily return series."""
    n = len(returns)
    excess = returns - rf_daily.reindex(returns.index)
    ann_return = float(np.prod(1 + returns.to_numpy()) ** (cfg.TRADING_DAYS / n) - 1)
    ann_vol = float(returns.std(ddof=1) * np.sqrt(cfg.TRADING_DAYS))
    excess_mean = float(excess.mean() * cfg.TRADING_DAYS)
    excess_vol = float(excess.std(ddof=1) * np.sqrt(cfg.TRADING_DAYS))
    downside = float(np.sqrt((np.minimum(excess.to_numpy(), 0) ** 2).mean()) * np.sqrt(cfg.TRADING_DAYS))
    dd = max_drawdown(returns)
    return {
        "ann_return": ann_return,
        "ann_vol": ann_vol,
        "sharpe": excess_mean / excess_vol if excess_vol > 0 else np.nan,
        "sortino": excess_mean / downside if downside > 0 else np.nan,
        "max_dd": dd,
        "calmar": ann_return / abs(dd) if dd < 0 else np.nan,
        "sterling": ann_return / (abs(dd) + STERLING_CUSHION),
    }


def results_frame(grid: Grid, risk_free: pd.Series) -> pd.DataFrame:
    """E1 -- the raw results frame.

    One row per (experiment, strategy). Columns are (basis, metric), with basis
    in gross / net / net_2x. Values are decimals (ratios unitless). Percent
    conversion happens only at display.
    """
    rows = {}
    for (i, name), res in grid.runs.items():
        rf = daily_risk_free(risk_free, res.gross.index)
        row = {}
        for basis, returns in (("gross", res.gross), ("net", res.net), ("net_2x", grid.stressed[(i, name)].net)):
            for metric, value in metrics(returns, rf).items():
                row[(basis, metric)] = value
            row[(basis, "turnover")] = res.turnover
        rows[(i, name)] = row
    frame = pd.DataFrame.from_dict(rows, orient="index")
    frame.index = pd.MultiIndex.from_tuples(frame.index, names=["experiment", "strategy"])
    frame.columns = pd.MultiIndex.from_tuples(frame.columns, names=["basis", "metric"])
    return frame.reindex(columns=pd.MultiIndex.from_product([BASES, METRICS], names=["basis", "metric"]))


def conventions_table() -> pd.DataFrame:
    """Table 4.1 -- the precise convention behind every reported metric."""
    td = cfg.TRADING_DAYS
    rows = [
        ("Ann. return", "(∏(1 + rₜ))^(252/n) − 1", "Geometric; n = 252 sessions, so it is the evaluation year's total return",
         "Not subtracted", "—"),
        ("Ann. volatility", "sd(rₜ) × √252", "√252 on daily sd (ddof = 1)", "—", "—"),
        ("Sharpe", "mean(rₜ − r_f,ₜ) × 252 / (sd(rₜ − r_f,ₜ) × √252)", "Arithmetic mean ×252, sd ×√252",
         "^IRX daily: yield ÷ 100 ÷ 252, each session", "—"),
        ("Sortino", "mean(rₜ − r_f,ₜ) × 252 / (√mean(min(rₜ − r_f,ₜ, 0)²) × √252)",
         "As Sharpe; downside deviation over all sessions, target r_f", "^IRX daily", "—"),
        ("Max drawdown", "min over t of Wₜ / maxₛ≤ₜ Wₛ − 1", "None — measured over the evaluation year",
         "—", "Wealth path W from 1 at the start of the evaluation year, so a fall from the start counts"),
        ("Calmar", "Ann. return / |max drawdown|", "Annualised return", "Not subtracted", "|Max drawdown|"),
        ("Sterling", f"Ann. return / (|max drawdown| + {STERLING_CUSHION * 100:.0f}%)",
         "Annualised return", "Not subtracted",
         "|Average annual max drawdown| + 10% (Jones). With one evaluation year the average is that year's max "
         "drawdown. The cushion keeps the ratio finite when drawdowns are shallow"),
        ("Turnover", "Σ over rebalances of Σᵢ|Δwᵢ|, ÷ evaluation years", "Per year; two-way",
         "—", "Excludes the opening trade from cash"),
        ("Gross / net", "Net deducts Σᵢ|Δwᵢ| × bpᵢ at each trade", "—", "—",
         "Definitions §6 bp; 2× in workstream F"),
        ("Across experiments", "Median of the per-experiment values", "—", "—",
         "Medians, because ratios with small denominators have heavy tails"),
    ]
    assert td == 252
    return pd.DataFrame(rows, columns=["Metric", "Formula", "Annualisation", "Risk-free", "Drawdown / denominator"]
                        ).set_index("Metric")


# --------------------------------------------------------------------------- #
# E3-E7 -- summaries across the 100 experiments
# --------------------------------------------------------------------------- #

def win_rate(frame: pd.DataFrame, metric: str = "sharpe", basis: str = "net", benchmark: str = "EW") -> pd.Series:
    """Share of experiments in which each strategy beats `benchmark` on `metric`, same experiment.

    Ties count as not beating. The benchmark's own row is NaN.
    """
    values = frame[(basis, metric)].unstack("strategy")
    rate = values.gt(values[benchmark], axis=0).mean()
    rate[benchmark] = np.nan
    return rate.reindex(cfg.STRATEGY_ORDER)


def headline_table(frame: pd.DataFrame, basis: str = "net") -> pd.DataFrame:
    """Table 4.2 (net) or its gross twin -- medians across experiments, plus the win rate vs EW."""
    cols = ["ann_return", "ann_vol", "sharpe", "max_dd", "sterling", "turnover"]
    table = frame[basis][cols].groupby("strategy").median().reindex(cfg.STRATEGY_ORDER)
    for c in PERCENT_METRICS & set(cols):
        table[c] *= 100
    table["beats_ew"] = win_rate(frame, basis=basis) * 100
    return table.rename(columns={**LABELS, "beats_ew": "Beats EW (Sharpe) %"})


def dispersion_table(frame: pd.DataFrame, basis: str = "net") -> pd.DataFrame:
    """Table 4.3 -- median, IQR and 10th/90th percentiles of Sharpe and of net annual return."""
    out = {}
    for metric, scale in (("sharpe", 1.0), ("ann_return", 100.0)):
        values = frame[(basis, metric)].unstack("strategy") * scale
        q = values.quantile([0.10, 0.25, 0.50, 0.75, 0.90])
        label = "Sharpe" if metric == "sharpe" else "Net return %"
        out[(label, "Median")] = q.loc[0.50]
        out[(label, "IQR")] = q.loc[0.75] - q.loc[0.25]
        out[(label, "P10")] = q.loc[0.10]
        out[(label, "P90")] = q.loc[0.90]
    table = pd.DataFrame(out).reindex(cfg.STRATEGY_ORDER)
    table.columns = pd.MultiIndex.from_tuples(table.columns)
    return table


def cost_impact_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Table 4.4 -- gross against net Sharpe, and what each strategy's trading cost it.

    The Sharpe difference is the median of the per-experiment differences, not
    the difference of the medians.
    """
    gross = frame[("gross", "sharpe")].unstack("strategy")
    net = frame[("net", "sharpe")].unstack("strategy")
    drag = (frame[("gross", "ann_return")] - frame[("net", "ann_return")]).unstack("strategy")
    turnover = frame[("net", "turnover")].unstack("strategy")
    table = pd.DataFrame({
        "Gross Sharpe": gross.median(),
        "Net Sharpe": net.median(),
        "Difference": (net - gross).median(),
        "Cost drag bp/yr": drag.median() * 1e4,
        "Turnover %/yr": turnover.median() * 100,
    })
    return table.reindex(cfg.STRATEGY_ORDER)


def paired_table(frame: pd.DataFrame, basis: str = "net", benchmark: str = "EW") -> pd.DataFrame:
    """Table 4.5 -- every strategy against `benchmark` *in the same experiment*.

    Table 4.2's medians are taken column by column, so a strategy can have a
    higher median Sharpe than EW and still lose to it in most experiments.
    Here every figure is a median of per-experiment differences, or the share
    of experiments in which the strategy is better on that measure -- the
    paired comparison the brief's win rate implies.
    """
    data = frame[basis]
    rows = {}
    for strategy in cfg.STRATEGY_ORDER:
        if strategy == benchmark:
            continue
        mine = data.xs(strategy, level="strategy")
        theirs = data.xs(benchmark, level="strategy")
        rows[strategy] = {
            "Median Δ Sharpe": (mine["sharpe"] - theirs["sharpe"]).median(),
            "Beats EW (Sharpe) %": (mine["sharpe"] > theirs["sharpe"]).mean() * 100,
            "Median Δ return pp": (mine["ann_return"] - theirs["ann_return"]).median() * 100,
            "Median Δ vol pp": (mine["ann_vol"] - theirs["ann_vol"]).median() * 100,
            "Lower vol %": (mine["ann_vol"] < theirs["ann_vol"]).mean() * 100,
            "Median Δ max DD pp": (mine["max_dd"] - theirs["max_dd"]).median() * 100,
            "Shallower DD %": (mine["max_dd"] > theirs["max_dd"]).mean() * 100,
        }
    return pd.DataFrame(rows).T.rename_axis("strategy")


def representative_experiment(frame: pd.DataFrame, strategy: str, metric: str = "sharpe", basis: str = "net") -> int:
    """The experiment at `strategy`'s lower median: the 50th of 100 when sorted.

    With an even count the median falls between two experiments, both equally
    close to it, and rounding would decide between them. The lower median is
    an actual experiment's value, so the choice is stable. Used to pick the one
    window Figures 4.3-4.4 draw, by a rule fixed before looking at the picture.
    """
    values = frame[(basis, metric)].xs(strategy, level="strategy").sort_values(kind="stable")
    return int(values.index[(len(values) - 1) // 2])
