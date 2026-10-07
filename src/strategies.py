"""The eight portfolio strategies, one signature each.

Covers workstream D tasks D1-D12. Every strategy is a weight function
`f(returns) -> pd.Series` (plan D9), interchangeable in `backtest.run_backtest`.
MSR alone also takes `risk_free`, which the loop passes when its signature asks.

All eight share the baseline constraints: long-only, fully invested, no
leverage (definitions SS7). They share the estimation inputs as well, from
`estimate`:

- expected returns: the sample mean of daily simple returns, x 252;
- covariance: the sample covariance, x 252 (`COVARIANCE`). With four assets
  and at least 252 observations it is well conditioned. Ledoit-Wolf
  shrinkage towards constant correlation is available as a switch, but by
  design it pulls every correlation towards the average, and under equal
  correlations ERC, MDP and IV coincide. Making it the default would erase
  the contrast the brief asks for (D11).

Every optimiser except ERC is a small convex quadratic programme (QP) of one
form, solved *exactly* by `solve_qp`. ERC is solved by Newton's method on
Spinu's convex reformulation. A strategy that cannot produce valid weights
raises, and the backtest loop logs the failure (C6). No strategy catches its
own errors.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config as cfg

#: Tolerance on the optimality (KKT) conditions in `solve_qp` and on ERC's risk budgets.
SOLVER_TOL = 1e-10

#: Covariance estimator shared by every strategy: "sample" or "ledoit-wolf".
COVARIANCE = "sample"


class InfeasibleError(ValueError):
    """The strategy's problem has no solution on this window."""


# --------------------------------------------------------------------------- #
# Estimation inputs
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Estimate:
    """Annualised inputs for one estimation window, indexed by asset."""

    mu: pd.Series            # expected return, decimal per year
    cov: pd.DataFrame        # covariance per year
    shrinkage: float         # Ledoit-Wolf intensity (0 = sample, 1 = target); 0 when not shrunk

    @property
    def vol(self) -> pd.Series:
        return pd.Series(np.sqrt(np.diag(self.cov)), index=self.cov.index)

    @property
    def corr(self) -> pd.DataFrame:
        vol = self.vol.to_numpy()
        return self.cov / np.outer(vol, vol)


def ledoit_wolf_constant_correlation(returns: np.ndarray) -> tuple[np.ndarray, float]:
    """Ledoit and Wolf (2004), 'Honey, I shrunk the sample covariance matrix'.

    Shrinks the sample covariance S towards F, the matrix that keeps every
    sample variance and sets every correlation to the average sample
    correlation. The intensity minimises the expected Frobenius loss and is
    estimated from the data. Returns (covariance, intensity), both per period.
    """
    t, n = returns.shape
    x = returns - returns.mean(axis=0)
    s = x.T @ x / t
    sd = np.sqrt(np.diag(s))
    corr = s / np.outer(sd, sd)
    rbar = (corr.sum() - n) / (n * (n - 1))
    f = rbar * np.outer(sd, sd)
    np.fill_diagonal(f, np.diag(s))

    # pi: sum of asymptotic variances of the sample covariances.
    y = x ** 2
    pi_mat = y.T @ y / t - s ** 2
    pi_hat = pi_mat.sum()

    # rho: sum of asymptotic covariances between the target and the sample entries.
    theta = (x ** 3).T @ x / t - np.diag(s)[:, None] * s     # theta[i, j] = AsyCov(s_ii, s_ij)
    ratio = sd[None, :] / sd[:, None]                         # ratio[i, j] = sd_j / sd_i
    off = rbar / 2 * (ratio * theta + ratio.T * theta.T)
    np.fill_diagonal(off, 0.0)
    rho_hat = np.diag(pi_mat).sum() + off.sum()

    gamma_hat = ((f - s) ** 2).sum()
    if gamma_hat <= 0:  # the sample matrix already has constant correlation
        return s, 0.0
    intensity = float(np.clip((pi_hat - rho_hat) / gamma_hat / t, 0.0, 1.0))
    return intensity * f + (1 - intensity) * s, intensity


def estimate(returns: pd.DataFrame, covariance: str | None = None) -> Estimate:
    """The shared estimation inputs every strategy uses (Table 3.2)."""
    covariance = covariance or COVARIANCE
    if covariance == "sample":
        cov, intensity = returns.cov().to_numpy(), 0.0
    elif covariance == "ledoit-wolf":
        cov, intensity = ledoit_wolf_constant_correlation(returns.to_numpy())
        cov = cov * len(returns) / (len(returns) - 1)  # same divisor as the sample estimate
    else:
        raise ValueError(f"unknown covariance estimator {covariance!r}")
    assets = returns.columns
    return Estimate(
        mu=returns.mean() * cfg.TRADING_DAYS,
        cov=pd.DataFrame(cov * cfg.TRADING_DAYS, index=assets, columns=assets),
        shrinkage=intensity,
    )


# --------------------------------------------------------------------------- #
# Solvers
# --------------------------------------------------------------------------- #

def solve_qp(q: np.ndarray, c: np.ndarray, a: np.ndarray, b: float = 1.0) -> np.ndarray:
    """min 1/2 x'Qx + c'x  subject to  a'x = b, x >= 0.

    Solved exactly by enumerating the possible sets of non-zero weights. For
    each set, solve the equality-constrained KKT system, then keep the solution
    that is primal feasible (x >= 0) and dual feasible (no excluded asset would
    improve the objective). With at most six assets that is at most 63 small
    linear systems, so the answer has no solver tolerance and no
    convergence failures. When Q is positive definite the solution is unique.
    """
    n = len(c)
    if n > 12:
        raise ValueError("enumeration is exact but exponential; use it for small universes only")
    if not (a > 0).any():
        raise InfeasibleError("no x >= 0 satisfies a'x = b > 0: every coefficient is <= 0")

    best, best_value = None, np.inf
    for size in range(1, n + 1):
        for support in itertools.combinations(range(n), size):
            s = list(support)
            kkt = np.zeros((size + 1, size + 1))
            kkt[:size, :size] = q[np.ix_(s, s)]
            kkt[:size, size] = -a[s]
            kkt[size, :size] = a[s]
            rhs = np.concatenate([-c[s], [b]])
            try:
                solution = np.linalg.solve(kkt, rhs)
            except np.linalg.LinAlgError:
                continue
            x_s, nu = solution[:size], solution[size]
            if (x_s < -SOLVER_TOL).any():
                continue
            x = np.zeros(n)
            x[s] = np.clip(x_s, 0.0, None)
            multipliers = q @ x + c - nu * a        # must be >= 0 off the support
            outside = np.setdiff1d(np.arange(n), s)
            if (multipliers[outside] < -SOLVER_TOL * max(1.0, np.abs(q).max())).any():
                continue
            value = 0.5 * x @ q @ x + c @ x
            if value < best_value - 1e-15:
                best, best_value = x, value
    if best is None:
        raise InfeasibleError("no KKT point found; the covariance matrix may be singular")
    return best


def risk_contributions(weights: pd.Series, cov: pd.DataFrame) -> pd.Series:
    """Each asset's share of portfolio variance, w_i (Σw)_i / w'Σw. Sums to 1."""
    w = weights.reindex(cov.index).to_numpy()
    marginal = cov.to_numpy() @ w
    return pd.Series(w * marginal / (w @ marginal), index=cov.index)


def _equal_risk(cov: np.ndarray, max_iter: int = 100) -> np.ndarray:
    """Spinu (2013): ERC weights are y / sum(y), with y minimising
    1/2 y'Σy - (1/N) sum log y_i, a strictly convex problem. Solved by Newton's
    method with a step that keeps y > 0."""
    n = len(cov)
    budget = np.full(n, 1 / n)
    y = 1 / np.sqrt(np.diag(cov))
    y /= np.sqrt(y @ cov @ y)
    for _ in range(max_iter):
        grad = cov @ y - budget / y
        if np.abs(grad).max() < SOLVER_TOL:
            w = y / y.sum()
            return w
        hess = cov + np.diag(budget / y ** 2)
        step = np.linalg.solve(hess, grad)
        t = 1.0
        while (y - t * step <= 0).any():
            t /= 2
        y = y - t * step
    raise InfeasibleError(f"ERC Newton iteration did not converge in {max_iter} steps")


# --------------------------------------------------------------------------- #
# D1-D8 -- the eight weight functions
# --------------------------------------------------------------------------- #

def _weights(x: np.ndarray, assets) -> pd.Series:
    return pd.Series(x / x.sum(), index=assets)


def equal_weight(returns: pd.DataFrame) -> pd.Series:
    """D1 EW: w_i = 1/N. Uses no estimate at all."""
    n = returns.shape[1]
    return pd.Series(np.full(n, 1 / n), index=returns.columns)


def global_minimum_variance(returns: pd.DataFrame) -> pd.Series:
    """D2 GMV: min w'Σw."""
    est = estimate(returns)
    n = len(est.mu)
    return _weights(solve_qp(est.cov.to_numpy(), np.zeros(n), np.ones(n)), est.mu.index)


def mean_variance(returns: pd.DataFrame, risk_aversion: float = cfg.MV_RISK_AVERSION) -> pd.Series:
    """D3 MV: max w'μ - (λ/2) w'Σw, with λ = 3 on annual decimal returns."""
    est = estimate(returns)
    n = len(est.mu)
    q = risk_aversion * est.cov.to_numpy()
    return _weights(solve_qp(q, -est.mu.to_numpy(), np.ones(n)), est.mu.index)


def maximum_sharpe(returns: pd.DataFrame, risk_free: pd.Series | None = None) -> pd.Series:
    """D4 MSR: max (w'μ - r_f) / sqrt(w'Σw).

    Solved as min y'Σy subject to (μ - r_f)'y = 1, y >= 0, then w = y / sum(y).
    This is exact when at least one asset's expected excess return is positive.
    When none is, no long-only portfolio has a positive Sharpe ratio. The
    tangency portfolio does not exist, so the function raises and the loop
    logs it. `r_f` is the mean of `^IRX` over the window, annualised, so it
    covers the same period as μ.
    """
    if risk_free is None:
        raise ValueError("MSR needs the risk-free rate; pass risk_free= to run_backtest")
    est = estimate(returns)
    rf = float(risk_free.mean() * cfg.TRADING_DAYS)
    excess = est.mu.to_numpy() - rf
    if not (excess > 0).any():
        raise InfeasibleError(
            f"no asset has expected return above the risk-free rate ({rf * 100:.2f}%/yr); "
            "tangency portfolio undefined"
        )
    n = len(excess)
    return _weights(solve_qp(est.cov.to_numpy(), np.zeros(n), excess), est.mu.index)


def inverse_volatility(returns: pd.DataFrame) -> pd.Series:
    """D5 IV: w_i ∝ 1/σ_i. Ignores correlations entirely."""
    est = estimate(returns)
    return _weights(1 / est.vol.to_numpy(), est.mu.index)


def equal_risk_contribution(returns: pd.DataFrame) -> pd.Series:
    """D6 ERC: every asset contributes 1/N of portfolio variance, under the full Σ."""
    est = estimate(returns)
    w = _weights(_equal_risk(est.cov.to_numpy()), est.mu.index)
    rc = risk_contributions(w, est.cov)
    if (rc - 1 / len(rc)).abs().max() > 1e-8:
        raise InfeasibleError(f"ERC risk contributions unequal: {rc.round(6).to_dict()}")
    return w


def most_diversified(returns: pd.DataFrame) -> pd.Series:
    """D7 MDP: max w'σ / sqrt(w'Σw), the diversification ratio.

    The same problem as MSR with σ in place of μ - r_f. Since σ > 0, it is
    always feasible.
    """
    est = estimate(returns)
    n = len(est.mu)
    return _weights(solve_qp(est.cov.to_numpy(), np.zeros(n), est.vol.to_numpy()), est.mu.index)


def maximum_decorrelation(returns: pd.DataFrame) -> pd.Series:
    """D8 MDC: min w'Cw, with C the correlation matrix.

    GMV as if every asset had the same volatility.
    """
    est = estimate(returns)
    n = len(est.mu)
    return _weights(solve_qp(est.corr.to_numpy(), np.zeros(n), np.ones(n)), est.mu.index)


#: The eight weight functions, in the fixed strategy order.
STRATEGIES = {
    "EW": equal_weight,
    "GMV": global_minimum_variance,
    "MV": mean_variance,
    "MSR": maximum_sharpe,
    "IV": inverse_volatility,
    "ERC": equal_risk_contribution,
    "MDP": most_diversified,
    "MDC": maximum_decorrelation,
}
assert list(STRATEGIES) == cfg.STRATEGY_ORDER


# --------------------------------------------------------------------------- #
# D10 -- Table 3.2, strategy specifications
# --------------------------------------------------------------------------- #

def specification_table() -> pd.DataFrame:
    """Table 3.2 -- objective, constraints, parameters, inputs and shortcomings."""
    base = "w ≥ 0, Σw = 1"
    rows = [
        ("EW", "wᵢ = 1/N", base, "—", "None",
         "Ignores risk and correlation entirely; the risk is dominated by the most volatile asset"),
        ("GMV", "min wᵀΣw", base, "—", "Σ",
         "Ignores expected returns; tends to concentrate in the lowest-volatility asset"),
        ("MV", "max wᵀμ − (λ/2)wᵀΣw", base, f"λ = {cfg.MV_RISK_AVERSION:g} (annual units)", "μ, Σ",
         "Very sensitive to errors in μ; often ends up in a corner holding one or two assets"),
        ("MSR", "max (wᵀμ − r_f) / √(wᵀΣw)", base, "r_f = mean ^IRX over the window", "μ, Σ, r_f",
         "As MV, plus undefined when no asset beats r_f (logged as a failure)"),
        ("IV", "wᵢ ∝ 1/σᵢ", base, "—", "σ (diagonal of Σ)",
         "Ignores correlations, so two highly correlated assets get full weight each"),
        ("ERC", "wᵢ(Σw)ᵢ = wᵀΣw / N for all i", base, "Equal risk budgets 1/N", "Σ",
         "Low-risk assets get large weights; the result depends on the quality of the Σ estimate"),
        ("MDP", "max (wᵀσ) / √(wᵀΣw)", base, "—", "σ, Σ",
         "Favours low-correlation assets whatever their return; can concentrate"),
        ("MDC", "min wᵀCw, C = correlation matrix", base, "—", "C",
         "Treats every asset as equally volatile, so it can overweight a very risky asset that is uncorrelated with the rest"),
    ]
    columns = ["Strategy", "Objective", "Constraints", "Parameters", "Estimation inputs", "Shortcomings"]
    return pd.DataFrame(rows, columns=columns).set_index("Strategy")
