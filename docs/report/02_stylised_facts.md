# 3. Stylised facts

*Draft of report section 3. Target ~3 pages alongside Tables 2.1–2.5 and Figures 2.1–2.5, with Tables
A2.1–A2.4 and Figures A2.1–A2.4 in the appendix. Every number is produced by
[`notebooks/02_stylised_facts.ipynb`](../../notebooks/02_stylised_facts.ipynb), extraction of 7 October
2026, and will be refreshed in the final re-run (plan G2).*

---

## 3.1 What we tested, and the answer

The brief asks us to take one share and test six features commonly said to describe asset returns,
and to **assess** each one rather than assume it. We use **JPMorgan Chase (`JPM`)** over the full
fifteen-year panel: **3,773 daily, 782 weekly and 179 monthly** log returns, from October 2011 to
early October 2026 (monthly returns run to September, the last complete month). A large bank is a
demanding test case. Its share price carries both leverage and credit risk, and the sample includes
the 2020 crash and the 2023 regional-bank failures.

Each verdict follows a rule fixed in advance and applied mechanically (rules in the appendix), at the
5% significance level. Table 2.5 is the result.

**Table 2.5 — Stylised facts summary, `JPM`.** 2011-10 to 2026-10; n = 3,773 / 782 / 179.

| Stylised fact | Daily | Weekly | Monthly | Evidence |
| --- | --- | --- | --- | --- |
| 1. Little or no serial correlation in raw returns | Partial | Supported | Supported | Table 2.3, Figure 2.3a |
| 2. Non-normal distribution, fat tails | Supported | Supported | Supported | Tables 2.1–2.2, Figure 2.2 |
| 3. Asymmetry / negative skewness | Partial | Partial | Partial | Table 2.1, Figure 2.2 |
| 4. Volatility clustering | Supported | Supported | Not supported | Table 2.3, Figures 2.1, 2.3b–c |
| 5. Leverage effect | Supported | Supported | Partial | Table 2.4, Figure 2.4 |
| 6. Conditional non-normality | Supported | Supported | Partial | Table 2.1, Figure 2.5 |

The pattern is as informative as any single cell. **At daily and weekly frequency, the classic picture
of an equity holds almost in full.** Returns are fat-tailed, volatility clusters, bad news raises
volatility more than good news, and the tails survive a volatility model. **Negative skewness is the
exception.** It is present in every series, but it never clears both of our robust tests. **Almost
everything weakens with aggregation.** By monthly frequency, volatility clustering is gone, and the
facts that depend on it are only partially supported.

Two checks run through the section, and both change what the table can claim. First, every test is
valid under fat tails and clustering. Second, every headline statistic is recomputed without the
COVID crash weeks (Appendix Table A2.3), because one quarter of extreme returns can carry a
fifteen-year result.

## 3.2 Serial correlation: absent, except in a crash

At weekly and monthly frequency there is no serial correlation in returns: no robust test rejects at
any lag (Table 2.3). At daily frequency, the robust test rejects (p = 0.014), driven by a **negative
lag-1 autocorrelation of −0.08** (Figure 2.3a).

This result needed care. The standard test (Ljung–Box) assumes constant volatility. When volatility
clusters, as it does here, the test finds autocorrelation that is not there. In plain form it rejects
at p < 0.001. We therefore use a version robust to changing volatility, which rejects far less
emphatically. Even so, the effect is **economically negligible**: it explains under 1% of next-day
return variance, far less than the cost of trading on it. Hence *Partial*.

The source is the crash, not the share. **Without mid-February to mid-May 2020, the daily lag-1
autocorrelation is −0.02 and the robust test no longer rejects** (p = 0.90). March 2020 whipsawed: a
−15% day, then +17%, then −16%. Those reversals are the whole of the daily effect.

## 3.3 The distribution: very fat-tailed, mildly skewed

**Fat tails are the strongest result in the section** (Table 2.1). Daily excess kurtosis is **11.1**,
where a normal distribution has 0, and all three normality tests reject decisively. In practical terms
(Table 2.2), `JPM` has more quiet days *and* more extreme days than a normal distribution with the same
volatility: the 5% and 95% quantiles sit inside the normal's, while the 1% and 99% sit outside them.
Moves beyond five standard deviations occurred **12 times** in fifteen years. A normal distribution
expects one such day in roughly seven thousand years.

Fat tails **fade with aggregation**. Excess kurtosis falls to 4.1 weekly and 1.7 monthly, but every
normality test still rejects at every frequency. The crash matters here too: without it, daily excess
kurtosis halves to 5.2. That is still strongly fat-tailed, but the 2020 weeks alone account for half
the headline figure.

**Skewness needed a different test, and the result is *Partial* throughout.** The textbook skewness
test assumes normal data. On data this fat-tailed, its standard error is too small by a factor of
**6.5** at daily frequency, so it would "find" skew in a handful of extreme days. We therefore test two
measures by bootstrap, resampling the actual data with its fat tails and clustering intact:

- **Moment skewness**, the usual measure, is negative at every frequency (−0.08 daily, −0.34 weekly,
  −0.66 monthly). It is significant only monthly (p = 0.03).
- **Quantile skewness** compares how far the 5th and 95th percentiles sit from the median, so a few
  extreme days cannot drive it. It is negative and significant at daily and weekly frequency
  (p = 0.035 and 0.004), but not monthly.

Each frequency passes one test but not both. The lower part of the distribution does reach further
than the upper. At monthly frequency, the 1% quantile sits outside the normal's while the 99% sits
inside it (Table 2.2). But the asymmetry is modest, and the measure most quoted in the literature
cannot establish it at the horizons where the data are richest. Had we used the textbook test, weekly
and monthly would have read *Supported*. We report the weaker answer because it is the one the data
support.

## 3.4 Volatility clustering: strong, fast, and short-horizon

Large moves cluster together. Figure 2.1 shows calm stretches (2013–14, 2017) alternating with
turbulent ones: the end of the European debt crisis, the 2012 trading loss, 2015–16, March 2020, the
2022 rate shock, the 2023 regional-bank failures and the April 2025 tariff shock. Figure 2.3b–c
measures the clustering: the autocorrelation of absolute and squared returns is positive and decays
slowly. Every test rejects at daily and weekly frequency (Table 2.3).

GARCH models put a number on it (Table 2.4). Daily persistence is **0.95–0.98** across specifications,
a **half-life of roughly one month** (about 22 trading days in the GJR model): after a shock,
volatility falls halfway back to normal within a month. Rolling three-month volatility ranged from
**11%** (late 2016) to **92%** (spring 2020) annualised, against a full-sample average of **27%**.

At monthly frequency, **clustering is not supported**: none of the nine tests rejects. GARCH models
fitted to monthly returns find no significant clustering term and put the persistence parameter on its
zero bound. With a one-month half-life, volatility shocks have largely died out within the month that
a monthly return sums over, so there is little left to cluster.

## 3.5 Leverage effect: strong at daily frequency

The leverage effect says that falls raise future volatility more than rises of the same size. We test
it with two asymmetric models, GJR-GARCH and EGARCH. At daily frequency, **both estimate the
asymmetry term with the expected sign, and both are significant at p < 0.001** (Table 2.4). In the
GJR model nearly all the reaction to news is to *bad* news: the asymmetry term is 0.12, against 0.02
for the symmetric term. The news impact curve (Figure 2.4) shows the scale. After a −4 standard
deviation day, next-day variance is about **2.7 times** what it is after a +4 standard deviation day
(2.2 times in EGARCH).

The daily result is robust (Appendix Table A2.4a). It holds with an autoregressive mean, in each half
of the sample separately, and without the 2020 crash, with the asymmetry term between 0.10 and 0.13
and significant every time. For a bank this is the expected result. A falling share price raises
leverage and credit concern together, and both feed volatility.

The **weekly** result is significant on the full sample, so the rule gives *Supported*. It is less
robust, though. It comes from the second half of the sample (p = 0.83 in the first half), and without
the crash it is only marginal (p = 0.054). **Monthly** evidence is *Partial*: EGARCH finds the
asymmetry and GJR does not, in a model that identifies no clustering at all.

## 3.6 Conditional non-normality: the tails are not just volatility

A natural question is whether the fat tails in §3.3 are *only* the result of volatility clustering:
calm periods and turbulent periods, each normal, mixed together. If they were, dividing each day's
return by that day's estimated volatility would leave something normal. It does not. The standardised
residuals from the GJR-GARCH model still have excess kurtosis of **4.2** daily and **2.1** weekly, and
Jarque–Bera rejects at p < 0.001 (Table 2.1, residual rows).

Figure 2.5 shows the same thing graphically. Against a normal distribution the residuals bend away in
both tails. Against the Student-t distribution the model estimated (**ν ≈ 5** degrees of freedom), they
sit close to the line. The model has done its job on volatility: no clustering remains in the squared
residuals. So **volatility clustering explains part of the fat tails, but not all of them**. That is
why fat-tailed errors fit the data far better than normal ones in Table 2.4.

Monthly residuals still reject normality, narrowly (p = 0.018). But the monthly model identifies no
clustering, so these "residuals" are close to the raw monthly returns rescaled. The cell is *Partial*:
it says the monthly distribution is non-normal, not that the conditional distribution is.

## 3.7 What this means for the portfolio analysis

Four implications carry into sections 4–6.

1. **Volatility-based risk measures understate tail risk.** With conditional fat tails, a portfolio's
   volatility tells the committee less about its worst days than a normal model implies. That is why
   section 5 reports drawdown-based measures (maximum drawdown, Sterling) alongside Sharpe.
2. **Volatility moves faster than our estimates.** A one-month half-life means volatility regimes change
   within a single quarterly rebalancing interval. A trailing one-year covariance estimate averages
   over several of them. Risk-based strategies (GMV, IV, ERC) therefore respond to a volatility shock
   with a lag of months, and they cut risk after the event rather than before it.
3. **Falls and volatility arrive together.** Because of the leverage effect, the worst days are also
   the ones that raise risk. A strategy that sizes positions by trailing volatility is therefore
   fully invested going into a sell-off and de-risks only after it.
4. **Returns are close to unpredictable in direction.** The only serial correlation is a crash-period
   reversal. Nothing in this section suggests that expected returns can be estimated precisely from
   history. That is the standard argument for strategies that use risk estimates only (GMV, IV, ERC)
   over those that also use estimated means (MV, MSR), and section 5 tests it directly.

*Limitations.* These are the properties of **one share**. The universe holds gold, silver, long
Treasuries and real estate as well as equities, and those almost certainly behave differently. We do not
generalise the leverage effect or the skewness result beyond `JPM`. And one quarter, March 2020, carries
half the measured daily kurtosis and all of the daily serial correlation. Any evaluation year that
contains it will be dominated by it.
