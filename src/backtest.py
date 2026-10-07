"""Backtest engine: experiment sampler, walk-forward loop, look-ahead guard, costs.

Covers workstream C tasks C1-C9. No strategy lives here. A strategy is any
function `f(returns_window) -> weights` (plan D9), and the loop treats every
strategy identically. Portfolio returns use simple returns (definitions SS5).
Weights drift with returns between rebalances and are reset only on rebalance
dates.

Timing within one experiment, in sessions (3 years = 756 daily returns):

    returns   0 .. 503    estimation period, 2 years
    returns 504 .. 755    evaluation period, 1 year -- the only returns reported

At each rebalance the weights are *formed* at the close of session f, from
returns up to and including f. The trade *executes* at the close of f + 1
(`EXECUTION_LAG`), and the new weights first earn the return of f + 2. The first
trade executes at the close of session 503, the last estimation session, so the
whole evaluation year is invested. Later trades follow every 63 sessions.
"""

from __future__ import annotations

import inspect
import itertools
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import config as cfg

#: Numerical tolerance on the weight constraints (sum to 1, no negatives).
WEIGHT_TOL = 1e-6

#: The fallback recorded in the failure log (C6).
FALLBACK_HOLD = "Held drifted weights (no trade)"
FALLBACK_EW = "Equal weight (no previous weights)"

FAILURE_COLUMNS = ["experiment", "date", "strategy", "error", "fallback"]

WeightFunction = Callable[..., "pd.Series | np.ndarray"]


class LookAheadError(RuntimeError):
    """Raised when data dated after a formation date could reach the weights."""


# --------------------------------------------------------------------------- #
# Schedule -- the walk-forward convention, in sessions
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Schedule:
    """Session counts for one experiment. The defaults are definitions SS7."""

    estimation: int = cfg.ESTIMATION_YEARS * cfg.TRADING_DAYS
    evaluation: int = cfg.EVALUATION_YEARS * cfg.TRADING_DAYS
    rebalance_every: int = cfg.TRADING_DAYS // cfg.REBALANCES_PER_YEAR[cfg.REBALANCE_FREQ]
    lookback: int = cfg.REFIT_LOOKBACK_YEARS * cfg.TRADING_DAYS
    #: Returns used for the first estimate. None means every return in the window
    #: up to the formation date (2 years less the execution lag).
    initial_lookback: int | None = None
    lag: int = cfg.EXECUTION_LAG

    @property
    def window(self) -> int:
        """Daily returns per experiment."""
        return self.estimation + self.evaluation

    def execution_positions(self) -> list[int]:
        """Positions (in the window's return index) of the closes at which trades execute."""
        return list(range(self.estimation - 1, self.window - 1, self.rebalance_every))


# --------------------------------------------------------------------------- #
# C1 -- experiment sampler
# --------------------------------------------------------------------------- #

def sample_experiments(
    prices: pd.DataFrame,
    schedule: Schedule = Schedule(),
    n: int = cfg.N_EXPERIMENTS,
    seed: int = cfg.SEED,
    subset_size: int = cfg.SUBSET_SIZE,
    assets: list[str] | None = None,
) -> pd.DataFrame:
    """Draw `n` distinct (window, asset subset) pairs under `seed`.

    Each draw picks a subset uniformly from all `subset_size`-combinations of
    `assets`, then picks a start uniformly from the positions where every asset
    *in that subset* has a price on every session of the window, including the
    session before it (the base for the first return). That is the
    availability rule of definitions SS4. A pair already drawn is drawn again.

    Columns: `anchor` (session before the first return), `start`,
    `estimation_end`, `evaluation_start`, `end`, `assets` (a tuple in the fixed
    asset order) and `btc` (whether `BTC-USD` is in the subset).
    """
    assets = assets or [t for t in cfg.ASSET_ORDER if t in prices.columns]
    subsets = list(itertools.combinations(assets, subset_size))
    available = prices[assets].notna().to_numpy()
    dates = prices.index
    span = schedule.window + 1  # prices needed: the anchor plus one per return

    rng = np.random.default_rng(seed)
    eligible: dict[tuple[str, ...], np.ndarray] = {}
    seen: set[tuple[int, tuple[str, ...]]] = set()
    rows = []
    while len(rows) < n:
        subset = subsets[rng.integers(len(subsets))]
        if subset not in eligible:
            complete = available[:, [assets.index(t) for t in subset]].all(axis=1)
            cumulative = np.concatenate([[0], np.cumsum(complete)])
            anchors = np.arange(len(dates) - span + 1)
            eligible[subset] = anchors[cumulative[anchors + span] - cumulative[anchors] == span]
        candidates = eligible[subset]
        if len(candidates) == 0:
            raise ValueError(f"No complete {schedule.window}-session window for subset {subset}.")

        anchor = int(rng.choice(candidates))
        if (anchor, subset) in seen:
            continue
        seen.add((anchor, subset))
        rows.append(
            {
                "experiment": len(rows) + 1,
                "anchor": dates[anchor],
                "start": dates[anchor + 1],
                "estimation_end": dates[anchor + schedule.estimation],
                "evaluation_start": dates[anchor + schedule.estimation + 1],
                "end": dates[anchor + schedule.window],
                "assets": subset,
                "btc": "BTC-USD" in subset,
            }
        )
    return pd.DataFrame(rows).set_index("experiment")


def experiment_prices(prices: pd.DataFrame, experiment: pd.Series) -> pd.DataFrame:
    """The price block one experiment runs on: its subset, anchor to end."""
    return prices.loc[experiment["anchor"]: experiment["end"], list(experiment["assets"])]


# --------------------------------------------------------------------------- #
# C5 -- transaction costs
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class CostModel:
    """One-way cost per asset in basis points of traded notional (definitions SS6).

    `cost(trades) = sum_i |dw_i| * bp_i * multiplier / 10,000`, a fraction of
    portfolio value, charged at the close on which the trade executes. An asset
    with no cost entry raises a KeyError rather than trading for free.
    """

    bp: dict[str, float] = field(default_factory=lambda: dict(cfg.COSTS_BP))
    multiplier: float = 1.0

    @classmethod
    def zero(cls) -> CostModel:
        return cls(multiplier=0.0)

    @classmethod
    def stressed(cls) -> CostModel:
        """The 2x robustness scenario (workstream F)."""
        return cls(multiplier=cfg.COST_STRESS_MULTIPLIER)

    def rates(self, assets: list[str]) -> np.ndarray:
        """Cost per unit of traded weight, as a decimal, in `assets` order."""
        return np.array([self.bp[a] for a in assets]) * self.multiplier / 1e4

    def __call__(self, trades: pd.Series) -> float:
        return float(np.abs(trades.to_numpy()) @ self.rates(list(trades.index)))


# --------------------------------------------------------------------------- #
# C3 -- look-ahead guard
# --------------------------------------------------------------------------- #

def estimation_window(returns: pd.DataFrame, formation: int, lookback: int | None) -> pd.DataFrame:
    """Returns up to and including position `formation`, the last `lookback` of them."""
    first = 0 if lookback is None else max(0, formation - lookback + 1)
    return returns.iloc[first: formation + 1]


def check_no_lookahead(
    window: pd.DataFrame,
    formation_date: pd.Timestamp,
    execution_date: pd.Timestamp,
    first_return_date: pd.Timestamp,
) -> None:
    """Raise `LookAheadError` unless the window ends by the formation date, the
    trade executes after it, and the new weights earn only later returns."""
    if window.empty:
        raise LookAheadError(f"Empty estimation window at formation date {formation_date.date()}.")
    if window.index.max() > formation_date:
        raise LookAheadError(
            f"Estimation window ends {window.index.max().date()}, after the formation date "
            f"{formation_date.date()}."
        )
    if not formation_date < execution_date:
        raise LookAheadError(
            f"Trade executes {execution_date.date()}, not after the formation date {formation_date.date()}."
        )
    if not execution_date < first_return_date:
        raise LookAheadError(
            f"New weights earn the return of {first_return_date.date()}, not after the trade on "
            f"{execution_date.date()}."
        )


# --------------------------------------------------------------------------- #
# C2, C4, C6, C7 -- walk-forward loop
# --------------------------------------------------------------------------- #

@dataclass
class BacktestResult:
    """One strategy on one experiment. Returns are decimals, not percent."""

    gross: pd.Series          # daily simple returns over the evaluation period, before costs
    net: pd.Series            # the same after costs; the opening trade's cost is in day 1
    weights: pd.DataFrame     # weights at each close, from the opening trade to the end
    trades: pd.DataFrame      # one row per rebalance
    failures: pd.DataFrame    # the C6 log; empty when every optimisation succeeded
    experiment: object = None
    strategy: str | None = None

    @property
    def years(self) -> float:
        return len(self.gross) / cfg.TRADING_DAYS

    @property
    def turnover(self) -> float:
        """Annualised two-way turnover, sum |dw| per year, as a decimal (C7).

        Excludes the opening trade out of cash, which is 100% for every
        strategy and would only shift every figure by the same amount. Its cost
        is still charged.
        """
        return float(self.trades["turnover"].iloc[1:].sum() / self.years)

    @property
    def total_cost(self) -> float:
        """Sum of the costs charged, as fractions of portfolio value at each trade."""
        return float(self.trades["cost"].sum())

    def wealth(self, net: bool = True) -> pd.Series:
        """Growth of $1 invested at the close of the opening trade."""
        returns = self.net if net else self.gross
        start = pd.Series([1.0], index=[self.weights.index[0]])
        return pd.concat([start, (1 + returns).cumprod()])


def _accepts_risk_free(weight_fn: WeightFunction) -> bool:
    try:
        return "risk_free" in inspect.signature(weight_fn).parameters
    except (TypeError, ValueError):
        return False


def _as_weights(raw, assets: list[str]) -> np.ndarray:
    """Check a weight function's output against the baseline constraints.

    Long-only and fully invested, to `WEIGHT_TOL`. Noise inside the tolerance is
    clipped and renormalised. Anything outside it is an optimisation failure.
    """
    if isinstance(raw, pd.Series):
        if set(raw.index) != set(assets):
            raise ValueError(f"weights are indexed {list(raw.index)}, expected {assets}")
        w = raw.reindex(assets).to_numpy(dtype=float)
    else:
        w = np.asarray(raw, dtype=float).ravel()
        if w.shape != (len(assets),):
            raise ValueError(f"{w.size} weights returned for {len(assets)} assets")
    if not np.isfinite(w).all():
        raise ValueError("non-finite weight")
    if w.min() < -WEIGHT_TOL:
        raise ValueError(f"negative weight {w.min():.2e} violates long-only")
    if abs(w.sum() - 1) > WEIGHT_TOL:
        raise ValueError(f"weights sum to {w.sum():.6f}, not 1")
    w = np.clip(w, 0.0, None)
    return w / w.sum()


def run_backtest(
    prices: pd.DataFrame,
    weight_fn: WeightFunction,
    cost_model: CostModel | None = None,
    schedule: Schedule = Schedule(),
    *,
    risk_free: pd.Series | None = None,
    experiment: object = None,
    strategy: str | None = None,
    _window_fn: Callable[[pd.DataFrame, int, int | None], pd.DataFrame] = estimation_window,
) -> BacktestResult:
    """Walk one weight function forward through one experiment's prices.

    `prices` is the experiment's block from `experiment_prices`: the anchor
    session plus one row per return, no missing values. `weight_fn` receives
    the estimation window of simple returns, plus the matching daily risk-free
    rate (decimal) as `risk_free` if its signature asks for it and one is
    given. It returns weights as a Series indexed by asset, or an array in
    column order.

    Gross and net come from the same pass. Costs never feed back into the weight
    decisions, so the two differ only by the cost charged at each trade.

    `_window_fn` exists so the look-ahead test can swap in a leaky slicer. The
    guard runs on whatever window reaches the weight function.
    """
    cost_model = cost_model or CostModel()
    assets = list(prices.columns)
    returns = (prices / prices.shift(1) - 1).iloc[1:]
    if len(returns) != schedule.window:
        raise ValueError(f"{len(returns)} returns supplied, the schedule needs {schedule.window}")
    if returns.isna().to_numpy().any():
        raise ValueError("missing prices inside the window; the sampler should have excluded it")

    rf_daily = None
    if risk_free is not None and _accepts_risk_free(weight_fn):
        rf_daily = risk_free.reindex(returns.index).ffill() / 100 / cfg.TRADING_DAYS

    r = returns.to_numpy()
    dates = returns.index
    executions = schedule.execution_positions()
    n_assets = len(assets)

    held = np.zeros(n_assets)  # start in cash
    invested = False
    carried_cost = 0.0         # the opening trade's cost, charged into day 1's net return
    gross, net, weight_rows, trade_rows, failure_rows = [], [], [], [], []

    for pos in range(schedule.estimation - 1, schedule.window):
        day_return = 0.0
        if pos >= schedule.estimation:
            day_return = float(held @ r[pos])
            held = held * (1 + r[pos]) / (1 + day_return)  # C4: drift

        cost = 0.0
        if pos in executions:
            k = executions.index(pos)
            formation = pos - schedule.lag
            lookback = schedule.lookback if k else schedule.initial_lookback
            window = _window_fn(returns, formation, lookback)
            check_no_lookahead(window, dates[formation], dates[pos], dates[pos + 1])  # C3

            status = "ok"
            try:
                if rf_daily is not None:
                    raw = weight_fn(window, risk_free=rf_daily.loc[window.index])
                else:
                    raw = weight_fn(window)
                target = _as_weights(raw, assets)
            except LookAheadError:
                raise
            except Exception as exc:  # C6: log, fall back, never drop the run
                status = "fallback"
                fallback = FALLBACK_HOLD if invested else FALLBACK_EW
                target = held.copy() if invested else np.full(n_assets, 1 / n_assets)
                failure_rows.append(
                    {
                        "experiment": experiment,
                        "date": dates[formation],
                        "strategy": strategy,
                        "error": f"{type(exc).__name__}: {exc}",
                        "fallback": fallback,
                    }
                )

            trades = pd.Series(target - held, index=assets)
            cost = cost_model(trades)  # C5
            trade_rows.append(
                {
                    "formation": dates[formation],
                    "execution": dates[pos],
                    "observations": len(window),
                    "turnover": float(trades.abs().sum()),
                    "cost": cost,
                    "status": status,
                }
            )
            held = target
            invested = True

        if pos >= schedule.estimation:
            gross.append(day_return)
            # (1 - c0)(1 + g)(1 - c) - 1, written so that zero cost returns g exactly.
            deducted = 1 - (1 - carried_cost) * (1 - cost)
            net.append(day_return - deducted * (1 + day_return))
            carried_cost = 0.0
        else:
            carried_cost = cost
        weight_rows.append(held.copy())

    evaluation = dates[schedule.estimation:]
    return BacktestResult(
        gross=pd.Series(gross, index=evaluation, name="gross"),
        net=pd.Series(net, index=evaluation, name="net"),
        weights=pd.DataFrame(weight_rows, index=dates[schedule.estimation - 1:], columns=assets),
        trades=pd.DataFrame(trade_rows).rename_axis("rebalance"),
        failures=pd.DataFrame(failure_rows, columns=FAILURE_COLUMNS),
        experiment=experiment,
        strategy=strategy,
    )


def failure_log(results: list[BacktestResult]) -> pd.DataFrame:
    """Every failure across a set of runs, in one frame (Table A.1)."""
    frames = [res.failures for res in results if not res.failures.empty]
    if not frames:
        return pd.DataFrame(columns=FAILURE_COLUMNS)
    return pd.concat(frames, ignore_index=True)


# --------------------------------------------------------------------------- #
# C9 -- Table 3.1, experiment design
# --------------------------------------------------------------------------- #

def design_table(
    experiments: pd.DataFrame,
    calendar: pd.DatetimeIndex,
    schedule: Schedule = Schedule(),
    seed: int = cfg.SEED,
    cost_model: CostModel | None = None,
) -> pd.DataFrame:
    """Table 3.1 -- the backtest's fixed parameters, then what the sampler drew."""
    cost_model = cost_model or CostModel()
    assets = sorted({a for subset in experiments["assets"] for a in subset}, key=cfg.ASSET_ORDER.index)
    n_assets = len(assets)
    n_subsets = len(list(itertools.combinations(range(n_assets), cfg.SUBSET_SIZE)))
    n_with_btc = len(list(itertools.combinations(range(n_assets - 1), cfg.SUBSET_SIZE - 1)))
    n = len(experiments)
    td = cfg.TRADING_DAYS
    costs = ", ".join(f"{a} {cost_model.bp[a]:g}" for a in cfg.ASSET_ORDER if a in cost_model.bp)

    # Share of panel sessions that fall in at least one evaluation year.
    covered = pd.Series(False, index=calendar)
    for _, e in experiments.iterrows():
        covered.loc[e["evaluation_start"]: e["end"]] = True
    eligible = calendar[calendar >= experiments["start"].min()]

    rows = [
        ("Random seed", f"{seed}", "Fixed before any result was seen (definitions §7); numpy default_rng"),
        ("Experiments", f"{n}", "The brief's 100 three-year datasets. Every strategy runs on the same 100"),
        ("Window", f"{schedule.window} sessions ({schedule.window / td:.0f} years)",
         "Contiguous NYSE sessions, chronological order kept"),
        ("Estimation / evaluation", f"{schedule.estimation} / {schedule.evaluation} sessions",
         "Brief's suggested split: 2 years in-sample, the 3rd year out-of-sample. Only the 3rd year is scored"),
        ("Asset subset", f"{cfg.SUBSET_SIZE} of {n_assets} ({n_subsets} possible subsets)",
         "Drawn uniformly, so assets with short histories are not under-sampled"),
        ("Window start", "Uniform over eligible sessions, given the subset",
         "Eligible means every asset in the subset has a price on every session of the window"),
        ("First estimate", "All returns to the formation date "
         f"({schedule.estimation - schedule.lag} sessions)" if schedule.initial_lookback is None
         else f"Trailing {schedule.initial_lookback} sessions",
         "Uses the full 2-year estimation period, as the brief proposes"),
        ("Re-estimates", f"Trailing {schedule.lookback} sessions (1 year), rolling",
         "Brief's proposed update rule. A shorter window adapts faster to volatility regimes"),
        ("Rebalancing", f"Every {schedule.rebalance_every} sessions (quarterly), "
         f"{len(schedule.execution_positions())} trades per experiment",
         "Opening trade at the close of the last estimation session, then each quarter"),
        ("Execution lag", f"{schedule.lag} session",
         "Weights formed at close t from data up to t; trade at close t+1; earns from t+2"),
        ("Between rebalances", "Weights drift with returns",
         "Reset only on rebalance dates, as the brief requires"),
        ("Portfolio returns", "Simple returns, compounded daily",
         "Log returns are reserved for the stylised facts (definitions §5)"),
        ("Constraints", "Long-only, fully invested, no leverage",
         f"Checked on every weight vector to {WEIGHT_TOL:g}; a violation counts as a failure"),
        ("Transaction costs (bp, one-way)", costs,
         "Charged on |Δw| at each trade, opening trade included. Re-run at "
         f"{cfg.COST_STRESS_MULTIPLIER:g}× in workstream F"),
        ("Turnover", "Two-way, Σ|Δw| per year",
         "Excludes the opening trade from cash, which is 100% for every strategy"),
        ("Optimisation failure", "Logged; hold the drifted weights (equal weight if none yet)",
         "No run is dropped (Table A.1)"),
        ("Experiments including BTC-USD", f"{int(experiments['btc'].sum())} of {n}",
         f"{n_with_btc} of the {n_subsets} subsets contain BTC-USD, so about "
         f"{n * n_with_btc / n_subsets:.0f} expected"),
        ("Distinct subsets drawn", f"{experiments['assets'].nunique()} of {n_subsets}", "—"),
        ("Window starts", f"{experiments['start'].min().date()} to {experiments['start'].max().date()}",
         "Earliest start is bounded by GOVT, RNMBY or BTC-USD; every subset holds at least one"),
        ("Last evaluation session", f"{experiments['end'].max().date()}", "—"),
        ("Evaluation coverage", f"{covered.loc[eligible].mean() * 100:.1f}% of sessions",
         "Share of sessions from the earliest start that fall in at least one evaluation year. "
         "Windows overlap, so the 100 experiments are not independent"),
    ]
    return pd.DataFrame(rows, columns=["Parameter", "Value", "Rationale"]).set_index("Parameter")


def inclusion_table(experiments: pd.DataFrame) -> pd.DataFrame:
    """Appendix -- how often each asset is drawn, and when each one's windows start."""
    rows = []
    for asset in cfg.ASSET_ORDER:
        mask = experiments["assets"].map(lambda subset: asset in subset)
        if not mask.any():
            continue
        starts = experiments.loc[mask, "start"]
        rows.append(
            {
                "Ticker": asset,
                "Experiments": int(mask.sum()),
                "Share %": mask.mean() * 100,
                "Earliest start": starts.min().date().isoformat(),
                "Median start": starts.sort_values().iloc[len(starts) // 2].date().isoformat(),
            }
        )
    return pd.DataFrame(rows).set_index("Ticker")


def evaluation_years_table(experiments: pd.DataFrame) -> pd.Series:
    """Appendix -- experiments by the calendar year their evaluation period starts."""
    return experiments["evaluation_start"].dt.year.value_counts().sort_index().rename("Experiments")
