"""Figure helpers and the house style.

One fixed colour per asset, one y-axis per chart, benchmarks in dashed neutral
grey. Everything the report draws goes through here so the styling cannot drift
between notebooks.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from . import config as cfg

#: Diverging map for correlations: blue <-> red with a neutral grey midpoint.
CORR_CMAP = LinearSegmentedColormap.from_list(
    "corr", [cfg.DIVERGING_LOW, cfg.DIVERGING_MID, cfg.DIVERGING_HIGH]
)


def use_house_style() -> None:
    """Apply the report's figure style. Call once at the top of a notebook."""
    mpl.rcParams.update(
        {
            "figure.facecolor": cfg.SURFACE,
            "axes.facecolor": cfg.SURFACE,
            "axes.edgecolor": cfg.GRID_COLOR,
            "axes.labelcolor": cfg.INK_SECONDARY,
            "axes.titlecolor": cfg.INK_PRIMARY,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": cfg.GRID_COLOR,
            "grid.linewidth": 0.6,
            "grid.alpha": 0.9,
            "xtick.color": cfg.INK_SECONDARY,
            "ytick.color": cfg.INK_SECONDARY,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.frameon": False,
            "legend.fontsize": 8,
            "lines.linewidth": 1.8,
            "figure.dpi": 120,
            "savefig.dpi": 200,
            "savefig.bbox": "tight",
            "font.size": 9,
        }
    )


def color_for(ticker: str) -> str:
    """The fixed colour for an asset; neutral grey for anything benchmark-like."""
    return cfg.ASSET_COLORS.get(ticker, cfg.BENCHMARK_COLOR)


def caption(ax: plt.Axes, text: str) -> None:
    """Figure captions sit *below* the chart (plan SS1)."""
    ax.figure.text(
        0.0, -0.04, text, ha="left", va="top", fontsize=8,
        color=cfg.INK_SECONDARY, wrap=True,
    )


# --------------------------------------------------------------------------- #
# A7 -- Figure 1.1, correlation heatmap
# --------------------------------------------------------------------------- #

def correlation_heatmap(
    returns: pd.DataFrame,
    tickers: list[str],
    ax: plt.Axes | None = None,
) -> tuple[plt.Axes, pd.DataFrame]:
    """Correlation heatmap on a diverging scale fixed to -1..+1, values in cells."""
    corr = returns[tickers].corr()
    if ax is None:
        _, ax = plt.subplots(figsize=(6.4, 5.4))

    image = ax.imshow(
        corr.to_numpy(), cmap=CORR_CMAP, norm=TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
    )
    ax.set_xticks(range(len(tickers)), tickers, rotation=45, ha="right")
    ax.set_yticks(range(len(tickers)), tickers)
    ax.grid(False)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i in range(len(tickers)):
        for j in range(len(tickers)):
            value = corr.iat[i, j]
            # Ink stays readable against the deepest ends of the ramp.
            ink = "#ffffff" if abs(value) > 0.65 else cfg.INK_PRIMARY
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8, color=ink)

    bar = ax.figure.colorbar(image, ax=ax, shrink=0.78, ticks=[-1, -0.5, 0, 0.5, 1])
    bar.outline.set_visible(False)
    bar.ax.tick_params(length=0, labelsize=8, colors=cfg.INK_SECONDARY)
    bar.set_label("Pearson correlation", fontsize=8, color=cfg.INK_SECONDARY)
    return ax, corr


def _spread(positions, min_gap: float):
    """Push sorted label positions apart so none sit closer than `min_gap`."""
    out = positions.astype(float).copy()
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + min_gap)
    return out



# --------------------------------------------------------------------------- #
# A8 -- Figure 1.2, cumulative growth of $1
# --------------------------------------------------------------------------- #

def growth_of_one(
    prices: pd.DataFrame,
    tickers: list[str],
    benchmarks: tuple[str, ...] = (cfg.PERFORMANCE_BENCHMARK,),
    ax: plt.Axes | None = None,
) -> tuple[plt.Axes, pd.DataFrame]:
    """Growth of $1 on a log y-axis, every series rebased at the first common date.

    Lines are labelled at their right-hand end as well as in the legend, so
    identity never rests on colour alone.
    """
    columns = list(tickers) + [b for b in benchmarks if b not in tickers]
    series = prices[columns].dropna()
    wealth = series / series.iloc[0]

    if ax is None:
        _, ax = plt.subplots(figsize=(8.0, 4.6))

    for ticker in columns:
        is_benchmark = ticker in benchmarks
        style = dict(cfg.BENCHMARK_STYLE) if is_benchmark else {"color": color_for(ticker)}
        label = f"{ticker} (benchmark)" if is_benchmark else ticker
        ax.plot(wealth.index, wealth[ticker], label=label, zorder=2 if is_benchmark else 3, **style)

    # Direct end labels, nudged apart so close finishers stay legible.
    ends = wealth.iloc[-1].sort_values()
    offsets = _spread(np.log10(ends.to_numpy()), min_gap=0.055)
    for ticker, offset in zip(ends.index, offsets):
        ax.annotate(
            ticker,
            xy=(wealth.index[-1], 10.0**offset),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontsize=8,
            color=cfg.INK_SECONDARY if ticker in benchmarks else color_for(ticker),
        )

    ax.set_yscale("log")
    ax.set_ylabel("Growth of $1 (log scale)")
    ax.set_xlabel("Year")
    ax.axhline(1.0, color=cfg.GRID_COLOR, linewidth=1.0, zorder=1)
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"${v:,.0f}" if v >= 1 else f"${v:,.2f}"))
    ax.margins(x=0.06)
    ax.legend(loc="upper left", ncols=4)
    return ax, wealth
