# Independent replication — where the two implementations converge and diverge

**Recorded:** 2026-10-17, revised 2026-10-21 for the colleague's final version · **Compared:** this
repository (workstreams A–F, figures from the 2010–2026 panel, 2026-10-19) against
[`delivered/Backtesting_Implementation.ipynb`](delivered/Backtesting_Implementation.ipynb) and its
exports, final version dated 2026-10-20 · **Files:** [`inventory.md`](inventory.md) ·
**Brief:** [`project-description.md`](../project-description.md)

A group colleague built the backtest independently. This page sets the two side by side. §1 is the bottom
line. §2 lists what changed in the colleague's final version. §§3–9 compare the design point by point. §10
compares the results. §11 lists defects in the colleague's notebook. §12 lists what the group needs to decide.

**Labels.** **Converge** = same choice, or the same in substance. **Diverge** = a different choice that changes
numbers. **Only ours** / **Only theirs** = done on one side only. **Brief** marks the rows where one side
departs from something the brief states explicitly.

"Ours" means this repo; "theirs" means `delivered/`. Their figures are from the quarterly-rebalancing,
15 bp run unless stated otherwise. Ours are net of costs (Tables 4.2, 4.5, 5.1).

---

## 1. Bottom line

1. **On the findings that matter, the two agree, and more closely than before.** The two implementations
   still differ in dataset length, estimation window, risk-free rate, costs and subset rule, yet the paired
   results line up. No strategy beats equal weight on Sharpe in a majority of experiments in either (ours at
   most 46%, theirs at most 48%). IV, ERC and GMV have lower volatility than EW in 98–100% of experiments in
   both, and shallower drawdowns in 63–82%. MV and MSR trail on every risk measure. Costs change no ranking.
   Fifteen of 21 paired cells are now within 5 points (§10.1). Agreement this close across two independent
   codebases is strong evidence that the result is not an artefact of either.
2. **The mean-vs-median effect now shows inside their own notebook.** Their final version reports both. Ranked
   by *mean* Sharpe, theirs puts 1/N first; ranked by *median*, 1/N drops to fourth, behind ERC, MDC and MDP.
   Ours, on medians, puts EW third. This is definitions §9, "medians across experiments are not head-to-head
   results", reproduced by an outside implementation.
3. **The data now match ours.** Their final version uses the same 25 assets (gold and silver through the same
   physically backed ETFs), the same panel (2010-01-04 to 2026-09-30) and a saved data snapshot (§2).
4. **The design still diverges where the brief is explicit.** Theirs uses **5-year** datasets (the brief says
   three-year), a **zero** risk-free rate, and a benchmark that is the S&P 500 **price index**, labelled as an
   ETF (no dividends, not investable). An optimiser failure would still stop the whole run rather than being
   logged.
5. **Theirs has three things worth taking.** A no-rebalancing (buy-and-hold) scenario, which is the brief's
   optional extension F. A wider cost grid (5–50 bp against our 1× and 2×). A Quintile momentum strategy as a
   second naive benchmark.
6. **Theirs covers only part of the brief.** Data treatment, stylised facts, concentration, limitations and a
   recommendation are absent (§3).

---

## 2. What changed in the final version

Changes between the first delivery (2026-10-16) and the final version (2026-10-20), read from a diff of the
two notebooks and their exports. The design is otherwise unchanged: 5-year datasets, rolling 2-year
estimation, uniform draw of 10 of 25, seed 1904, r_f = 0, the same nine strategies and solvers.

| Area | First delivery | Final version | Effect on this comparison |
| --- | --- | --- | --- |
| Gold and silver | Continuous front-month futures | `GLD`, `SLV` | Now **converges** with ours. Roll jumps and the CME calendar issue are gone |
| Panel end | 2024-12-31 | 2026-09-30 (`end="2026-10-01"`) | Now **identical** to ours. Evaluation windows start 2012–2023 instead of 2012–2021 |
| Data snapshot | Live download each run | Download written to `Data_Utilized.xlsx` with a timestamp; the notebook then reads from it. Missing values printed before and after the fill (none) | Results can be reproduced from the delivered files. Extraction date stated (2026-10-18/19) |
| Benchmark | EUR-quoted S&P 500 UCITS ETF on Borsa Italiana | `^GSPC`, the S&P 500 index in USD | FX and calendar noise removed, but it is now the **price** index: no dividends, not investable, still labelled "S&P 500 ETF" (§11, item 4) |
| Summary across runs | Means only | Means **and medians** for every performance table, the benchmark and turnover. Charts and the fee grid now use medians | Closer to the brief. Their own tables now show the mean-vs-median reversal (§1, point 2) |
| Paired metrics | Seven | Eight: adds *Median Annual Return* (median of calendar-year returns within a run) | Minor |
| Max drawdown | Peak started at the first day's wealth | Peak floored at 1 (`cummax().clip(lower=1.0)`), for strategies and benchmark | Defect fixed |
| Weight-evolution figure | Titled GMVP, plotted MDC on dataset 2 | Titled and plotted as MDC, on dataset 3 like the wealth chart | Defect fixed |
| Workbook sheet names | 15 bp run stored as "10bps" | Sheet name built from `FEES` ("15.0bps") | Defect fixed |
| Presentation workbook | Hand-edited copy of the summary | Replaced by `Table Testing Fees.xlsx` (fee table, pivot, colour legend) | — |
| Written conclusions | Cells 15 and 31 | Same text, not updated for the new results | Defect 3 still stands |
| Their results | 1/N top on mean Sharpe; MDC beat 1/N in 56% of runs; MSR in 17% | 1/N top on mean, fourth on median; best paired Sharpe win rate 48% (MDC); MSR 27% | Their two outliers against ours (MSR, MDC) closed (§10.1) |

The results moved because the inputs moved: same seed, but a longer panel and different gold and silver
series give a different set of 100 windows and subsets. No change in the strategies themselves.

---

## 3. Scope

| Brief item | Ours | Theirs | Label |
| --- | --- | --- | --- |
| Universe selection, source, extraction date | Notebook 01, report §2 | Download cell; timestamp saved in the data workbook | Converge on date · Only ours on documentation |
| Dividends, corporate actions, currency, calendar, index vs investable | Tables 1.1–1.3, A1.1–A1.2 | — (one comment on forward fill) | Only ours |
| Stylised facts on one share | Notebook 02 on `JPM` | — | Only ours |
| Eight core strategies | All eight | All eight, plus Quintile | Converge |
| 100 random datasets, walk-forward backtest | Yes | Yes | Converge |
| Costs before and after, less favourable costs | 1× and 2× | 0 bp, 15 bp, and a 5–50 bp grid | Converge |
| Turnover | Yes | Yes, mean and median | Converge |
| Failures logged, no run dropped | Logged, held weights (0 of 3,200) | Raises and stops; none happened | Diverge |
| Medians, dispersion, share beating EW | Tables 4.2–4.5 | Means and medians; box plots; paired win rates | Converge |
| Period and subset dependence | Tables 5.2, A5.1; Figures 5.1–5.2 | Per-asset and per-start-year sheets | Converge |
| Survivorship and today's universe | F6, Table A5.2 | *"Survivorship bias ????"* (a comment) | Only ours |
| Concentration | Table 5.3 | — | Only ours |
| Rebalancing policy (optional extension F) | — | Buy-and-hold vs quarterly throughout | Only theirs |
| Recommendation for a stated investor | ERC (capital preservation); EW (return-seeking) | None; brief conclusions on returns and outliers | Only ours |

---

## 4. Data and universe

| Item | Ours | Theirs | Label | Consequence |
| --- | --- | --- | --- | --- |
| Assets | 20 stocks in four sectors plus `GLD`, `SLV`, `TLT`, `VNQ`, `XOM` | The same 25 tickers | Converge | — |
| Sector groups | 5 groups of 5; `GLD`, `SLV`, `TLT`, `VNQ`, `XOM` form *Real assets & defensive* | 7 groups: *Commodities and Bonds* (3), *Real Estate* (1), *Energy* (1) | Diverge | Matters only because ours stratifies the draw by group (§5). Theirs uses the groups for chart colours only |
| Source and price | Yahoo, `auto_adjust=True` | Yahoo, `auto_adjust=False`, then `Adj Close` | Converge | Both are split- and dividend-adjusted |
| Panel | 2010-01-04 to 2026-09-30 | 2010-01-04 to 2026-09-30 (4,211 sessions) | Converge | — |
| Extraction date | Stated (2026-10-19); downloads cut at a fixed `end="2026-10-01"` | Timestamp in `Data_Utilized.xlsx` (2026-10-18 17:17; the notebook prints 2026-10-19 00:36); `end="2026-10-01"` | Converge | One day apart, same cut-off |
| Data snapshot | Panel rebuilt from Yahoo at fixed bounds; rebuild asserted bit-identical | Prices saved to a workbook and read back | Converge in purpose | Theirs freezes the data itself; ours freezes the bounds |
| Calendar | NYSE sessions from `SPY`; off-calendar prints dropped and counted (none) | Union of all tickers' dates | Converge in effect | All 25 are US-listed, so the union is the NYSE calendar |
| Gaps | Forward-fill up to 3 sessions; longer gaps reported (none) | Forward-fill up to 2; missing values printed before and after (none) | Converge | — |
| Risk-free | `^IRX`, daily | 0 | Diverge | Raises every Sharpe and Sortino by roughly the T-bill yield over volatility. Matters most after 2022, when bills paid about 5%. Also changes MSR (§6) |
| Benchmark | `SPY` (USD, investable, total return); `^GSPC` quoted as the non-investable index | `^GSPC` only, labelled "S&P 500 ETF — Buy & Hold" | Diverge · **Brief** | `^GSPC` is a price index: its `Adj Close` carries no dividends, so the benchmark is short by the dividend yield (about 1.5–2% a year) and every "beats the ETF" figure is flattered. The brief's index-vs-investable distinction is not made |
| Stylised-facts share | `JPM` | — | Only ours | — |

---

## 5. Experiment design

| Item | Ours | Theirs | Label | Consequence |
| --- | --- | --- | --- | --- |
| Experiments | 100 | 100 | Converge | — |
| Seed | 20261001 | 1904 | — | Recorded on both sides, as the brief asks |
| Dataset length | **3 years** | **5 years** | Diverge · **Brief** | The brief says "100 three-year datasets" |
| Estimation / evaluation | 2 years / 1 year | 2 years / 3 years | Diverge | Three-year evaluations overlap more with each other, so the 100 runs carry less independent information. They also blend crash and recovery in one window (§9) |
| Estimation update | First estimate on the 2 years, then a trailing **1 year** | Rolling **2 years** throughout | Diverge | A longer window gives smoother weights. This is the main reason their optimiser turnover is lower (§7) |
| Rebalancing | Quarterly, every 63 sessions | Quarterly, every 63 sessions | Converge | — |
| Execution lag | Formed at close *t*, traded at close *t*+1 | Estimated on prices up to *t*−1, earns from the close of *t* | Converge | Both use one session of lag, though only ours asserts it (§6) |
| Subset | 10 of 25, **2 per sector** | 10 of 25, **uniform** | Diverge | A uniform draw lets the sector mix vary, so some runs have no defensive asset and others hold three banks. This confounds strategy differences with composition (definitions §9, workstream C) |
| Same windows and subsets for all strategies | Yes | Yes | Converge | — |
| Evaluation years covered | 2012-01 to 2026-09 | Starts 2012–2023, ends by 2026-09 | Converge | Both now include 2025–26 |

---

## 6. Engine mechanics

| Item | Ours | Theirs | Label |
| --- | --- | --- | --- |
| Portfolio returns | Simple returns, compounded | Simple returns, compounded | Converge |
| Weight drift between rebalances | Yes | Yes | Converge |
| Initial portfolio | Bought from cash; cost charged; its 100% turnover excluded from reported turnover | Identical | Converge |
| Cost application | Multiplicative: (1 − c₀)(1 + g)(1 − c) − 1 | Subtracted from the first day's return | Converge (second-order difference) |
| Look-ahead protection | Guard that **raises**, plus deliberate-leak tests | Correct by construction; not tested | Only ours |
| Optimisation failure | Logged; hold drifted weights (EW if none yet); run kept | `RuntimeError` stops the whole notebook | Diverge · **Brief** ("do not silently remove") |
| Weight-sum check | `_as_weights` validation | Raises if off by more than 1e-4 | Converge |
| Cost scenarios | Each weight decision computed once and replayed at 2×, verified identical | Full re-run for each fee level (7 × ≈ 2.9 min) | Converge on results; ours is faster |
| Reproducibility | Fixed panel bounds, rebuild asserted bit-identical, locked environment | Saved data workbook, fixed end date; hard-coded Windows path, no environment file | Converge on data · Diverge on environment |

---

## 7. Strategies

| Strategy | Ours | Theirs | Label |
| --- | --- | --- | --- |
| EW | 1/N | 1/N | Converge |
| GMV | min w′Σw, exact QP (support enumeration) | min w′Σw, SLSQP | Converge (solver only) |
| MV | max w′μ − (λ/2)w′Σw, **λ = 3**, checked to differ from GMV and MSR | max w′μ − 0.5·w′Σw, i.e. **λ = 1** in our notation | Diverge |
| MSR | r_f = mean `^IRX` over the window; exact QP; failure if no asset beats r_f | r_f = 0; SLSQP on the ratio | Diverge |
| IV | wᵢ ∝ 1/σᵢ | wᵢ ∝ 1/σᵢ | Converge |
| ERC | Spinu's convex formulation, own Newton solver, contributions checked to 1e-8 | Spinu's formulation via `riskparityportfolio.vanilla.design` | Converge |
| MDP | max w′σ/√(w′Σw), exact QP | Same objective, SLSQP | Converge (solver only) |
| MDC | min w′Cw, exact QP | Same objective, SLSQP (ftol 1e-10) | Converge (solver only) |
| Quintile | — | Top 20% of assets (2 of 10) by mean return over the lookback, equally weighted | Only theirs |
| Expected returns, covariance | Sample mean and covariance of daily simple returns, ×252 | Same, over 2 years instead of 1 | Converge in method |
| Constraints | Long-only, fully invested | Long-only, fully invested | Converge |
| Shrinkage switch | Ledoit–Wolf, robustness only | — | Only ours |
| Specification table with shortcomings | Table 3.2 | — | Only ours |

**MV.** Their λ = 1 is a third of ours, so their MV leans further toward the highest-mean asset. Their MV has
the highest volatility of any strategy (26%) and the highest turnover (240%/yr). Ours documents how often MV
lands on a single asset (32.3% of days, Table 5.3) and on MSR (13 of 400 windows). Theirs does not check
either.

**MSR.** With r_f = 0, theirs maximises return over volatility rather than excess return over volatility.
Their MSR is the weakest strategy against 1/N (beats it in 27% of runs).

---

## 8. Costs, turnover and metrics

| Item | Ours | Theirs | Label |
| --- | --- | --- | --- |
| Cost level | 2–3 bp one-way per asset, from liquidity | Flat 15 bp, grid 5–50 bp | Diverge |
| Cost convention | bp × \|Δw\| summed over assets | fee × Σ\|Δw\| | Converge |
| Turnover | Annualised two-way, Σ\|Δw\| per year | Annualised two-way, Σ\|Δw\| per year, mean and median | Converge |
| Annual return | Geometric | Arithmetic mean × 252 | Diverge |
| Volatility | sd × √252 | sd × √252 (`quantstats`) | Converge |
| Sharpe, Sortino | Excess over `^IRX` | r_f = 0 (`quantstats`) | Diverge |
| Max drawdown | From wealth 1 at the start of the evaluation | From wealth 1 (peak floored at 1); 3-year path | Converge |
| Sterling | Return / (\|max DD\| + 10%) | Return / average drawdown | Diverge |
| Calmar | Return / \|max DD\| | `quantstats` CAGR / \|max DD\| | Converge |
| Extra metrics | — | Daily win rate, skew, kurtosis, VaR, CVaR, median calendar-year return | Only theirs |
| Summary across runs | Medians, IQR, P10/P90 | Means and medians; box plots | Converge (no IQR table in theirs) |
| Paired win rate vs EW | Sharpe, plus Δ return, vol and drawdown (Table 4.5) | Eight metrics, vs 1/N, Quintile and the "ETF" | Converge |

Their column called *Win Rate* is the share of **days** with a positive return. Ours, *Beats EW*, is the
share of **experiments** in which a strategy beats EW. The names should not be merged.

---

## 9. Robustness and dependence

| Item | Ours | Theirs | Label |
| --- | --- | --- | --- |
| Period dependence | Paired Δ Sharpe vs EW by evaluation year (Figure 5.1); March 2020 in the evaluation year / in the estimation period only / neither (Table 5.2) | Paired win rate and Δ Sharpe by out-of-sample start year (2012–2023), every strategy against three benchmarks | Converge in idea |
| Subset dependence | Each asset held vs not (Figure 5.2); near-collinear pair, re-checked in crash-free windows | Each asset held vs not, Sharpe win rate and Δ Sharpe | Converge in idea |
| Noise yardstick | ±2 standard errors stated with every split | None | Only ours |
| Cost stress | 2×: no rank moves | 5–50 bp: no rank moves on return | Converge |
| Rebalancing policy | — | Buy-and-hold vs quarterly | Only theirs |

**Where the crash falls cannot be read from their split.** Each of their evaluation windows is three years
long, so a window that contains March 2020 usually contains the recovery too. Their ERC-vs-1/N table shows
wins for 2017–18 starts (12 of 13 in 2017, 8 of 9 in 2018) and losses for 2019–23 starts (win rates 20–43%),
but the 2019 and 2020 starts contain the crash *and* the rebound. Our finding, that optimisers gain on EW
when the crash is in the evaluation year and lose when it is only in the estimation data, needs one-year
evaluations to show.

---

## 10. Results compared

Theirs: quarterly rebalancing at 15 bp, 100 runs. Ours: net of costs, 100 experiments. Per-run returns and
volatilities are not comparable in level (3-year vs 1-year windows, arithmetic vs geometric, r_f = 0 vs
`^IRX`). Win rates and rankings are comparable.

### 10.1 Share of experiments in which the strategy beats EW (paired)

| Strategy | Sharpe — ours | Sharpe — theirs | Lower vol — ours | Lower vol — theirs | Shallower max DD — ours | Shallower max DD — theirs |
| --- | --- | --- | --- | --- | --- | --- |
| GMV | 42% | 35% | 98% | 100% | 63% | 70% |
| MV | 30% | 29% | 1% | 0% | 8% | 12% |
| MSR | 30% | 27% | 15% | 34% | 24% | 43% |
| IV | 39% | 46% | 100% | 100% | 80% | 82% |
| ERC | 46% | 45% | 100% | 100% | 78% | 78% |
| MDP | 45% | 45% | 92% | 89% | 72% | 69% |
| MDC | 44% | 48% | 67% | 71% | 56% | 67% |

**Converge.** Fifteen of the 21 cells are within 5 points (twelve in the first delivery), and every risk
column is ordered the same way: risk-based strategies win on risk and lose on return, and MV/MSR lose on
both. The Sharpe column now agrees within 7 points for every strategy. The remaining gaps:

- **MSR on risk (lower vol 15% vs 34%, drawdown 24% vs 43%):** their r_f = 0 and 2-year μ make it a
  different portfolio. Its Sharpe win rate, the earlier outlier (17%), now matches ours.
- **GMV and IV on Sharpe (7 points each), MDC on drawdown (11 points):** no single cause identified. Two
  standard errors on a win rate near 50% over 100 experiments are about ±10 points, before allowing for
  overlap, so gaps of this size are within what a different draw of windows and subsets can produce.

### 10.2 Rankings

| | Ours: median net Sharpe | Theirs: median Sharpe, 15 bp | Theirs: mean Sharpe, 15 bp |
| --- | --- | --- | --- |
| 1 | MDC 1.02 | ERC 0.914 | 1/N 0.944 |
| 2 | MDP 1.01 | MDC 0.910 | IV 0.938 |
| 3 | EW 1.00 | MDP 0.900 | ERC 0.938 |
| 4 | ERC 0.99 | 1/N 0.889 | MDC 0.912 |
| 5 | IV 0.99 | IV 0.885 | MDP 0.901 |
| 6 | GMV 0.93 | GMV 0.786 | GMV 0.816 |
| 7 | MSR 0.69 | Quintile 0.717 | Quintile 0.739 |
| 8 | MV 0.57 | MV 0.670 | MSR 0.714 |
| 9 | — | MSR 0.652 | MV 0.676 |

**Diverge in order, converge in shape.** All three columns have the same tiers: EW and the risk-based
strategies within a few hundredths of each other, then GMV, then MV and MSR (and Quintile) well behind.
EW's place in the top tier depends on the statistic: first on their mean, fourth on their median, third on
ours. Ours reads neighbours within about 0.01 as ties (definitions §9). On that reading, every top five is a
tie (spans 0.03, 0.03 and 0.04).

### 10.3 Turnover (annualised two-way, %/yr)

| | EW | IV | ERC | MDP | MDC | GMV | MSR | MV | Quintile |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ours | 20 | 27 | 31 | 78 | 78 | 87 | 265 | 349 | — |
| Theirs (mean) | 26 | 26 | 27 | 54 | 56 | 58 | 189 | 240 | 219 |

**Converge in ranking, diverge in level.** The order is the same. Their optimisers trade about a third less,
which is what a 2-year estimation window should do against a 1-year one. Their medians are within 0.07 of
their means.

### 10.4 Costs

**Converge.** Neither side finds a cost level that reorders strategies. Ours: doubling 2–3 bp moves Sharpe
by under 0.01. Theirs (median annual return): at 50 bp the ranking is the same as at 0 bp, and the heaviest
cost (MV) is 1.49 pp/yr.

### 10.5 Rebalancing (theirs only)

Median annual return, buy-and-hold for three years against quarterly rebalancing at 15 bp: buy-and-hold
wins for MSR (13.1% vs 10.3%), MV (20.4% vs 18.0%) and Quintile (19.4% vs 16.1%), and makes little
difference for EW and the risk-based strategies (within 1 pp). On median Sharpe the split is the same:
buy-and-hold is better for MSR, MV and Quintile by 0.12–0.18; for EW and the risk-based strategies the
difference is within ±0.03 either way. For the return-driven optimisers, re-estimating μ every quarter costs more than it
adds, even before fees. Ours has no equivalent.

### 10.6 Conclusions drawn

| | Ours | Theirs |
| --- | --- | --- |
| Headline | No strategy beats EW in a clear majority; risk-based strategies buy lower risk for 1–2 pp of return | Markowitz highest return without rebalancing; "Quintile" highest after fees (unchanged from the first delivery; see §11, item 3) |
| Recommendation | ERC for a capital-preservation investor, EW for a return-seeking one | None |

---

## 11. Defects in the colleague's notebook

Found by reading the code against its saved output. Status is for the final version. None of the open items
changes the convergence in §10.

| # | Where (final cell numbers) | Defect | Status |
| --- | --- | --- | --- |
| 1 | Cell 37, weight-evolution figure | Was titled GMVP while plotting MDC on dataset 2 | **Fixed:** titled MDC, plots dataset 3 like the wealth chart |
| 2 | Cell 29, summary workbook | 15 bp run stored in a sheet named "10bps" | **Fixed:** sheet name built from `FEES` |
| 3 | Cell 17, conclusion 2 | "After fees, the highest performing strategy appears to be the Quintile." Their own tables have Markowitz higher on return (median 18.0% vs 16.1%) and 1/N (mean) or ERC (median) highest on Sharpe | **Open:** text not updated |
| 4 | Cells 3, 16 | Benchmark is `^GSPC`, a price index without dividends, labelled "S&P 500 ETF — Buy & Hold". It replaces an EUR-quoted ETF | **Changed, still open:** FX and calendar noise gone; dividends missing, so the benchmark is understated by about 1.5–2% a year and "beats the ETF" rates are flattered. A total-return series (e.g. `SPY` adjusted, or `^SP500TR`) would fix it |
| 5 | Cell 3 | Futures and stocks on a union calendar | **Resolved:** all assets are US-listed; no gaps before the fill |
| 6 | Cells 8, 13 | Optimiser failure raises and stops the run | **Open:** brief requires failures to be logged; harmless here only because none occurred |
| 7 | Cell 16 | Drawdown peak started at the first day's wealth | **Fixed:** peak floored at 1 |
| 8 | Cell 1 | Not reproducible as delivered | **Partly fixed:** data saved with a timestamp and read back, end date fixed. Still a hard-coded Windows `file_path` and no environment file (yfinance version printed only) |
| 9 | `Data_Utilized.xlsx` vs cell 3 output | The timestamp saved in the workbook (2026-10-18 17:17) differs from the one the notebook prints (2026-10-19 00:36) | **New, minor:** the delivered workbook and the saved output come from different runs of the download cell. Worth one line if the extraction date is quoted |

---

## 12. Decisions for the group

1. **Keep this repo as the submission pipeline.** It meets the brief's explicit requirements where theirs
   still departs from them: three-year datasets, failure logging, a dividend-inclusive investable benchmark,
   and the index-vs-investable distinction. It also covers the parts theirs does not (data, stylised facts,
   F5–F6).
2. **Cite the colleague's work as an independent replication** in report §6. Use §10.1 of this page: two
   implementations on the same data, with different windows, risk-free rate, costs and estimation windows,
   reach the same paired conclusions. That is a robustness result, and it is free.
3. **Consider adopting from theirs** (each a choice, not a requirement):
   - a **no-rebalancing scenario** for the recommended strategy and EW (optional extension F; §10.5 suggests
     it matters for MV and MSR);
   - a **wider cost grid** as a one-line addition to Table 5.1, since the replay makes extra cost levels free;
   - the **Quintile** strategy as a second naive benchmark. It would need to be fixed before any result is
     seen, per definitions §7.
4. **Tell the colleague about the open items in §11**, particularly 3 and 4 if their figures or conclusions
   are going into the shared report: the Quintile conclusion, and the price-only benchmark labelled as an ETF.
5. Any adoption goes into `project-definitions.md` §8 first, then the notebooks, in order.
