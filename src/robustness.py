"""Robustness: do the conclusions depend on the sampled period or the asset subset?

Covers workstream F tasks F2-F4. Every function re-cuts the raw results frame
from notebook 05 (`performance.results_frame`) and the experiments frame from
the sampler; nothing is re-run. All comparisons are *paired* with EW in the same
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
