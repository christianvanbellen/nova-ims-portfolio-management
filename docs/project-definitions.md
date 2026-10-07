# Project definitions

**Last updated:** 2026-10-07 · **Source of truth for the brief:** `project-description.md`

What we analyse and under which conventions. The plan and the notebooks assume this page. If something
changes, change it here first and note it in §8. §9 keeps what earlier work taught us, so that a change
of universe does not mean learning it again.

---

## 1. Investable universe

Twenty-five assets in five sector groups of five, all **US-listed and quoted in USD**, so the pipeline
needs no currency conversion. Strategies allocate **only** to these.

| Sector | Tickers | Instrument |
| --- | --- | --- |
| Technology | `AAPL`, `MSFT`, `ORCL`, `AMZN`, `INTC` | Common stock |
| Healthcare | `JNJ`, `PFE`, `MRK`, `UNH`, `ABT` | Common stock |
| Financials | `JPM`, `BAC`, `WFC`, `GS`, `AXP` | Common stock |
| Consumer staples | `PG`, `KO`, `PEP`, `WMT`, `CL` | Common stock |
| Real assets & defensive | `GLD` (gold), `SLV` (silver), `TLT` (long Treasuries), `VNQ` (real estate), `XOM` (energy) | ETFs, plus `XOM` as a common stock |

The order above, sector by sector, is the fixed asset order for every table and figure. Full names and
asset classes are in Table 1.1 and in `src/config.py`.

**The sector groups are the group's own**, not a GICS classification. `AMZN` is in *Technology* although
GICS classifies it as consumer discretionary. `XOM`, a common stock, sits with the four ETFs as the
energy exposure.

**Stylised-facts share** (the brief asks for one): **`JPM`**. A large bank, so the leverage effect and
crisis behaviour the stylised facts test for have room to show.

**Proxies.** None. Every asset is a directly investable listed security. `GLD` and `SLV` are physically
backed trusts, so they hold the metal and carry no futures roll. The `proxy_for` field in
`src/config.py` and the proxy check in notebook 01 remain, in case a later universe needs them.

---

## 2. Benchmark — S&P 500

Held **outside** the universe. No strategy may allocate to it.

| Ticker | What it is | Use |
| --- | --- | --- |
| `^GSPC` | S&P 500 price index, **non-investable** | Quoted when describing "the market" |
| `SPY` | SPDR S&P 500 ETF, **investable tracker** | Every performance comparison; also defines the NYSE calendar |

Use `SPY` in performance tables. `^GSPC` excludes dividends and would understate the benchmark by about
2 points a year (Table 1.3).

The brief's *own* benchmark for the 100-experiment comparison is the **equally weighted portfolio** of
each experiment's assets. The S&P 500 is the external reference. Report both, because they answer
different questions.

---

## 3. Data availability (Yahoo Finance, measured 2026-10-07)

Every asset clears the 15-year minimum, most by decades. The latest-listed is `SLV` (first observation
2006-04-28, 20.4 years). The others reach back to between 1962 and 2004. Table 1.1 gives the full list.

| Measure | Range across the 25 |
| --- | --- |
| History | 20.4 years (`SLV`) to 64.8 years (`JNJ`, `MRK`, `PG`, `KO`, `XOM`) |
| Median daily dollar volume, panel | $220m (`CL`) to $7.9bn (`AAPL`) |
| Missing sessions in the panel | 0 for every asset |
| Zero-return days | 0.08% (`GS`) to 1.91% (`SLV`) |

| Ticker | First obs. | Years | Use |
| --- | --- | --- | --- |
| `^GSPC` | 1927-12-30 | 98.8 | Market description |
| `SPY` | 1993-01-29 | 33.7 | Benchmark and calendar |
| `^IRX` | 1960-01-04 | 66.7 | Risk-free |

Consequences for the report: none of the history caveats a 15-year brief usually forces. The span
**and** the all-asset intersection are both the full 15.0 years. Liquidity is deep everywhere, so no
asset needs a staleness caveat.

---

## 4. Panel and calendar

| Convention | Decision |
| --- | --- |
| Panel start | `2011-10-01`. 15 years of span, per the brief. Kept on 2026-10-07 although the universe would allow a start in May 2006 (see §8) |
| Panel end | Latest session available at extraction |
| Staggered entry | Assets enter on their own first observation. Pre-entry cells stay `NaN`, never zero- or back-filled. Not exercised by this universe, which is complete from the first session |
| Full-panel date | First date every asset has data, derived in code (`Panel.full_panel_start`). Currently the panel's first session |
| Sampler rule | A random window is drawn only from dates where every asset **in that drawn subset** has data |
| Trading calendar | NYSE sessions, defined as the dates `SPY` trades. All series reindexed to it; off-calendar observations dropped and counted (currently none) |
| Interior gaps | Forward-fill up to 3 sessions. Anything longer is reported, not patched (currently none) |
| Extreme moves | Daily log returns beyond ±15% are listed (Table A1.1) and checked against the corporate-action log. Kept in the data unless one is shown to be an artefact |

---

## 5. Returns and prices

| Item | Decision |
| --- | --- |
| Source | Yahoo Finance via `yfinance`, downloaded live each run; nothing written to disk |
| Prices | `auto_adjust=True`: adjusted for splits, spin-offs and cash distributions. Distributions are material for every stock except `AMZN` and dominate `TLT`, `VNQ` and `XOM`. The effect is quantified in **Table 1.3** against the price-only series. Dividends are reinvested gross of tax |
| Spin-offs | Yahoo books a spin-off as a fractional split ratio, so the parent's series continues as if the spun-off shares were sold on the ex-date and reinvested. Three in the panel: `ABT` 2013, `PFE` 2020, `MRK` 2021 (Table A1.2) |
| Log returns | `ln(P_t) − ln(P_{t−1})`, used for all stylised-facts analysis |
| Simple returns | `P_t/P_{t−1} − 1`, used for all portfolio compounding and performance stats |
| Weekly / monthly | Sum of daily log returns. Weeks end Friday, months on the last trading day |
| Currency | All USD, no conversion, and no foreign listing in the universe. Foreign-currency exposure exists only indirectly, through the companies' overseas earnings |
| Risk-free | `^IRX`, 13-week T-bill yield, annualised percent. ÷100 for decimal, ÷252 for daily |
| Annualisation | 252 days. Return ×252, volatility ×√252 |

---

## 6. Transaction costs (proposed)

One-way, in basis points of traded notional, applied to turnover at each rebalance. Each asset's cost
is stored on its `UNIVERSE` entry in `src/config.py`, and `COSTS_BP` is derived from those entries.

| Assets | bp | Why |
| --- | --- | --- |
| `GLD`, `TLT`, `VNQ` | 2 | Among the most traded ETFs, with spreads of about a cent |
| The 20 common stocks, `XOM` included | 3 | US large caps with deep books. Spread plus a small impact allowance |
| `SLV` | 3 | Liquid, but a lower share price makes the one-cent spread a larger fraction |

Every asset in this universe is cheap to trade, and the range of costs is narrow (2–3 bp). Costs will
therefore separate strategies **by turnover** rather than by which assets they trade. The brief requires
results **before and after** costs, plus a re-run at **2×** these figures to test whether the ranking
holds.

---

## 7. Fixed parameters

| Parameter | Value |
| --- | --- |
| Random seed | `20261001` |
| Experiments | 100 |
| Window | 3 contiguous years |
| Split | 2 years estimation, 3rd year out-of-sample |
| First estimate | Every return in the window up to the formation date (2 years less the lag) |
| Estimation update | Trailing 1 year, rolling |
| Rebalancing | Quarterly, every 63 sessions. Opening trade at the close of the last estimation session |
| Execution lag | 1 session. Weights formed at close *t*, traded at close *t*+1, earning from *t*+2 |
| Initial portfolio | Bought out of cash. Its cost is charged; its 100% turnover is excluded from reported turnover |
| Optimisation failure | Logged; hold the drifted weights (equal weight if none yet); the run is never dropped |
| Asset subset | **10 of 25, sector-stratified**: 2 drawn uniformly from each of the 5 sectors, so every portfolio spans every sector (10⁵ possible subsets). `SUBSET_SIZE` and `SUBSET_GROUPS` in `src/config.py`; groups `None` gives an unstratified draw |
| Constraints | Long-only, fully invested, no leverage |
| Expected returns | Sample mean of daily simple returns over the estimation window, ×252 |
| Covariance | Sample covariance, ×252. Ledoit–Wolf (constant correlation) is a switch for robustness only. To be re-checked in workstream D (§9) |
| MV risk aversion | λ = 3, on annual decimal returns. To be re-checked in workstream D (§9) |
| MSR risk-free | Mean `^IRX` over the estimation window, annualised. No asset above it → logged failure |
| Trading days/year | 252 |

The seed is fixed now and is not re-rolled after seeing results.

---

## 8. Changelog

| Date | Change |
| --- | --- |
| 2026-10-07 | **Universe rebuilt on the professor's advice to use more assets.** The universe is now 25 assets in five sector groups (§1). It replaces the previous universe entirely. The lessons that universe taught are kept in §9, and git history holds the rest. Stylised-facts share: `JPM`. Panel start kept at 2011-10-01: all 25 assets have data from 2006-04-28, so the panel could include 2008, but the group kept the 15-year panel. |
| 2026-10-07 | **Workstream A complete on the new universe.** `notebooks/01_investment_universe.ipynb` runs clean top-to-bottom, extraction date 2026-10-07; report §2 redrafted. Universe entries now carry their own sector and cost; asset order, sector groups, colours and `COSTS_BP` are derived from them. Asset colour = sector colour (palette slots 1–5), because 25 assets exceed the palette; Figure 1.2 is now small multiples. New: Table A1.1 (extreme-move screen) and Table A1.2 (corporate-action log, which classifies spin-offs). Table 1.1 reports median **dollar** volume over the panel. |
| 2026-10-07 | **Workstream B complete on `JPM`.** `notebooks/02_stylised_facts.ipynb` runs clean top-to-bottom; report §3 redrafted. Three rule changes, each made because a test was invalid for this data, not because of the verdict it gave (two of the three make the verdict *weaker*): (1) **fact 3** is tested by moving-block bootstrap on moment *and* quantile skewness. The D'Agostino test's standard error was 6.5× too small under JPM's fat tails, and would have read weekly and monthly as *Supported*; they are now *Partial*. (2) **"Clustering identified"** (facts 6 and the failure log) now means at least one of α, γ significant. The old check only caught the α≈0/β≈1 collapse and missed JPM's monthly β≈0 one. (3) Anderson–Darling computed on the log scale (statsmodels overflowed to ∞). Added: half-life in Table 2.4; robustness tables A2.3 (without the COVID window) and A2.4 (leverage term under AR(1) mean, sample halves, without the window), so every number the report quotes is now printed by the notebook. |
| 2026-10-07 | **Workstream C complete on the new universe.** The asset subset is now **10 of 25, two per sector** (§7), decided by the group before any strategy was run. The brief requires random subsets, and four of 25 would have left most portfolios as four single stocks with no defensive asset. A full-universe reference run was considered and deferred. The sampler now draws subsets directly instead of enumerating them, and drops the old universe-specific column. `notebooks/03_backtest_engine.ipynb` runs clean, with all 10 unit tests passing, both deliberate-leak tests raising `LookAheadError`, and tests 7–8 made universe-agnostic. New diagnostic: covariance conditioning at the subset size (median condition number 18; 24 of 100 experiments hold a financials pair above 0.85). |
| 2026-10-07 | **Workstreams D–E to be re-run** against the new universe, in order. Their notebooks still run on the previous configuration's assumptions in places (e.g. subset size, the shrinkage and λ decisions) and their results are not current. |

---

## 9. Lessons carried forward

What earlier work established. Each lesson is written so that it applies to any universe. Each says
where the check lives and what it shows for the current universe.

### Data (workstream A)

| Lesson | Kept as | Current universe |
| --- | --- | --- |
| A thinly traded instrument produces **stale prices**, which bias measured volatility down and correlations toward zero. Optimisers then over-weight it (IV directly, GMV and ERC through the covariance) | `% zero-return days` in Table 1.2; dollar liquidity in Table 1.1 | Clean: under 2% zero-return days everywhere, and at least $220m traded a day |
| An asset that trades **off the NYSE calendar** (e.g. every day) must be reindexed. Dropping weekend prints understates its risk; aggregating them fattens Monday tails | Off-calendar count in A3; disclosed in report §2 | None |
| **Short histories** can make the all-asset intersection shorter than the panel. Never pad. Use staggered entry and a subset-aware sampler, and state both spans | Staggered entry, sampler rule (§4), span/intersection check in notebook 01 | Not binding: intersection = panel = 15.0 years |
| **Futures and spot series are proxies**, not holdings. Label them, and name the investable counterpart | `proxy_for` on each universe entry; done-when check | None |
| **Foreign listings (ADRs)** carry FX inside the return and foreign withholding tax on dividends, which a gross adjustment overstates | Currency row in §5 | None. All US domestic listings |
| **Dividend adjustment is material for income assets.** An unadjusted bond or REIT fund can show a loss on price alone | Table 1.3 | `TLT` is negative on price alone. Distributions are worth about 4 points a year for the highest-yielding names |
| A price index (`^GSPC`) is not investable and excludes dividends. Benchmark on the tracker (`SPY`) | §2; Table 1.3 row pair | 2.0 points a year gap |
| **One extreme performer** can make "performance" mean "how much of it you held". Random subsets and windows dilute it | Growth summary under Figure 1.2 | Best asset ends about 5× the median one, so no single asset dominates |
| *New with this universe:* **spin-offs** arrive as fractional split ratios, and an unadjusted one would look like a crash | Tables A1.1 and A1.2, with asserted cross-checks | Three spin-offs, all adjusted cleanly |
| *New with this universe:* **ex-post selection.** A list of today's large caps is tilted toward winners before any strategy runs | Growth commentary under Figure 1.2; report §2.5; limitations (F6) | 7 of 25 beat `SPY`; the top three are among today's largest companies |

### Stylised facts (workstream B)

- Weekly and monthly series use **complete periods only**; drop the first period and any trailing stub.
- **Any test whose null assumes iid or normal data is suspect on returns.** Plain Ljung–Box over-rejects
  no-serial-correlation under volatility clustering, so the verdict uses a heteroskedasticity-robust
  portmanteau. *New with this universe:* the same is true of the D'Agostino skewness test under fat
  tails, so skewness is tested by moving-block bootstrap. A test of *normality* (JB, kurtosis) is
  fine, because there normality is the null being tested.
- **Quantile skewness alongside moment skewness.** Moment skewness at daily frequency is a statement
  about a handful of days; the quantile measure says whether the body of the distribution is skewed.
- **A GARCH fit can collapse in two ways**: α at zero with β at one, or β at zero with α insignificant.
  Judge "clustering identified" by whether any ARCH-type term is significant, and treat p-values of
  parameters on a boundary as uninterpretable.
- **Check every headline statistic without the crisis window** (`stylised.STRESS_WINDOW`). For `JPM`,
  March 2020 carries half the daily kurtosis and all the daily serial correlation.
- **Every number the report quotes must be printed by the notebook**, robustness checks included.
- GARCH models are fitted on **percent** log returns with a constant mean. Decimal returns cause
  optimiser scaling problems.
- *For the backtest:* the daily volatility half-life is about a month, shorter than the quarterly
  rebalancing interval, and falls raise volatility about 2.7× as much as rises.

### Backtest engine (workstream C)

- The sampled experiments are reproducible under the seed **and** the extraction date, because the set
  of eligible window starts grows as the panel grows.
- The look-ahead guard must **raise**, and a deliberate-leak test must prove it does.
- **The subset size is a design decision, not a detail.** It sets how much each portfolio can
  diversify, how many observations per asset the estimates get (252 / k), and how hard the optimiser's
  problem is. Fix it before any strategy runs. A rule that suited a small universe (4 of 6) does not
  carry over: at 4 of 25 most portfolios would be four stocks.
- **Stratify when the universe has structure.** A uniform draw lets the sector mix vary between
  experiments, which confounds strategy differences with composition. Drawing a fixed number per
  sector keeps the mix constant and varies the names.
- **Never enumerate subsets.** Draw them. C(25, 10) is 3.3 million.
- **Check the estimation problem the sampler creates** (condition number, most-correlated pair) in C,
  before the optimisers meet it in D.

### Strategies (workstream D), to re-check on the new universe

- **Shrinkage can erase the contrast the brief asks for.** On a small, weakly correlated universe,
  Ledoit–Wolf towards constant correlation (median intensity about 0.5) collapsed ERC and MDP onto IV.
  The sample covariance was kept. With sector blocks at 0.75 correlation this may now behave
  differently, so re-run the D11 check before carrying the decision over.
- **λ = 3 can make MV coincide with MSR** when both land on a single-asset corner. The coincidences are
  reported, not tuned away. Re-run D12.
- **MSR is undefined** when no asset's expected return exceeds the risk-free rate. Log it and hold the
  previous weights.
- The exact QP solver enumerates supports, at a cost of 2ⁿ − 1 for an n-asset subset. It is measured
  at about 20 ms per solve at 10 assets (about 9 s per strategy over 400 rebalances): fine. It is
  infeasible at 25, so a full-universe run would need a different solver.
- *New, from Figure 1.1:* subsets can now draw **near-collinear pairs** (two banks at 0.8–0.85
  correlation). Expect unstable MV/MSR weights between them; check turnover.

### Experiments and performance (workstream E)

- Fix every metric convention **before** looking at results: geometric annual return; Sharpe and
  Sortino on daily excess returns over `^IRX`; drawdown measured from wealth 1 at the start of the
  evaluation year; Sterling = annual return / (|max drawdown| + 10%); medians across experiments; win
  rate = share of experiments with net Sharpe above EW's in the same experiment.
- Pick the illustrative experiment by a stated rule (e.g. the recommended strategy's median net
  Sharpe), never by eye.
