# 3. Stylised facts

*Draft of report section 3. Target ~3 pages alongside Tables 2.1–2.5 and Figures 2.1–2.5. Every
number is produced by [`notebooks/02_stylised_facts.ipynb`](../../notebooks/02_stylised_facts.ipynb);
figures below are from the 5 October 2026 extraction and will be refreshed in the final re-run (plan G2).*

---

## 3.1 What we tested, and the answer

The brief asks us to take one share and test six features commonly said to describe asset returns —
and to **assess** each one rather than assume it. We use **Taiwan Semiconductor (`TSM`)**, the most
liquid single stock in the universe, over the full fifteen-year panel: **3,771 daily, 782 weekly and
179 monthly** log returns from October 2011 to early October 2026 (monthly to September, the last complete month).

Each verdict follows a rule fixed in advance and applied mechanically (rules in the appendix), at the
5% significance level. Table 2.5 is the result.

**Table 2.5 — Stylised facts summary, `TSM`.** 2011-10 to 2026-10; n = 3,771 / 782 / 179.

| Stylised fact | Daily | Weekly | Monthly | Evidence |
| --- | --- | --- | --- | --- |
| 1. Little or no serial correlation in raw returns | Partial | Supported | Supported | Table 2.3, Figure 2.3a |
| 2. Non-normal distribution, fat tails | Supported | Supported | Supported | Tables 2.1–2.2, Figure 2.2 |
| 3. Asymmetry / negative skewness | Not supported | Not supported | Not supported | Table 2.1, Figure 2.2 |
| 4. Volatility clustering | Supported | Supported | Partial | Table 2.3, Figures 2.1, 2.3b–c |
| 5. Leverage effect | Not supported | Not supported | Not supported | Table 2.4, Figure 2.4 |
| 6. Conditional non-normality | Supported | Supported | Not supported | Table 2.1, Figure 2.5 |

The pattern is as informative as any single cell. **The facts about the *size* of returns hold
strongly** — fat tails, volatility clustering, and fat tails that survive a volatility model. **The
facts about *direction* and *asymmetry* do not** — returns are not skewed, and bad news does not raise
volatility measurably more than good news. And almost everything weakens as returns aggregate from
daily to monthly, which is what we would expect if most of the non-normality is short-horizon.

## 3.2 Serial correlation: absent, except for one day

At weekly and monthly frequency there is no serial correlation in returns: no test rejects at any lag
(Table 2.3). At daily frequency there is one exception — a **negative lag-1 autocorrelation of −0.09**
(Figure 2.3a). An up day is slightly more likely to be followed by a partial reversal.

This result needed care. The standard test for autocorrelation (Ljung–Box) assumes calm, constant
volatility; when volatility clusters, as it does here, the test finds autocorrelation that is not there.
We therefore re-ran it in a form robust to changing volatility. The lag-1 effect survives (robust
p<0.001), so it is real, but it is **economically negligible**: it explains under 1% of the next day's
return variance, far less than the cost of trading on it. We record the daily cell as *Partial*.

The likely source is structural rather than behavioural. `TSM` is an ADR: it trades in New York while
the underlying share trades in Taipei during the US night. Part of each day's ADR price is the market
catching up with, and partly reversing, a move that happened overnight in Taiwan. The effect disappears
at weekly frequency, as it should if it is a timing artefact.

## 3.3 The distribution: fat-tailed, but not skewed

**Fat tails are the strongest result in the section** (Table 2.1). Daily excess kurtosis is **4.1**
(a normal distribution has 0), and all three normality tests reject decisively. In practical terms
(Table 2.2), daily `TSM` has more very quiet days *and* more extreme days than a normal distribution
with the same volatility: the 5% and 95% quantiles sit slightly inside the normal's, the 1% and 99%
outside them. Moves beyond four standard deviations occurred **16 times** in fifteen years, against
fewer than one expected under normality.

Fat tails **fade with aggregation**: excess kurtosis falls to about 1.1 weekly and 1.3 monthly. Monthly
normality is still rejected by Jarque–Bera (p = 0.001) and Shapiro–Wilk (p = 0.012), but only narrowly
missed by Anderson–Darling (p = 0.061). With 179 observations the monthly evidence is real but thinner.

**Skewness is not supported at any frequency.** The measured skewness is +0.01 daily, −0.01 weekly and
+0.23 monthly, none significantly different from zero. Negative skewness — large falls more frequent
than large rises — is a well-documented property of equity *indices*, but this share does not show it.
Its largest daily rises (+11.9% in July 2020, +11.6% in April 2025, +11.3% in May 2023) are almost as
large as its largest falls (−15.1% in March 2020, −14.3% in January 2025). Over this sample `TSM` was a
growth stock repriced upward in a series of jumps, and that offsets the crash risk that produces
negative skew elsewhere. We report this as *Not supported* rather than forcing the textbook answer.

## 3.4 Volatility clustering: strong and persistent

Large moves cluster together. Figure 2.1 shows calm stretches (2013–14, 2017) alternating with
turbulent ones (2020, 2022, 2024–25), and Figure 2.3b–c measures it: the autocorrelation of absolute
and squared returns is positive at every lag out to 40 days. Every test rejects at daily and weekly
frequency (Table 2.3).

A GARCH(1,1) model puts a number on it (Table 2.4). Persistence is **0.99**, which means a volatility
shock takes roughly **six months (about 128 trading days) to halve**. Rolling three-month volatility ranged from **14%** (June
2017) to **64%** (April 2020) annualised, against a full-sample average of 32%.

At monthly frequency the evidence is only *Partial*. Short-lag tests on absolute returns still reject,
but the GARCH model cannot be estimated: with 179 monthly observations the ARCH term falls to zero, so
the model finds no clustering. Monthly averaging smooths away most of the day-to-day clustering that
drives the result.

## 3.5 Leverage effect: right sign, not significant

The leverage effect says that falls raise future volatility more than rises of the same size. We test
it with two asymmetric models, GJR-GARCH and EGARCH. Both estimate the asymmetry term with the
**expected sign**, and **neither is significant** (GJR p = 0.36, EGARCH p = 0.12; Table 2.4). The news
impact curve (Figure 2.4) shows the scale: after a −4 standard deviation day, next-day variance is
only about **9% higher** than after a +4 standard deviation day.

We checked that this is not an artefact of the model. Adding an autoregressive term to the mean, or
splitting the sample at 2019, leaves the asymmetry insignificant in every case. The finding is
consistent with the literature, which locates the leverage effect mainly at **index** level. For a
single growth stock, large positive surprises generate as much subsequent volatility as large negative
ones.

## 3.6 Conditional non-normality: the tails are not just volatility

A natural question is whether the fat tails in §3.3 are *only* the result of volatility clustering:
calm periods and turbulent periods, each normal, mixed together. If they were, then dividing each
day's return by that day's estimated volatility would leave something normal. It does not. The
standardised residuals from the GJR-GARCH model still have excess kurtosis of **2.7** daily and **1.0**
weekly, and Jarque–Bera rejects at p<0.001 (Table 2.1, residual rows).

Figure 2.5 shows the same thing graphically. Against a normal distribution the residuals bend away in
both tails; against the Student-t distribution the model estimated (**ν ≈ 5.4** degrees of freedom) they
sit almost on the line. The model has done its job on volatility: no clustering remains in the squared
residuals. Even so, **volatility clustering explains part of the fat tails, not all of them**, and this
is why fat-tailed errors fit the data far better than normal ones in Table 2.4.

Monthly residuals pass the normality test (p = 0.11), so we mark that cell *Not supported*. Because the
monthly model is degenerate (§3.4), these residuals are close to the raw monthly returns rescaled, and
the cell says more about the sample size than about the distribution.

## 3.7 What this means for the portfolio analysis

Three implications carry into sections 4–6.

1. **Volatility-based risk measures understate tail risk.** With conditional fat tails, a portfolio's
   volatility tells the committee less about its worst days than a normal model implies. That is why
   section 5 reports drawdown-based measures (maximum drawdown, Sterling, Calmar) alongside Sharpe.
2. **Volatility regimes are persistent but do change.** A six-month half-life means a trailing one-year
   covariance estimate always partly reflects the previous regime. That favours the walk-forward refit
   in our design, and it limits how much any estimate-dependent strategy can be expected to gain.
3. **Returns are close to unpredictable in direction.** The only serial correlation is a small one-day
   timing effect. Nothing in this section suggests that expected returns can be estimated precisely from
   history. This is the standard argument for strategies that rely on risk estimates only (GMV, IV, ERC)
   over those that also rely on estimated means (MV, MSR), and section 5 tests it directly.

*Limitation:* these are the properties of **one share**. The six assets in the universe differ widely —
`GOVT` and `GC=F` almost certainly behave differently from a semiconductor equity — and we do not
generalise the absence of skewness or leverage beyond `TSM`.
