"""Stylised facts of one share's returns, at daily, weekly and monthly frequency.

Covers workstream B tasks B1-B13. Every function takes a `{frequency: Series}`
map of log returns (in percent) so the three frequencies are always treated
identically. The verdict rules in `verdicts` are fixed thresholds, written down
before they are applied -- the brief asks us to assess each fact, not assume it.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tsa.stattools import acf as _acf

from . import config as cfg

ALPHA = 0.05                  # significance level for every verdict
LB_LAGS = (5, 10, 20)         # Ljung-Box / ARCH-LM lags (plan B6, B8)
ACF_LAGS = 40                 # ACF lags plotted (plan B6)
ECONOMIC_RHO = 0.10           # |autocorrelation| below this is economically negligible
TAIL_QUANTILES = (0.01, 0.05, 0.95, 0.99)
SKEW_QUANTILE = 0.05          # quantile skewness uses the 5th and 95th percentiles
BOOTSTRAP_DRAWS = 2000        # moving-block bootstrap replications

#: A crisis window whose influence every headline statistic is checked against.
#: It is a property of the sample, not of the share: March 2020 holds the panel's
#: largest daily moves for most assets (notebook 01, Table A1.1).
STRESS_WINDOW = ("2020-02-15", "2020-05-15")
STRESS_LABEL = "COVID crash, mid-Feb to mid-May 2020"


# --------------------------------------------------------------------------- #
# Input -- complete periods only
# --------------------------------------------------------------------------- #

def share_returns(
    returns: dict[tuple[str, str], pd.DataFrame],
    calendar: pd.DatetimeIndex,
    ticker: str = cfg.STYLISED_FACTS_TICKER,
) -> dict[str, pd.Series]:
    """Log returns of `ticker` in percent, keyed by frequency, complete periods only.

    The daily series starts on the panel's second session, so the first week and
    month always miss at least one day's move and are dropped. The last week or
    month is dropped when the panel ends before that period does (an extraction
    mid-month leaves a stub of a few sessions).
    """
    out = {}
    for frequency in cfg.FREQUENCY_ORDER:
        series = returns[(frequency, "log")][ticker].dropna() * 100
        if frequency != "daily":
            series = series.iloc[1:]
            if series.index[-1] > calendar[-1]:
                series = series.iloc[:-1]
        out[frequency] = series.rename(f"{ticker} {frequency}")
    return out


# --------------------------------------------------------------------------- #
# B1, B4, B12 -- Table 2.1, descriptive statistics and normality tests
# --------------------------------------------------------------------------- #

def block_bootstrap(x: np.ndarray, statistic, draws: int = BOOTSTRAP_DRAWS, seed: int = cfg.SEED) -> np.ndarray:
    """`statistic` on `draws` circular moving-block resamples of `x`.

    Blocks of length n^(1/3) keep the short-range dependence -- volatility
    clustering above all -- that an iid bootstrap would destroy. `statistic`
    takes a (draws, n) array and returns one value per row.
    """
    n = len(x)
    block = max(1, int(round(n ** (1 / 3))))
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n, size=(draws, -(-n // block)))
    index = (starts[:, :, None] + np.arange(block)).reshape(draws, -1)[:, :n] % n
    return statistic(x[index])


def quantile_skew(x: np.ndarray, q: float = SKEW_QUANTILE) -> np.ndarray:
    """(Q(1-q) + Q(q) - 2 median) / (Q(1-q) - Q(q)), along the last axis.

    Bounded in [-1, 1] and set by quantiles, not moments, so a handful of crash
    days cannot drive it. Negative means the lower tail reaches further.
    """
    lo, mid, hi = np.quantile(x, [q, 0.5, 1 - q], axis=-1)
    return (hi + lo - 2 * mid) / (hi - lo)


def _bootstrap_p(estimate: float, draws: np.ndarray) -> float:
    """Two-sided p-value for `estimate` = 0, from the bootstrap draws re-centred on zero."""
    return float(np.mean(np.abs(draws - draws.mean()) >= abs(estimate)))


def anderson_darling(x: np.ndarray) -> tuple[float, float]:
    """Anderson-Darling normality test, mean and variance estimated.

    scipy computes the statistic on the log scale, so a single extreme day
    cannot overflow it to infinity. The p-value is the D'Agostino and Stephens
    (1986, table 4.9) approximation, as statsmodels' `normal_ad` uses.
    """
    n = len(x)
    stat = float(stats.anderson(x, "norm", method="interpolate").statistic)
    a = stat * (1 + 0.75 / n + 2.25 / n**2)
    if a >= 153.467:
        p = 0.0
    elif a >= 0.6:
        p = np.exp(1.2937 - 5.709 * a + 0.0186 * a**2)
    elif a >= 0.34:
        p = np.exp(0.9177 - 4.279 * a - 1.38 * a**2)
    elif a >= 0.2:
        p = 1 - np.exp(-8.318 + 42.796 * a - 59.938 * a**2)
    else:
        p = 1 - np.exp(-13.436 + 101.14 * a - 223.73 * a**2)
    return stat, float(p)


def describe(series: pd.Series) -> dict[str, float]:
    """One row of Table 2.1. Kurtosis is *excess* kurtosis.

    Both skewness p-values come from a moving-block bootstrap. The textbook
    D'Agostino skew test assumes normal data; under fat tails its standard
    error is several times too small and it finds skew that is not there.
    `Q-skew` is the quantile skewness at the 5th/95th percentiles.
    """
    x = series.dropna().to_numpy()
    jb = stats.jarque_bera(x)
    sw = stats.shapiro(x)
    ad_stat, ad_p = anderson_darling(x)
    skew = float(stats.skew(x))
    qskew = float(quantile_skew(x))
    return {
        "n": len(x),
        "Mean %": x.mean(),
        "SD %": x.std(ddof=1),
        "Min %": x.min(),
        "Max %": x.max(),
        "Skew": skew,
        "Skew p": _bootstrap_p(skew, block_bootstrap(x, lambda b: stats.skew(b, axis=1))),
        "Q-skew": qskew,
        "Q-skew p": _bootstrap_p(qskew, block_bootstrap(x, quantile_skew)),
        "Excess kurtosis": stats.kurtosis(x),
        "Kurtosis p": stats.kurtosistest(x).pvalue,
        "JB stat": jb.statistic,
        "JB p": jb.pvalue,
        "SW stat": sw.statistic,
        "SW p": sw.pvalue,
        "AD stat": ad_stat,
        "AD p": ad_p,
    }


def descriptive_table(series_by_freq: dict[str, pd.Series], label: str = "") -> pd.DataFrame:
    """Table 2.1 -- one row per frequency in the fixed order."""
    rows = {f"{label}{f}" if label else f: describe(s) for f, s in series_by_freq.items()}
    return pd.DataFrame(rows).T.rename_axis("Series")


# --------------------------------------------------------------------------- #
# B5 -- Table 2.2, tail quantiles
# --------------------------------------------------------------------------- #

def tail_table(series_by_freq: dict[str, pd.Series]) -> pd.DataFrame:
    """Table 2.2 -- empirical against normal-implied quantiles.

    The normal is fitted by the sample mean and standard deviation. A ratio
    above 1 in both tails means the empirical quantile sits further from the
    centre than a normal with the same variance would put it.
    """
    rows = []
    for frequency, series in series_by_freq.items():
        x = series.dropna()
        mu, sd = x.mean(), x.std(ddof=1)
        for q in TAIL_QUANTILES:
            empirical = x.quantile(q)
            normal = stats.norm.ppf(q, mu, sd)
            rows.append(
                {
                    "Frequency": frequency,
                    "Quantile %": q * 100,
                    "Empirical %": empirical,
                    "Normal-implied %": normal,
                    # Distance from the mean, so the ratio reads the same in both tails.
                    "Ratio": (empirical - mu) / (normal - mu),
                }
            )
    return pd.DataFrame(rows).set_index(["Frequency", "Quantile %"])


def exceedance_table(series_by_freq: dict[str, pd.Series], k: tuple[int, ...] = (3, 4, 5)) -> pd.DataFrame:
    """How often |r - mean| exceeds k standard deviations, against the normal rate."""
    rows = []
    for frequency, series in series_by_freq.items():
        x = series.dropna()
        z = (x - x.mean()) / x.std(ddof=1)
        for sigmas in k:
            observed = int((z.abs() > sigmas).sum())
            expected = 2 * stats.norm.sf(sigmas) * len(z)
            rows.append(
                {
                    "Frequency": frequency,
                    "Beyond ±kσ": sigmas,
                    "Observed": observed,
                    "Normal-expected": expected,
                    "Ratio": observed / expected,
                }
            )
    return pd.DataFrame(rows).set_index(["Frequency", "Beyond ±kσ"])


# --------------------------------------------------------------------------- #
# B6, B7, B8 -- autocorrelation, Ljung-Box, ARCH-LM
# --------------------------------------------------------------------------- #

TRANSFORMS = {"raw": lambda x: x, "absolute": np.abs, "squared": np.square}


def acf_frame(series: pd.Series, lags: int = ACF_LAGS) -> pd.DataFrame:
    """ACF of raw, absolute and squared returns, lags 1..`lags`.

    `band` is the iid 95% band, +/-1.96/sqrt(n). `robust_band` widens it for
    conditional heteroskedasticity (each lag's variance estimated from the
    cross-products, as in the robust portmanteau below); it is the honest band
    for the raw series, whose squares are themselves autocorrelated.
    """
    x = series.dropna()
    n = len(x)
    frame = pd.DataFrame(
        {name: _acf(f(x), nlags=lags, fft=True)[1:] for name, f in TRANSFORMS.items()},
        index=pd.RangeIndex(1, lags + 1, name="Lag"),
    )
    frame["band"] = 1.96 / np.sqrt(n)
    frame["robust_band"] = 1.96 * np.sqrt(_robust_lag_variance(x, lags) / n)
    return frame


def _robust_lag_variance(series: pd.Series, lags: int) -> np.ndarray:
    """n * Var(rho_k) under heteroskedasticity; equals 1 for iid data."""
    x = (series - series.mean()).to_numpy()
    gamma0 = (x**2).mean()
    return np.array([((x[k:] * x[:-k]) ** 2).mean() / gamma0**2 for k in range(1, lags + 1)])


def robust_portmanteau(series: pd.Series, lags: int) -> tuple[float, float]:
    """Heteroskedasticity-robust portmanteau: Q* = sum_k t_k^2, chi2(lags).

    t_k = sum(x_t x_{t-k}) / sqrt(sum(x_t^2 x_{t-k}^2)) on demeaned returns.
    Plain Ljung-Box assumes iid errors and over-rejects when volatility
    clusters; this version does not, so it is the one the verdict uses.
    """
    x = (series.dropna() - series.dropna().mean()).to_numpy()
    q = 0.0
    for k in range(1, lags + 1):
        cross = x[k:] * x[:-k]
        q += cross.sum() ** 2 / (cross**2).sum()
    return q, stats.chi2.sf(q, lags)


def dependence_table(series_by_freq: dict[str, pd.Series], lags: tuple[int, ...] = LB_LAGS) -> pd.DataFrame:
    """Table 2.3 -- Ljung-Box on raw, |r| and r^2, the robust portmanteau, ARCH-LM.

    Rows: (frequency, test). Columns: statistic and p-value at each lag.
    """
    rows = []
    for frequency, series in series_by_freq.items():
        x = series.dropna()
        tests: dict[str, list[tuple[float, float]]] = {}
        for name, f in TRANSFORMS.items():
            lb = acorr_ljungbox(f(x), lags=list(lags))
            tests[f"Ljung–Box, {name}"] = list(zip(lb["lb_stat"], lb["lb_pvalue"]))
        tests["Robust portmanteau, raw"] = [robust_portmanteau(x, k) for k in lags]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)  # statsmodels return-type notice
            tests["ARCH-LM"] = [het_arch(x - x.mean(), nlags=k)[:2] for k in lags]

        for test, results in tests.items():
            row = {"Frequency": frequency, "Test": test}
            for k, (stat, p) in zip(lags, results):
                row[f"Q({k})"] = stat
                row[f"p({k})"] = p
            rows.append(row)
    return pd.DataFrame(rows).set_index(["Frequency", "Test"])


# --------------------------------------------------------------------------- #
# B9, B10 -- Table 2.4, volatility models
# --------------------------------------------------------------------------- #

#: The four specifications. GARCH-n vs GARCH-t isolates the error assumption;
#: GJR and EGARCH add the asymmetry term that is the leverage-effect test.
MODELS: dict[str, dict[str, object]] = {
    "GARCH-N": {"vol": "GARCH", "p": 1, "o": 0, "q": 1, "dist": "normal"},
    "GARCH-t": {"vol": "GARCH", "p": 1, "o": 0, "q": 1, "dist": "t"},
    "GJR-t": {"vol": "GARCH", "p": 1, "o": 1, "q": 1, "dist": "t"},
    "EGARCH-t": {"vol": "EGARCH", "p": 1, "o": 1, "q": 1, "dist": "t"},
}

#: arch's parameter names, mapped to the symbols used in the report.
PARAM_LABELS = {
    "mu": "μ",
    "omega": "ω",
    "alpha[1]": "α",
    "gamma[1]": "γ",
    "beta[1]": "β",
    "nu": "ν",
}

#: The model whose standardised residuals and news impact curve the report uses.
PREFERRED_MODEL = "GJR-t"


@dataclass
class FitResult:
    name: str
    frequency: str
    result: object          # arch ARCHModelResult
    converged: bool
    message: str

    @property
    def params(self) -> pd.Series:
        return self.result.params

    @property
    def std_resid(self) -> pd.Series:
        return self.result.std_resid.dropna()

    @property
    def persistence(self) -> float:
        """alpha + beta (+ gamma/2 for GJR); beta alone for EGARCH."""
        p = self.params
        if self.name.startswith("EGARCH"):
            return float(p["beta[1]"])
        return float(p["alpha[1]"] + p["beta[1]"] + p.get("gamma[1]", 0.0) / 2)

    @property
    def half_life(self) -> float:
        """Periods for a volatility shock to decay by half: ln(0.5) / ln(persistence)."""
        return float(np.log(0.5) / np.log(self.persistence)) if 0 < self.persistence < 1 else np.nan

    @property
    def degenerate(self) -> bool:
        """No clustering identified: no ARCH-type term (alpha, or gamma where the
        model has one) is significant at `ALPHA`.

        This covers both ways a GARCH fit collapses on too little data -- alpha
        on its zero bound with beta at one, or beta on its zero bound with an
        insignificant alpha -- and any case in between.
        """
        terms = [t for t in ("alpha[1]", "gamma[1]") if t in self.params.index]
        return not any(self.result.pvalues[t] < ALPHA for t in terms)


def fit_models(series: pd.Series, frequency: str) -> dict[str, FitResult]:
    """Fit every model in `MODELS` to one series (percent log returns), constant mean.

    Convergence failures are caught and recorded rather than raised: the plan
    asks that failures be logged, never silently dropped.
    """
    fits = {}
    for name, spec in MODELS.items():
        model = arch_model(series.dropna(), mean="Constant", **spec)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = model.fit(disp="off")
        converged = result.convergence_flag == 0
        message = "" if converged else (str(caught[-1].message).splitlines()[0] if caught else "optimizer flag")
        fits[name] = FitResult(name, frequency, result, converged, message)
    return fits


def model_table(fits: dict[str, FitResult]) -> pd.DataFrame:
    """Table 2.4 -- one block of (estimate, SE, p) per model, parameters as rows.

    Fit statistics (log-likelihood, AIC, BIC, persistence) are appended as
    rows with only the estimate column filled.
    """
    blocks = {}
    for name, fit in fits.items():
        r = fit.result
        block = pd.DataFrame({"Estimate": r.params, "SE": r.std_err, "p": r.pvalues})
        block.index = [PARAM_LABELS.get(i, i) for i in block.index]
        extra = pd.DataFrame(
            {"Estimate": [fit.persistence, fit.half_life, r.loglikelihood, r.aic, r.bic, float(fit.converged)]},
            index=["Persistence", "Half-life", "Log-likelihood", "AIC", "BIC", "Converged"],
        )
        blocks[name] = pd.concat([block, extra])
    order = list(PARAM_LABELS.values()) + ["Persistence", "Half-life", "Log-likelihood", "AIC", "BIC", "Converged"]
    table = pd.concat(blocks, axis=1)
    return table.reindex([i for i in order if i in table.index]).rename_axis("Parameter")


# --------------------------------------------------------------------------- #
# B10b -- robustness: sub-samples, mean specification, the crisis window
# --------------------------------------------------------------------------- #

def excluding_stress(series: pd.Series, window: tuple[str, str] = STRESS_WINDOW) -> pd.Series:
    """`series` without the observations dated inside `window`."""
    return series.drop(series.loc[window[0]: window[1]].index)


def stress_sensitivity(series_by_freq: dict[str, pd.Series], window: tuple[str, str] = STRESS_WINDOW) -> pd.DataFrame:
    """The headline statistics with and without the crisis window.

    A fact that holds only because of a few weeks of extreme returns is a fact
    about those weeks; this shows which verdicts are that fragile.
    """
    rows = []
    for frequency, series in series_by_freq.items():
        for label, x in (("Full sample", series), ("Excluding window", excluding_stress(series, window))):
            d = describe(x)
            rows.append(
                {
                    "Frequency": frequency,
                    "Sample": label,
                    "n": d["n"],
                    "Skew": d["Skew"],
                    "Skew p": d["Skew p"],
                    "Q-skew": d["Q-skew"],
                    "Q-skew p": d["Q-skew p"],
                    "Excess kurtosis": d["Excess kurtosis"],
                    "Lag-1 ρ": float(pd.Series(x.to_numpy()).autocorr()),
                    f"Q*({LB_LAGS[1]}) p": robust_portmanteau(x, LB_LAGS[1])[1],
                }
            )
    return pd.DataFrame(rows).set_index(["Frequency", "Sample"])


def asymmetry_robustness(series: pd.Series, window: tuple[str, str] = STRESS_WINDOW) -> pd.DataFrame:
    """GJR-t asymmetry term under alternative specifications and samples.

    The sample is split at its midpoint date, so the check does not depend on
    which share or which period is being analysed.
    """
    x = series.dropna()
    middle = x.index[len(x) // 2]
    variants = {
        "Baseline (constant mean)": (x, "Constant"),
        "AR(1) mean": (x, "AR"),
        f"First half, to {x.index[len(x) // 2 - 1]:%Y-%m}": (x.loc[: x.index[len(x) // 2 - 1]], "Constant"),
        f"Second half, from {middle:%Y-%m}": (x.loc[middle:], "Constant"),
        "Excluding crisis window": (excluding_stress(x, window), "Constant"),
    }
    rows = []
    for label, (sample, mean) in variants.items():
        model = arch_model(sample, mean=mean, lags=1 if mean == "AR" else 0, **MODELS["GJR-t"])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = model.fit(disp="off")
        p = r.params
        rows.append(
            {
                "Variant": label,
                "n": int(r.nobs),
                "γ": p["gamma[1]"],
                "γ p": r.pvalues["gamma[1]"],
                "α": p["alpha[1]"],
                "Persistence": p["alpha[1]"] + p["beta[1]"] + p["gamma[1]"] / 2,
                "ν": p["nu"],
                "Converged": r.convergence_flag == 0,
            }
        )
    return pd.DataFrame(rows).set_index("Variant")


def rolling_volatility(daily: pd.Series, window: int = 63) -> pd.Series:
    """Annualised rolling volatility of daily percent returns, in percent."""
    return daily.rolling(window).std() * np.sqrt(cfg.TRADING_DAYS)


# --------------------------------------------------------------------------- #
# B11 -- news impact curve
# --------------------------------------------------------------------------- #

def news_impact(fit: FitResult, shocks: np.ndarray) -> pd.Series:
    """Next-period conditional variance as a function of today's shock.

    Lagged variance is held at the model's unconditional level, the standard
    convention (Engle and Ng, 1993). Shocks are in the same percent units as
    the returns.
    """
    p = fit.params
    if fit.name.startswith("EGARCH"):
        sigma2 = np.exp(p["omega"] / (1 - p["beta[1]"]))
        z = shocks / np.sqrt(sigma2)
        # arch centres |z| by sqrt(2/pi) whatever the error distribution.
        log_var = p["omega"] + p["alpha[1]"] * (np.abs(z) - np.sqrt(2 / np.pi)) + p["gamma[1]"] * z + p["beta[1]"] * np.log(sigma2)
        values = np.exp(log_var)
    else:
        gamma = p.get("gamma[1]", 0.0)
        sigma2 = p["omega"] / (1 - p["alpha[1]"] - p["beta[1]"] - gamma / 2)
        values = p["omega"] + (p["alpha[1]"] + gamma * (shocks < 0)) * shocks**2 + p["beta[1]"] * sigma2
    return pd.Series(values, index=pd.Index(shocks, name="Shock %"), name=fit.name)


# --------------------------------------------------------------------------- #
# B13 -- Table 2.5, verdicts
# --------------------------------------------------------------------------- #

FACTS = [
    "1. Little or no serial correlation in raw returns",
    "2. Non-normal distribution, fat tails",
    "3. Asymmetry / negative skewness",
    "4. Volatility clustering",
    "5. Leverage effect",
    "6. Conditional non-normality",
]

#: Where the evidence for each fact sits in the report.
FACT_SOURCES = {
    FACTS[0]: "Table 2.3, Figure 2.3a",
    FACTS[1]: "Tables 2.1–2.2, Figure 2.2",
    FACTS[2]: "Table 2.1, Figure 2.2",
    FACTS[3]: "Table 2.3, Figures 2.1, 2.3b–c",
    FACTS[4]: "Table 2.4, Figure 2.4",
    FACTS[5]: "Table 2.1, Figure 2.5",
}

SUPPORTED, PARTIAL, NOT_SUPPORTED = "Supported", "Partial", "Not supported"

#: The rules, written once and printed in the notebook beside the table.
RULES = {
    FACTS[0]: (
        f"Supported if the robust portmanteau does not reject at any of lags {LB_LAGS}. "
        f"Partial if it rejects but every |ρ_k|, k ≤ 20, is below {ECONOMIC_RHO:.2f} "
        "(detectable, economically negligible). Not supported otherwise."
    ),
    FACTS[1]: (
        "Supported if Jarque–Bera rejects and excess kurtosis is positive and significant "
        "(D'Agostino kurtosis test). Partial if only one of JB, Shapiro–Wilk, Anderson–Darling "
        "rejects, or kurtosis is not significant. Not supported if none rejects."
    ),
    FACTS[2]: (
        "Two measures, each tested by moving-block bootstrap: moment skewness and quantile "
        f"skewness ({SKEW_QUANTILE:.0%}/{1 - SKEW_QUANTILE:.0%}). Supported if both are negative and "
        "significant. Partial if one is. Not supported if neither is (significant positive skew "
        "is reported in the evidence, but is not the negative kind the fact describes)."
    ),
    FACTS[3]: (
        "Supported if Ljung–Box on |r| and r² and ARCH-LM all reject at every lag. Partial if "
        "some reject. Not supported if none does."
    ),
    FACTS[4]: (
        "Supported if the asymmetry term has the leverage sign (GJR γ > 0, EGARCH γ < 0) and is "
        "significant in both converged models. Partial if significant in one. Not supported otherwise."
    ),
    FACTS[5]: (
        f"Supported if Jarque–Bera rejects on the {PREFERRED_MODEL} standardised residuals and "
        "the model identifies clustering (at least one of α, γ significant). Partial if JB rejects "
        "but no clustering is identified, so the residuals are barely filtered. Not supported if "
        "JB does not reject."
    ),
}


def _p(p: float) -> str:
    return "p<0.001" if p < 0.001 else f"p={p:.3f}"


def verdicts(
    descriptive: pd.DataFrame,
    dependence: pd.DataFrame,
    acfs: dict[str, pd.DataFrame],
    fits: dict[str, dict[str, FitResult]],
    residual_stats: pd.DataFrame,
) -> pd.DataFrame:
    """Table 2.5 -- a verdict and the statistic behind it, for each fact and frequency.

    `descriptive` and `residual_stats` are Table 2.1 frames indexed by frequency;
    `dependence` is Table 2.3; `acfs` and `fits` are keyed by frequency.
    """
    cells: dict[tuple[str, str], tuple[str, str]] = {}
    for frequency in cfg.FREQUENCY_ORDER:
        d = descriptive.loc[frequency]
        dep = dependence.loc[frequency]
        lag_cols = [f"p({k})" for k in LB_LAGS]

        # 1 -- serial correlation
        robust = dep.loc["Robust portmanteau, raw", lag_cols]
        rho = acfs[frequency]["raw"].loc[1:20]
        worst = rho.abs().idxmax()
        if (robust >= ALPHA).all():
            v = SUPPORTED
        elif rho.abs().max() < ECONOMIC_RHO:
            v = PARTIAL
        else:
            v = NOT_SUPPORTED
        cells[(FACTS[0], frequency)] = (v, f"Q*({LB_LAGS[1]}) {_p(robust.iloc[1])}; max |ρ| {rho.abs().max():.2f} at lag {worst}")

        # 2 -- fat tails
        rejects = [d["JB p"] < ALPHA, d["SW p"] < ALPHA, d["AD p"] < ALPHA]
        fat = d["Excess kurtosis"] > 0 and d["Kurtosis p"] < ALPHA
        if d["JB p"] < ALPHA and fat:
            v = SUPPORTED
        elif any(rejects):
            v = PARTIAL
        else:
            v = NOT_SUPPORTED
        cells[(FACTS[1], frequency)] = (v, f"Excess kurtosis {d['Excess kurtosis']:.2f}; JB {_p(d['JB p'])}")

        # 3 -- skewness
        negative = int(d["Skew"] < 0 and d["Skew p"] < ALPHA) + int(d["Q-skew"] < 0 and d["Q-skew p"] < ALPHA)
        v = SUPPORTED if negative == 2 else PARTIAL if negative == 1 else NOT_SUPPORTED
        cells[(FACTS[2], frequency)] = (
            v, f"Skew {d['Skew']:.2f}, {_p(d['Skew p'])}; Q-skew {d['Q-skew']:.2f}, {_p(d['Q-skew p'])}"
        )

        # 4 -- volatility clustering
        tests = ["Ljung–Box, absolute", "Ljung–Box, squared", "ARCH-LM"]
        grid = dep.loc[tests, lag_cols] < ALPHA
        if grid.all().all():
            v = SUPPORTED
        elif grid.any().any():
            v = PARTIAL
        else:
            v = NOT_SUPPORTED
        cells[(FACTS[3], frequency)] = (
            v,
            f"LB |r|({LB_LAGS[1]}) {_p(dep.loc['Ljung–Box, absolute', lag_cols[1]])}; "
            f"{int(grid.to_numpy().sum())}/{grid.size} tests reject",
        )

        # 5 -- leverage
        gjr, egarch = fits[frequency]["GJR-t"], fits[frequency]["EGARCH-t"]
        hits, parts = 0, []
        for fit, sign in ((gjr, 1), (egarch, -1)):
            g, p = fit.params["gamma[1]"], fit.result.pvalues["gamma[1]"]
            label = fit.name.split("-")[0]
            if not fit.converged:
                parts.append(f"{label} not converged")
                continue
            hits += int(np.sign(g) == sign and p < ALPHA)
            parts.append(f"{label} γ {g:.3f}, {_p(p)}")
        v = SUPPORTED if hits == 2 else PARTIAL if hits == 1 else NOT_SUPPORTED
        cells[(FACTS[4], frequency)] = (v, "; ".join(parts))

        # 6 -- conditional non-normality
        z = residual_stats.loc[frequency]
        preferred = fits[frequency][PREFERRED_MODEL]
        if z["JB p"] < ALPHA:
            v = PARTIAL if preferred.degenerate else SUPPORTED
        else:
            v = NOT_SUPPORTED
        nu = preferred.params["nu"]
        cells[(FACTS[5], frequency)] = (v, f"Resid. excess kurt. {z['Excess kurtosis']:.2f}; JB {_p(z['JB p'])}; ν {nu:.1f}")

    columns = pd.MultiIndex.from_product([cfg.FREQUENCY_ORDER, ["Verdict", "Evidence"]])
    table = pd.DataFrame(index=pd.Index(FACTS, name="Stylised fact"), columns=columns, dtype=object)
    for (fact, frequency), (verdict, evidence) in cells.items():
        table.loc[fact, (frequency, "Verdict")] = verdict
        table.loc[fact, (frequency, "Evidence")] = evidence
    table[("", "Evidence in")] = [FACT_SOURCES[f] for f in FACTS]
    return table
