"""Robustness: do the conclusions depend on the sampled period or the asset subset?

Covers workstream F tasks F1-F5. Every function re-cuts the raw results frame
from notebook 05 (`performance.results_frame`), the experiments frame from the
sampler, or the held weights in the grid; nothing is re-run. All comparisons are *paired* with EW in the same
experiment, as in Table 4.5, because column-wise medians are not head-to-head
results (definitions SS9).

These splits are descriptive, not tests. The experiments overlap in time and
share assets, and each period is paired with one subset, so the period and
subset splits are not fully separable.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import backtest as bt
from . import config as cfg
from . import performance as pf
from .stylised import STRESS_WINDOW

#: Correlation above which two assets count as a near-collinear pair. The same
#: threshold notebook 03's conditioning diagnostic and notebook 06's turnover
#: check use.
COLLINEAR_THRESHOLD = 0.85

CRISIS_GROUPS = ["In evaluation year", "In estimation period only", "Neither"]


def paired_differences(frame: pd.DataFrame, metric: str = "sharpe", basis: str = "net",
                       benchmark: str = "EW") -> pd.DataFrame:
    """Strategy minus `benchmark` on `metric`, same experiment. Rows experiments, columns strategies."""
    values = frame[(basis, metric)].unstack("strategy")
    others = [s for s in cfg.STRATEGY_ORDER if s != benchmark]
    return values[others].sub(values[benchmark], axis=0)


# --------------------------------------------------------------------------- #
# F1 -- harsher costs
# --------------------------------------------------------------------------- #

def cost_ranking(frame: pd.DataFrame) -> pd.DataFrame:
    """Table 5.1 -- rank by median net Sharpe at 1x and 2x costs, and the paired win rate at each.

    Rank 1 is the highest median Sharpe. The 2x runs trade exactly as the 1x
    runs (costs never change a weight), so any change in rank comes from the
    cost deducted alone.
    """
    out = {}
    for basis, label in (("net", "1x"), ("net_2x", "2x")):
        sharpe = frame[(basis, "sharpe")].groupby("strategy").median()
        out[f"Rank {label}"] = sharpe.rank(ascending=False, method="min").astype(int)
        out[f"Net Sharpe {label}"] = sharpe
        out[f"Beats EW (Sharpe) % {label}"] = pf.win_rate(frame, basis=basis) * 100
    table = pd.DataFrame(out).reindex(cfg.STRATEGY_ORDER)
    order = ["Rank 1x", "Rank 2x", "Net Sharpe 1x", "Net Sharpe 2x", "Beats EW (Sharpe) % 1x", "Beats EW (Sharpe) % 2x"]
    return table[order].rename_axis("strategy")


# --------------------------------------------------------------------------- #
# F3 -- crisis exposure
# --------------------------------------------------------------------------- #

def crisis_exposure(experiments: pd.DataFrame, window: tuple[str, str] = STRESS_WINDOW) -> pd.Series:
    """Where `window` falls in each experiment: evaluation year, estimation period only, or neither.

    An overlap of a single session counts. The evaluation year takes precedence,
    because that is the year the metrics measure.
    """
    lo, hi = pd.Timestamp(window[0]), pd.Timestamp(window[1])
    in_eval = (experiments["evaluation_start"] <= hi) & (experiments["end"] >= lo)
    in_est = (experiments["start"] <= hi) & (experiments["estimation_end"] >= lo)
    group = np.select([in_eval, in_est], CRISIS_GROUPS[:2], default=CRISIS_GROUPS[2])
    return pd.Series(pd.Categorical(group, categories=CRISIS_GROUPS), index=experiments.index,
                     name="crisis")


# --------------------------------------------------------------------------- #
# F4 -- asset subset
# --------------------------------------------------------------------------- #

def max_pair_correlation(prices: pd.DataFrame, experiments: pd.DataFrame,
                         schedule: bt.Schedule = bt.Schedule()) -> pd.Series:
    """Each subset's highest pairwise correlation over the trailing year that ends the estimation period.

    The window is the one-year lookback every re-estimate uses, so the measure
    reflects what the optimisers see at a typical rebalance.
    """
    out = {}
    for i, e in experiments.iterrows():
        r = bt.experiment_prices(prices, e).pct_change().iloc[1:]
        corr = r.iloc[schedule.estimation - schedule.lookback: schedule.estimation].corr()
        out[i] = corr.where(~np.eye(len(corr), dtype=bool)).max().max()
    return pd.Series(out, name="max_pair_corr").rename_axis(experiments.index.name)


def holdings(experiments: pd.DataFrame) -> pd.DataFrame:
    """Boolean frame, experiments x assets in the fixed order: does the subset hold the asset?"""
    held = pd.DataFrame(False, index=experiments.index, columns=cfg.ASSET_ORDER)
    for i, assets in experiments["assets"].items():
        held.loc[i, list(assets)] = True
    return held


def asset_effect(frame: pd.DataFrame, experiments: pd.DataFrame, metric: str = "sharpe",
                 basis: str = "net") -> tuple[pd.DataFrame, pd.Series]:
    """Figure 5.2 -- per asset and strategy, the share of experiments better than EW when the
    asset is held minus the share when it is not, in percentage points.

    Returns the effect (assets x strategies) and the number of experiments holding each asset.
    """
    better = paired_differences(frame, metric, basis) > 0
    held = holdings(experiments).reindex(better.index)
    effect = {}
    for asset in held.columns:
        h = held[asset]
        effect[asset] = (better[h].mean() - better[~h].mean()) * 100
    return pd.DataFrame(effect).T.rename_axis("asset"), held.sum().rename("n held")


# --------------------------------------------------------------------------- #
# Table 5.2 -- the paired results within each group
# --------------------------------------------------------------------------- #

def split_table(frame: pd.DataFrame, splits: dict[str, pd.Series], basis: str = "net") -> pd.DataFrame:
    """Table 5.2 and its appendix twin, long form.

    `splits` maps a split name to a categorical Series over experiments. For
    every group and strategy: n, the median paired Sharpe difference with EW,
    the share of experiments beating EW on Sharpe, and the share with lower
    volatility than EW. Every group includes an "All experiments" reference row.
    """
    d_sharpe = paired_differences(frame, "sharpe", basis)
    d_vol = paired_differences(frame, "ann_vol", basis)
    rows = []
    groups = [("All experiments", "All", pd.Series(True, index=d_sharpe.index))]
    for name, labels in splits.items():
        for g in (labels.cat.categories if hasattr(labels, "cat") else labels.unique()):
            groups.append((name, g, labels == g))
    for name, g, mask in groups:
        mask = mask.reindex(d_sharpe.index)
        for s in d_sharpe.columns:
            rows.append({
                "split": name, "group": g, "strategy": s, "n": int(mask.sum()),
                "Median Δ Sharpe": d_sharpe.loc[mask, s].median(),
                "Beats EW (Sharpe) %": (d_sharpe.loc[mask, s] > 0).mean() * 100,
                "Lower vol %": (d_vol.loc[mask, s] < 0).mean() * 100,
            })
    return pd.DataFrame(rows).set_index(["split", "group", "strategy"])


# --------------------------------------------------------------------------- #
# F5 -- concentration, and what the held weights are exposed to
# --------------------------------------------------------------------------- #

def concentration(grid: pf.Grid) -> pd.DataFrame:
    """Per run, the evaluation-year average of the daily max weight and effective N (1 / sum w^2).

    Uses the weights actually held at each close, drift included, from the
    opening trade to the end of the evaluation year. Rows (experiment,
    strategy); max weight as a decimal.
    """
    rows = {}
    for key, res in grid.runs.items():
        w = res.weights.to_numpy()
        rows[key] = {"max_weight": w.max(axis=1).mean(),
                     "effective_n": (1 / (w ** 2).sum(axis=1)).mean(),
                     "single_asset": (w.max(axis=1) > 0.99).mean()}
    frame = pd.DataFrame.from_dict(rows, orient="index")
    frame.index = pd.MultiIndex.from_tuples(frame.index, names=["experiment", "strategy"])
    return frame


def concentration_table(conc: pd.DataFrame) -> pd.DataFrame:
    """Table 5.3 -- per strategy, means across experiments of `concentration`'s per-run figures."""
    by = conc.groupby("strategy")
    table = pd.DataFrame({
        "Mean max weight %": by["max_weight"].mean() * 100,
        "Mean effective N": by["effective_n"].mean(),
        "Lowest effective N": conc["effective_n"].groupby("strategy").min(),
        "Days in one asset %": by["single_asset"].mean() * 100,
    })
    return table.reindex(cfg.STRATEGY_ORDER)


def weighted_exposure(grid: pf.Grid, values: pd.Series) -> pd.DataFrame:
    """Per run, the evaluation-year average of sum_i w_i * values_i. Experiments x strategies.

    `values` is indexed by asset: 0/1 flags give the capital held in a group
    of assets, a yield gives the portfolio's yield.
    """
    out = {}
    for key, res in grid.runs.items():
        out[key] = float((res.weights @ values.reindex(res.weights.columns)).mean())
    s = pd.Series(out)
    s.index = pd.MultiIndex.from_tuples(s.index, names=["experiment", "strategy"])
    return s.unstack("strategy")[cfg.STRATEGY_ORDER]
