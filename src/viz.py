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


# --------------------------------------------------------------------------- #
# B2 -- Figure 2.1, log returns over time
# --------------------------------------------------------------------------- #

def return_panels(series_by_freq: dict[str, pd.Series], ticker: str) -> tuple[plt.Figure, np.ndarray]:
    """One stacked panel per frequency on a shared date axis.

    Each panel keeps its own y-scale -- a monthly move is several daily ones,
    and a common scale would flatten the daily clusters the figure exists to show.
    """
    fig, axes = plt.subplots(len(series_by_freq), 1, figsize=(8.4, 6.6), sharex=True)
    for ax, (frequency, series) in zip(axes, series_by_freq.items()):
        ax.plot(series.index, series, color=color_for(ticker), linewidth=0.7)
        ax.axhline(0, color=cfg.INK_SECONDARY, linewidth=0.6, zorder=1)
        ax.set_ylabel(f"{frequency.capitalize()} log return (%)")
    axes[-1].set_xlabel("Year")
    return fig, axes


# --------------------------------------------------------------------------- #
# B3 -- Figure 2.2, histogram against a fitted normal, and a Q-Q plot
# --------------------------------------------------------------------------- #

def distribution_pair(series: pd.Series, ticker: str, axes: np.ndarray, label: str) -> None:
    """Histogram with the moment-matched normal density, beside a normal Q-Q plot."""
    from scipy import stats

    x = series.dropna()
    mu, sd = x.mean(), x.std(ddof=1)
    hist_ax, qq_ax = axes

    bins = min(120, max(20, int(np.sqrt(len(x)) * 1.5)))
    hist_ax.hist(x, bins=bins, density=True, color=color_for(ticker), alpha=0.85,
                 edgecolor=cfg.SURFACE, linewidth=0.4, label=f"{ticker} empirical")
    grid = np.linspace(x.min(), x.max(), 400)
    hist_ax.plot(grid, stats.norm.pdf(grid, mu, sd), label="Normal, same mean and SD", **cfg.BENCHMARK_STYLE)
    hist_ax.set_xlabel(f"{label} log return (%)")
    hist_ax.set_ylabel("Density")
    hist_ax.legend(loc="upper left")

    qq_plot(x, qq_ax, ticker, label=f"{label} (standardised)")


def qq_plot(x: pd.Series, ax: plt.Axes, ticker: str, label: str, dist=None, dist_label: str = "normal") -> None:
    """Sample quantiles of the standardised series against a reference distribution.

    `dist` is a frozen scipy distribution with unit variance; the default is the
    standard normal. Points off the 45-degree line in the tails are fat tails.
    """
    from scipy import stats

    dist = dist or stats.norm()
    z = np.sort(((x - x.mean()) / x.std(ddof=1)).to_numpy())
    probs = (np.arange(1, len(z) + 1) - 0.5) / len(z)
    theory = dist.ppf(probs)
    lim = max(np.abs(z).max(), np.abs(theory).max()) * 1.05
    ax.plot([-lim, lim], [-lim, lim], zorder=1, **cfg.BENCHMARK_STYLE)
    ax.scatter(theory, z, s=9, color=color_for(ticker), edgecolor=cfg.SURFACE, linewidth=0.3, zorder=3)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xlabel(f"Theoretical quantile, {dist_label}")
    ax.set_ylabel(f"Sample quantile, {label.lower()}")


# --------------------------------------------------------------------------- #
# B6, B7 -- Figure 2.3, ACF of raw, absolute and squared returns
# --------------------------------------------------------------------------- #

ACF_TITLES = {"raw": "Raw returns", "absolute": "Absolute returns", "squared": "Squared returns"}


def acf_panels(acf: pd.DataFrame, ticker: str, label: str) -> tuple[plt.Figure, np.ndarray]:
    """Three ACF panels side by side on a shared y-scale.

    The shared scale is the point: the raw ACF only looks small next to the
    absolute and squared ones if all three are read off the same axis. The
    shaded band is the iid 95% band; the dotted line on the raw panel is the
    heteroskedasticity-robust band the verdict is judged against.
    """
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.4), sharey=True)
    lags = acf.index.to_numpy()
    top = max(0.25, float(acf[list(ACF_TITLES)].abs().max().max()) * 1.1)
    for ax, (column, title) in zip(axes, ACF_TITLES.items()):
        ax.fill_between(lags, -acf["band"], acf["band"], color=cfg.GRID_COLOR, alpha=0.8,
                        step="mid", zorder=1, label="95% band, iid")
        ax.bar(lags, acf[column], width=0.6, color=color_for(ticker), zorder=3)
        ax.axhline(0, color=cfg.INK_SECONDARY, linewidth=0.6, zorder=2)
        if column == "raw":
            for sign in (1, -1):
                ax.plot(lags, sign * acf["robust_band"], color=cfg.INK_SECONDARY, linestyle=":",
                        linewidth=1.2, zorder=4, label="95% band, robust" if sign == 1 else None)
            ax.legend(loc="upper right")
        ax.set_title(title)
        ax.set_xlabel("Lag")
        ax.set_ylim(-top, top)
    axes[0].set_ylabel(f"Autocorrelation, {label}")
    return fig, axes


# --------------------------------------------------------------------------- #
# B11 -- Figure 2.4, news impact curve
# --------------------------------------------------------------------------- #

def news_impact_plot(
    curves: dict[str, pd.Series], ticker: str, reference: str, ax: plt.Axes | None = None,
) -> plt.Axes:
    """Next-period variance against today's shock; the symmetric model as a grey reference."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6.8, 4.2))
    for name, curve in curves.items():
        style = dict(cfg.BENCHMARK_STYLE) if name == reference else {"color": color_for(ticker)}
        ax.plot(curve.index, curve, label=f"{name} (symmetric reference)" if name == reference else name, **style)
        # Direct label at the right-hand end, so identity never rests on colour alone.
        ax.annotate(name, xy=(curve.index[-1], curve.iloc[-1]), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8, color=cfg.INK_SECONDARY)
    ax.axvline(0, color=cfg.INK_SECONDARY, linewidth=0.6, zorder=1)
    ax.set_xlabel("Shock today, ε_t (% return)")
    ax.set_ylabel("Conditional variance tomorrow (%²)")
    ax.margins(x=0.08)
    ax.legend(loc="upper center")
    return ax


# --------------------------------------------------------------------------- #
# E5 -- Figure 4.1, Sharpe ratio across the 100 experiments
# --------------------------------------------------------------------------- #

def strategy_color(strategy: str) -> str:
    return cfg.STRATEGY_COLORS.get(strategy, cfg.BENCHMARK_COLOR)


def sharpe_boxplot(values: pd.DataFrame, benchmark: str = "EW", ax: plt.Axes | None = None) -> plt.Axes:
    """Horizontal box plots, one row per strategy, sorted by median (best on top).

    Boxes span the IQR and whiskers the 10th-90th percentiles, matching Table
    4.3. The benchmark's median is a dashed grey reference line.
    """
    order = values.median().sort_values().index.tolist()
    if ax is None:
        _, ax = plt.subplots(figsize=(7.6, 4.4))
    parts = ax.boxplot(
        [values[s].dropna() for s in order], vert=False, whis=(10, 90), widths=0.55,
        patch_artist=True, showfliers=True,
        medianprops={"color": cfg.INK_PRIMARY, "linewidth": 1.6},
        whiskerprops={"color": cfg.INK_SECONDARY, "linewidth": 1.0},
        capprops={"color": cfg.INK_SECONDARY, "linewidth": 1.0},
        flierprops={"marker": "o", "markersize": 2.5, "markerfacecolor": cfg.INK_SECONDARY,
                    "markeredgecolor": "none", "alpha": 0.5},
    )
    for box, strategy in zip(parts["boxes"], order):
        box.set_facecolor(strategy_color(strategy))
        box.set_alpha(0.85)
        box.set_edgecolor(cfg.SURFACE)
        box.set_linewidth(2)
    ax.set_yticks(range(1, len(order) + 1), order)
    ax.axvline(values[benchmark].median(), **cfg.BENCHMARK_STYLE, zorder=0,
               label=f"{benchmark} median ({values[benchmark].median():.2f})")
    ax.axvline(0, color=cfg.GRID_COLOR, linewidth=1.0, zorder=0)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Sharpe ratio, net of costs (annualised)")
    ax.legend(loc="lower right")
    return ax


# --------------------------------------------------------------------------- #
# E6 -- Figure 4.2, win rate against the equally weighted benchmark
# --------------------------------------------------------------------------- #

def win_rate_bars(rate: pd.Series, ax: plt.Axes | None = None) -> plt.Axes:
    """Horizontal bars of the share of experiments beating EW, sorted, 50% reference line."""
    rate = rate.dropna().sort_values()
    if ax is None:
        _, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.barh(rate.index, rate.to_numpy() * 100, height=0.62,
            color=[strategy_color(s) for s in rate.index], edgecolor=cfg.SURFACE, linewidth=2)
    for y, value in enumerate(rate.to_numpy() * 100):
        ax.text(value + 1, y, f"{value:.0f}%", va="center", fontsize=8, color=cfg.INK_PRIMARY)
    ax.axvline(50, **cfg.BENCHMARK_STYLE, zorder=0, label="50%: no better than a coin flip")
    ax.set_xlim(0, 100)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Experiments in which the strategy's net Sharpe beats EW's (%)")
    ax.legend(loc="lower right")
    return ax


# --------------------------------------------------------------------------- #
# E8 -- Figure 4.3, growth of $1 in one experiment
# --------------------------------------------------------------------------- #

def wealth_paths(paths: dict[str, pd.Series], benchmarks: dict[str, dict], ax: plt.Axes | None = None) -> plt.Axes:
    """Growth of $1 on a log y-axis. `paths` are strategies in their own colours;
    `benchmarks` maps a label to a grey line style. Every line is end-labelled."""
    if ax is None:
        _, ax = plt.subplots(figsize=(7.8, 4.4))
    finals = {}
    for name, wealth in paths.items():
        ax.plot(wealth.index, wealth, color=strategy_color(name), label=name, zorder=3)
        finals[name] = (wealth.iloc[-1], strategy_color(name))
    for label, (wealth, style) in benchmarks.items():
        ax.plot(wealth.index, wealth, label=label, zorder=2, **style)
        finals[label] = (wealth.iloc[-1], cfg.INK_SECONDARY)

    ends = pd.Series({k: v[0] for k, v in finals.items()}).sort_values()
    offsets = _spread(np.log10(ends.to_numpy()), min_gap=0.012)
    last = max(w.index[-1] for w in paths.values())
    for name, offset in zip(ends.index, offsets):
        ax.annotate(f"{name}  ${ends[name]:.2f}", xy=(last, 10.0**offset), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=8, color=cfg.INK_PRIMARY)
    ax.set_yscale("log")
    lo, hi = ax.get_ylim()
    step = next(s for s in (0.02, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0) if (hi - lo) / s <= 7)
    ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(np.arange(np.ceil(lo / step) * step, hi, step)))
    ax.yaxis.set_minor_locator(mpl.ticker.NullLocator())
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"${v:,.2f}"))
    ax.axhline(1.0, color=cfg.GRID_COLOR, linewidth=1.0, zorder=1)
    ax.xaxis.set_major_locator(mpl.dates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%Y-%m"))
    ax.set_ylabel("Growth of $1 (log scale)")
    ax.set_xlabel("Month")
    ax.margins(x=0.02)
    ax.legend(loc="upper left", ncols=3)
    return ax


# --------------------------------------------------------------------------- #
# E9 -- Figure 4.4, portfolio weights over time
# --------------------------------------------------------------------------- #

def weights_area(weights: pd.DataFrame, rebalances: list[pd.Timestamp], ax: plt.Axes | None = None) -> plt.Axes:
    """Stacked area of daily weights, fixed asset order and colours, rebalance dates marked."""
    assets = [a for a in cfg.ASSET_ORDER if a in weights.columns]
    if ax is None:
        _, ax = plt.subplots(figsize=(7.8, 4.0))
    ax.stackplot(weights.index, (weights[assets] * 100).T.to_numpy(), labels=assets,
                 colors=[color_for(a) for a in assets], edgecolor=cfg.SURFACE, linewidth=1.0, alpha=0.9)
    for i, date in enumerate(rebalances):
        ax.axvline(date, color=cfg.INK_SECONDARY, linewidth=0.8, linestyle=":", zorder=3,
                   label="Rebalance" if i == 0 else None)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Weight (%)")
    ax.set_xlabel("Month")
    ax.xaxis.set_major_locator(mpl.dates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%Y-%m"))
    ax.margins(x=0)
    ax.grid(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncols=len(assets) + 1)
    return ax
