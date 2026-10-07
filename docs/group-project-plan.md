# Group project — detailed plan

**Deadline:** 30 October 2026, via Moodle · **Weight:** 14/20
**Inputs:** `project-description.md` (the brief) · [`project-definitions.md`](project-definitions.md) (universe, benchmark, conventions) · [`group-work-division.md`](group-work-division.md) (the group's draft split, reconciled against this plan)

Granular task list for the group project. Every task names its **direct output** and the **format that
output takes**, so nothing is produced twice or in a shape the report cannot use.

---

## 1. Output conventions

Agree these once; they apply to every table and figure anyone produces.

### Numbers

| Quantity | Format | Example |
| --- | --- | --- |
| Returns, volatility, drawdown | Percent, 2 dp, `%` in the **column header**, not the cell | `12.43` |
| Sharpe, Sortino, Sterling, Calmar | 2 dp, unitless | `0.87` |
| Weights | Percent, 1 dp | `23.4` |
| Turnover | Percent per year, 1 dp | `84.2` |
| Skewness, kurtosis | 2 dp (kurtosis as **excess**, state it) | `-0.41` |
| p-values | 3 dp; below that write `<0.001` | `0.027` |
| Counts | Integer, thousands separator | `3,672` |
| Not applicable / insufficient data | Em dash `—`, never `0`, never blank | `—` |

Negative numbers take a minus sign, not parentheses. Never report more precision than the estimate
supports — no 4-decimal Sharpe ratios.

### Tables

- Caption **above**: `Table 4.2 — Net performance by strategy. 100 experiments, median across runs.`
- Numbered by report section: `Table <section>.<n>`.
- Fixed row order for strategies everywhere: **EW, GMV, MV, MSR, IV, ERC, MDP, MDC**. EW first, because
  it is the brief's benchmark.
- Fixed column order for assets everywhere: sector by sector, in the order of `UNIVERSE` in
  `src/config.py` (definitions §1), then benchmark. Sector order: Technology, Healthcare, Financials,
  Consumer staples, Real assets & defensive.
- Fixed frequency order everywhere: **daily → weekly → monthly**.
- Every table states its period and `n` in the caption or a footnote.

### Figures

- Caption **below**: `Figure 2.1 — JPM daily log returns against a fitted normal. 2011-10 to 2026-10, n = 3,773.`
- One y-axis per chart. **Never two scales on one chart** — use two charts or index both to 100.
- Axes labelled with units. Date axes in `YYYY` or `YYYY-MM`.
- Cumulative wealth on a **log y-axis**, as growth of $1.
- One fixed colour per strategy and per **sector**, used identically in every figure in the report. An
  asset takes its sector's colour, because 25 assets exceed the palette; where assets of one sector
  share a chart, identity comes from direct labels or small multiples, never colour alone. The
  benchmark (EW, and S&P 500) is drawn in neutral grey, dashed, so it reads as a reference line rather
  than a competitor.
- More than ~4 lines on one chart is unreadable: show the recommended strategy plus benchmarks in the
  main report, and put the full set in the appendix as small multiples.
- Correlation heatmaps: diverging scale fixed to −1…+1 with a neutral midpoint at 0, values printed in
  the cells.

### Where output lives

| Destination | What goes there |
| --- | --- |
| **Main report** | Written for an investment committee. Conclusions, the headline table per section, at most 2–3 figures per section. No code, no raw output. |
| **Appendix** | Full statistics, per-asset breakdowns, all diagnostic plots, optimisation failure log, parameter tables. |
| **Reproducibility appendix** | Data source and extraction date, random seed, package versions, notebook run order, data-retrieval instructions. |
| **Notebooks** | Everything that produces the above. Submitted as supporting files. |

### Notebook pipeline

Each notebook ends by printing the tables and figures the report consumes. No data files are written —
data is pulled from Yahoo Finance on every run (see definitions §5).

| Notebook | Produces |
| --- | --- |
| `01_investment_universe.ipynb` | Universe, panel, return frames, data-quality tables |
| `02_stylised_facts.ipynb` | All of report section 2 |
| `03_backtest_engine.ipynb` | Sampler, walk-forward loop, cost model — no results, just the machinery |
| `04_strategies.ipynb` | The eight weight functions and their unit tests |
| `05_experiments.ipynb` | The 100 runs; the raw results frame |
| `06_performance.ipynb` | All of report sections 4 and 5 |
| `07_robustness.ipynb` | Cost sensitivity, subset/period dependence |

---

## 2. Workstream A — Data and universe

Brief: *A.1, first half.* Report section: **Data**.

| # | Task | Direct output | Format |
| --- | --- | --- | --- |
| A1 | Build notebook 01 on the universe and S&P 500 benchmark from the definitions file | Working `UNIVERSE` / `BENCHMARKS` dicts | Code. Single source of truth — downstream imports it |
| A2 | Download full history for the universe + `^GSPC`, `SPY`, `^IRX`; record extraction date | Raw price frame | In memory. Extraction date printed |
| A3 | Build the NYSE calendar from `SPY`; reindex every series to it; drop and count any off-calendar observations | Aligned adjusted-close panel | Wide frame, dates × tickers |
| A4 | Audit history and liquidity per asset | **Table 1.1 — Data availability** | Cols: ticker, name, sector, class, instrument, first obs., years, obs./yr, median $ volume over the panel, meets 15y |
| A5 | Count missing and stale observations per asset; screen for extreme moves | **Table 1.2 — Data quality** + **Table A1.1 — Extreme daily moves** | Cols: ticker, missing obs., longest gap (sessions), % zero-return days, days with \|r\| > 15%, treatment applied. A1.1 lists every flagged session and how many assets moved that day |
| A5b | Quantify the adjustment: adjusted close against price-only close, every asset plus `SPY` and `^GSPC`; log and classify corporate actions | **Table 1.3 — Dividend and adjustment effect** + **Table A1.2 — Corporate-action log** | Cols: ticker, instrument, from, total return %/yr, price return %/yr, distributions pp/yr, distribution events, split / spin-off events. A1.2: date, ticker, ratio, split or spin-off, return that day |
| A6 | Build daily, weekly, monthly log and simple return frames | 6 return frames | Daily/weekly/monthly × log/simple |
| A7 | Correlation matrix of daily returns, full-panel period | **Figure 1.1 — Asset correlation heatmap** | Diverging scale −1…+1, values in cells, fixed asset order, sector blocks separated |
| A8 | Normalised price chart, every asset plus S&P 500 | **Figure 1.2 — Cumulative growth of $1** | Small multiples, one panel per asset, one row per sector; shared log y-axis; benchmark dashed grey in every panel |
| A9 | Write the *Data* section prose: source, extraction date, adjustment, dividends, corporate actions (spin-offs included), currencies, calendars, proxy labels if any, the 15-year span and the all-asset intersection, hindsight in the asset selection | Draft section | ~1.5 pages, main report |

**Done when:** the panel has no silent fills, Table 1.1 and 1.2 reconcile, every extreme move is checked
against the corporate-action log, and any proxy in the universe is labelled in the prose.

---

## 3. Workstream B — Stylised facts (`JPM`)

Brief: *A.1, second half.* Report section: **Stylised facts**. Every test is run at **daily, weekly and
monthly** frequency, and the brief is explicit: assess whether the evidence supports each feature — do
not assume it holds.

| # | Task | Direct output | Format |
| --- | --- | --- | --- |
| B1 | Descriptive statistics for `JPM` log returns, three frequencies | **Table 2.1 — Descriptive statistics** | Rows: daily/weekly/monthly. Cols: n, mean %, sd %, min %, max %, skew and quantile skew (bootstrap p), excess kurtosis, Jarque–Bera stat, p |
| B2 | Return series plot, three frequencies | **Figure 2.1 — Log returns over time** | 3 stacked panels, shared x-axis; volatility clusters visible |
| B3 | Histogram vs fitted normal + Q–Q plot, three frequencies | **Figure 2.2 — Return distribution** | 2 panels per frequency; main report shows daily, appendix the rest |
| B4 | Normality tests: Jarque–Bera, Shapiro–Wilk, Anderson–Darling | Folded into Table 2.1 | Statistic and p-value |
| B5 | Tail analysis: empirical vs normal quantiles at 1%, 5%, 95%, 99% | **Table 2.2 — Tail quantiles** | Cols: quantile, empirical %, normal-implied %, ratio |
| B6 | ACF of **raw** returns, lags 1–40, with 95% band; Ljung–Box at lags 5/10/20 | **Figure 2.3a** + **Table 2.3** | Bar chart with shaded band; table of Q-stat and p per lag |
| B7 | ACF of **absolute** and **squared** returns, same lags | **Figure 2.3b–c** | Same spec — three panels side by side make the contrast the point |
| B8 | ARCH-LM test for conditional heteroskedasticity | Row in Table 2.3 | Statistic, p-value |
| B9 | Fit GARCH(1,1) with normal and Student-t errors | **Table 2.4 — Volatility model** | Cols: parameter, estimate, std. error, p. Both error assumptions side by side |
| B10 | Fit GJR-GARCH / EGARCH; test the asymmetry term | Added to Table 2.4 | The γ term and its p-value is the leverage-effect evidence |
| B10b | Robustness: headline statistics without the crisis window; leverage term with an AR(1) mean, on each half of the sample, without the window; half-life and rolling volatility | **Tables A2.3–A2.4** (appendix) | Every robustness claim in the prose must come from these |
| B11 | News impact curve | **Figure 2.4 — News impact curve** | Shock on x, next-period conditional variance on y; asymmetry visible |
| B12 | Standardised residuals: Q–Q against normal and Student-t, plus JB | **Figure 2.5** + row in Table 2.1 | Tests conditional non-normality — the sixth stylised fact |
| B13 | Verdict table: each of the six stylised facts, the evidence, and whether it holds at each frequency | **Table 2.5 — Stylised facts summary** | Rows: the 6 facts. Cols: daily / weekly / monthly, each `Supported` / `Partial` / `Not supported`, plus the statistic cited |
| B14 | Write the section prose | Draft section | ~3 pages. Table 2.5 is the anchor; it is what the examiner reads first |

**Done when:** Table 2.5 has a verdict in all 18 cells, each backed by a numbered table or figure, and at
least one cell honestly says *Not supported* if that is what the data shows (monthly serial correlation
and monthly normality are the usual candidates).

---

## 4. Workstream C — Backtest engine

Brief: *Methodology — backtesting design.* No results here; this is the machinery everything else runs
on. Build and test it before any strategy is written.

| # | Task | Direct output | Format |
| --- | --- | --- | --- |
| C1 | Experiment sampler: draw 100 (3-year window, 10-asset subset, 2 per sector) pairs under the seed and the availability rule | `experiments` frame | 100 rows. Cols: experiment id, start, end, assets (tuple in the fixed asset order) |
| C2 | Walk-forward loop: 2y estimation → 1y evaluation, trailing 1y refit, quarterly rebalance | Reusable function | Takes (prices, weight function, cost model) → returns daily portfolio returns, weights and turnover |
| C3 | **Look-ahead guard**: weights at date *t* use data strictly up to *t*; trades execute at *t+1* | Assertion inside the loop | Must raise, not warn. One unit test that deliberately leaks and must fail |
| C4 | Weight drift between rebalances | Implemented in C2 | Weights drift with returns; only reset on rebalance dates |
| C5 | Per-asset transaction-cost model from definitions §6 | Cost function | Cost = Σ \|Δw_i\| × bp_i, charged on the rebalance date |
| C6 | Optimisation failure handling: log it, fall back to the previous weights, **never drop the run** | `failures` log | Cols: experiment id, date, strategy, error, fallback used. Appears in the appendix |
| C7 | Turnover accounting | Returned by C2 | Annualised two-way turnover, percent |
| C8 | Unit tests: EW on a known panel reproduces hand-computed wealth; zero-cost run matches no-cost path; weights sum to 1 and stay ≥ 0 | Passing test cell | Keep in notebook 03 — it is evidence of rigour for the examiner |
| C9 | **Table 3.1 — Experiment design** | Summary of the sampler | Cols: parameter, value, rationale. Plus: subset design and number of possible subsets, experiments per asset, subset overlap, window coverage, min/max start date. Appendix: Table A3.1 (inclusion per asset), A3.2 (evaluation years), covariance-conditioning diagnostic |

**Done when:** C8 passes and C3's deliberate-leak test fails as designed.

---

## 5. Workstream D — Strategies

Brief: *A.2 (a)–(f).* Eight portfolios. Each needs a stated objective, constraints and parameters — the
brief specifically asks that MV be distinguishable from GMV and MSR, and IV from ERC.

| # | Strategy | Objective | Parameter to fix **before** running |
| --- | --- | --- | --- |
| D1 | **EW** — equally weighted | wᵢ = 1/N | — (the benchmark) |
| D2 | **GMV** — global minimum variance | min wᵀΣw | — |
| D3 | **MV** — Markowitz mean–variance | max wᵀμ − (λ/2)wᵀΣw | **λ = 3** (state it; this is what makes MV ≠ GMV ≠ MSR) |
| D4 | **MSR** — maximum Sharpe | max (wᵀμ − r_f)/√(wᵀΣw) | Risk-free from `^IRX` |
| D5 | **IV** — inverse volatility | wᵢ ∝ 1/σᵢ | Ignores correlations — this is the contrast with ERC |
| D6 | **ERC** — equal risk contribution | Each asset contributes equal risk | Uses the full Σ |
| D7 | **MDP** — most diversified | max (wᵀσ)/√(wᵀΣw) | — |
| D8 | **MDC** — maximum decorrelation | min wᵀCw, C the correlation matrix | — |

All eight share the baseline constraints: **long-only, fully invested, no leverage** (definitions §7).

| # | Task | Direct output | Format |
| --- | --- | --- | --- |
| D9 | Implement each as `f(returns_window) → weights` | 8 functions, one signature | Interchangeable in the C2 loop |
| D10 | Specification table | **Table 3.2 — Strategy specifications** | Cols: strategy, objective (formula), constraints, parameters, estimation inputs needed |
| D11 | Sanity check on one fixed window: do IV and ERC differ, and does the difference track the correlation structure? | Short diagnostic + a sentence in the report | The brief asks this explicitly |
| D12 | Check MV, GMV and MSR give three distinct weight vectors on the same window | Diagnostic table | If they coincide, λ is wrong |

**Done when:** D11 and D12 both show distinct results and the report can state *why* they differ.

---

## 6. Workstream E — Experiments and performance

Brief: *Methodology — evaluate performance.* Report sections: **Results**.

| # | Task | Direct output | Format |
| --- | --- | --- | --- |
| E1 | Run 8 strategies × 100 experiments, gross and net of costs | Raw results frame | Rows: experiment × strategy. Cols: ann. return, ann. vol, Sharpe, max DD, Sterling, Sortino, Calmar, turnover — gross and net |
| E2 | Define and document every metric convention | **Table 4.1 — Performance conventions** | Cols: metric, formula, annualisation, risk-free used, drawdown denominator. The brief asks for this precision |
| E3 | Headline results, median across the 100 experiments | **Table 4.2 — Net performance by strategy** | Rows: 8 strategies in fixed order. Cols: ann. return %, ann. vol %, Sharpe, max DD %, Sterling, turnover %/yr. **Net of costs.** Gross version goes in the appendix |
| E4 | Dispersion, not just the median | **Table 4.3 — Dispersion** | Per strategy: median, IQR, 10th and 90th percentile of Sharpe and of net return |
| E5 | Same, as a figure | **Figure 4.1 — Sharpe ratio across 100 experiments** | Horizontal box plots, one row per strategy, sorted by median, EW drawn as a dashed reference line |
| E6 | Proportion of experiments beating EW | **Figure 4.2 — Win rate vs equally weighted** | Horizontal bars, 50% reference line. Also as a column in Table 4.2 |
| E7 | Gross vs net comparison | **Table 4.4 — Cost impact** | Per strategy: gross Sharpe, net Sharpe, difference, turnover. Shows who pays for their own trading |
| E8 | Cumulative wealth, recommended strategy vs EW vs S&P 500 | **Figure 4.3 — Growth of $1** | One representative experiment, log y-axis, stated which experiment and why |
| E9 | Weight evolution for the recommended strategy | **Figure 4.4 — Portfolio weights over time** | Stacked area, fixed asset order and colours |
| E10 | Optimisation failures | **Table A.1 — Optimisation failures** (appendix) | From C6. If empty, say so explicitly — do not omit the table |

**Done when:** every number in Table 4.2 is reproducible from notebook 05 under the fixed seed, and the
net table is the one in the main report.

---

## 7. Workstream F — Robustness and limitations

Brief: *Methodology — robustness; show whether conclusions depend on period or subset.* Report section:
**Robustness checks and limitations.**

| # | Task | Direct output | Format |
| --- | --- | --- | --- |
| F1 | Re-run at **2×** transaction costs | **Table 5.1 — Ranking under harsher costs** | Cols: strategy, rank at 1× cost, rank at 2×, net Sharpe at each. The question is whether the ranking changes |
| F2 | Split results by **period**: early vs late windows | **Figure 5.1 — Sharpe by window start date** | Scatter, window start on x, Sharpe on y, one small multiple per strategy |
| F3 | Split results by **subset composition**: with vs without a diversifier (`TLT` or `GLD`) | **Table 5.2 — Sensitivity to subset composition** | Per strategy: median Sharpe with, without, difference, n experiments each. *Proposed; confirm in F* |
| F4 | Same for **sector concentration**: subsets holding two or more assets from one sector vs none | Rows added to Table 5.2 | Tests whether near-collinear pairs drive the ranking. *Proposed; confirm in F* |
| F5 | Concentration: max weight and effective number of assets per strategy | **Table 5.3 — Concentration** | Per strategy: mean max weight %, mean effective N (1/Σwᵢ²) |
| F6 | Write the limitations: overlapping windows are **not** 100 independent tests; survivorship bias and hindsight in choosing today's large caps; one vendor, one adjustment method; spin-offs treated as reinvested in the parent; dividends reinvested gross of tax; a 15-year panel without the 2008 crisis | Draft section | ~1 page. Each limitation states its direction of bias, not just its existence |

**Done when:** F6 names a direction of bias for each limitation, and the report never calls the 100
experiments independent.

---

## 8. Workstream G — Report and submission

Target structure, from the brief. Main report written **for an investment committee**; technical output
in the appendix.

| § | Section | Length | Anchored by |
| --- | --- | --- | --- |
| 1 | Executive summary and recommendation | 1 page | Table 4.2, one named strategy, stated investor objective |
| 2 | Data | 1.5 pages | Tables 1.1–1.3, Figures 1.1–1.2 |
| 3 | Stylised facts | 3 pages | Tables 2.1–2.5, Figures 2.1–2.5 |
| 4 | Methods and assumptions | 2 pages | Tables 3.1–3.2, 4.1 |
| 5 | Results | 3 pages | Tables 4.2–4.4, Figures 4.1–4.4 |
| 6 | Robustness and limitations | 2 pages | Tables 5.1–5.3, Figure 5.1 |
| 7 | Conclusions | 0.5 page | The recommendation, and the conditions under which we would reconsider it |
| — | References | — | Ledoit–Wolf and any other cited source |
| — | Reproducibility appendix | — | G4 below |

| # | Task | Direct output |
| --- | --- | --- |
| G1 | Agree section owners and a single document owner who merges | Owner list at the top of the draft |
| G2 | Final re-run of **all** notebooks on **one day**, so every number shares an extraction date | One extraction date quoted throughout |
| G3 | Consistency pass: every table and figure referenced in the text, numbering contiguous, strategy and asset order identical everywhere | Checked draft |
| G4 | Reproducibility appendix: source, extraction date, seed, package versions, notebook run order, retrieval instructions | Appendix section |
| G5 | Export to PDF; bundle notebooks as supporting files | Submission package |
| G6 | Submit via Moodle before 30 October 2026 | Confirmation |

**The recommendation must be a decision**, not a summary: one strategy, for a stated investor objective,
with the evidence behind it and the conditions that would change it. The brief says a strategy that
performs poorly still supports a strong project if the analysis explains why.

---

## 9. Schedule

| Week | Dates | Target |
| --- | --- | --- |
| 1 | Oct 1–7 | Workstream A complete. Workstream C started (C1–C3) |
| 2 | Oct 8–14 | Workstream B complete. Workstream C complete, tests passing |
| 3 | Oct 15–21 | Workstream D complete. E1 run. Draft sections 2 and 3 |
| 4 | Oct 22–26 | Workstreams E and F complete. Draft sections 4, 5, 6 |
| 5 | Oct 27–29 | G2 final re-run, G3 consistency pass, G4 appendix, executive summary written last |
| — | Oct 30 | Submit, with a day of slack already spent |

Workstreams B and C are independent — run them in parallel. C and D must be finished before E starts;
E is the long pole.

---

## 10. Checklist before submitting

- [ ] Extraction date stated, identical across every number in the report
- [ ] Random seed stated and results reproduce under it
- [ ] 15-year span **and** all-asset intersection both disclosed
- [ ] Any proxy in the universe labelled, investable counterpart named
- [ ] Stylised facts assessed, not assumed — Table 2.5 complete at all three frequencies
- [ ] MV distinguished from GMV and MSR, with λ stated
- [ ] IV distinguished from ERC, with the correlation argument made
- [ ] Performance reported **before and after** costs, plus the 2× sensitivity
- [ ] Turnover reported per strategy
- [ ] Win rate vs the equally weighted benchmark reported
- [ ] Optimisation failures logged and shown; no runs silently dropped
- [ ] Overlapping windows never described as independent observations
- [ ] Survivorship bias discussed
- [ ] A single strategy recommended, for a stated objective, with reconsideration conditions
- [ ] Notebooks run top-to-bottom from a clean kernel without error
- [ ] Supporting files bundled; reproducibility appendix complete
