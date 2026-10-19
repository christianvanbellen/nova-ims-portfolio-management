# Independent replication — where the two implementations converge and diverge

**Recorded:** 2026-10-17, our figures refreshed 2026-10-19 on the 2010–2026 panel · **Compared:** this repository (workstreams A–F) against
[`delivered/Backtesting_Implementation.ipynb`](delivered/Backtesting_Implementation.ipynb) and its
exports, dated 2026-10-16 · **Files:** [`inventory.md`](inventory.md) ·
**Brief:** [`project-description.md`](../project-description.md)

A group colleague built the backtest independently. This page sets the two side by side. §1 is the bottom
line. §§2–8 compare the design point by point. §9 compares the results. §10 lists defects found in the
colleague's notebook. §11 lists what the group needs to decide.

**Labels.** **Converge** = same choice, or the same in substance. **Diverge** = a different choice that changes
numbers. **Only ours** / **Only theirs** = done on one side only. **Brief** marks the rows where one side
departs from something the brief states explicitly.

"Ours" means this repo; "theirs" means `delivered/`. Their figures are from the quarterly-rebalancing,
15 bp run unless stated otherwise. Ours are net of costs (Tables 4.2, 4.5, 5.1).

---

## 1. Bottom line

1. **On the findings that matter, the two agree.** The two implementations differ in window length,
   estimation window, risk-free rate, costs, benchmark and aggregation, yet the paired results line up
   closely. No strategy beats equal weight on Sharpe in a clear majority of experiments in either (ours at
   most 46%, theirs at most 56%). IV, ERC and GMV have lower volatility than EW in 98–100% of experiments
   in both, and shallower drawdowns in 63–80%. MV and MSR trail on every risk measure. Costs change no
   ranking. Agreement this close across two independent codebases is strong evidence that the result is
   not an artefact of either.
2. **The column-wise rankings differ, and the reason is one we already record.** Ranked by *mean* Sharpe,
   theirs puts 1/N first. Ranked by *median* Sharpe, ours puts EW third, 0.02 behind the top. Paired head
   to head, the two agree (point 1). This is definitions §9, "medians across experiments are not head-to-head results", reproduced
   by an outside implementation.
3. **The design diverges in ways the brief cares about.** Theirs uses **5-year** datasets (the brief says
   three-year), data that **ends 2024-12-31** (the brief says latest available), **futures** for gold and
   silver, a **EUR-quoted** S&P 500 ETF as benchmark, a **zero** risk-free rate, and summarises by **means**
   (the brief asks for medians and dispersion). An optimiser failure would stop the whole run rather than
   being logged.
4. **Theirs has three things worth taking.** A no-rebalancing (buy-and-hold) scenario, which is the brief's
   optional extension F. A wider cost grid (5–50 bp against our 1× and 2×). A Quintile momentum strategy as a
   second naive benchmark.
5. **Theirs covers only part of the brief.** Data treatment, stylised facts, concentration, limitations and a
   recommendation are absent (§2).

---

## 2. Scope

| Brief item | Ours | Theirs | Label |
| --- | --- | --- | --- |
| Universe selection, source, extraction date | Notebook 01, report §2 | Download cell; no extraction date stated | Only ours |
| Dividends, corporate actions, currency, calendar, index vs investable | Tables 1.1–1.3, A1.1–A1.2 | — (one comment on forward fill) | Only ours |
| Stylised facts on one share | Notebook 02 on `JPM` | — | Only ours |
| Eight core strategies | All eight | All eight, plus Quintile | Converge |
| 100 random datasets, walk-forward backtest | Yes | Yes | Converge |
| Costs before and after, less favourable costs | 1× and 2× | 0 bp, 15 bp, and a 5–50 bp grid | Converge |
| Turnover | Yes | Yes | Converge |
| Failures logged, no run dropped | Logged, held weights (0 of 3,200) | Raises and stops; none happened | Diverge |
| Medians, dispersion, share beating EW | Tables 4.2–4.5 | Means; box plots; paired win rates | Partial |
| Period and subset dependence | Tables 5.2, A5.1; Figures 5.1–5.2 | Per-asset and per-start-year sheets | Converge |
| Survivorship and today's universe | F6, Table A5.2 | *"Survivorship bias ????"* (a comment) | Only ours |
| Concentration | Table 5.3 | — | Only ours |
| Rebalancing policy (optional extension F) | — | Buy-and-hold vs quarterly throughout | Only theirs |
| Recommendation for a stated investor | ERC (capital preservation); EW (return-seeking) | None; brief conclusions on returns and outliers | Only ours |

---

## 3. Data and universe

| Item | Ours | Theirs | Label | Consequence |
| --- | --- | --- | --- | --- |
| Equities, `TLT`, `VNQ`, `XOM` | 20 stocks in four sectors plus `TLT`, `VNQ`, `XOM` | The same 23 tickers | Converge | — |
| Gold and silver | `GLD`, `SLV`: physically backed ETFs | `GC=F`, `SI=F`: continuous front-month **futures** | Diverge | Futures are proxies, not holdings (definitions §9). Yahoo's continuous series are not roll-adjusted, so each roll can print a jump that is not a return. Futures also trade on the CME calendar (below) |
| Sector groups | 5 groups of 5; gold, silver, `TLT`, `VNQ`, `XOM` form *Real assets & defensive* | 7 groups: *Commodities and Bonds* (3), *Real Estate* (1), *Energy* (1) | Diverge | Matters only because ours stratifies the draw by group (§4). Theirs uses the groups for chart colours only |
| Source and price | Yahoo, `auto_adjust=True` | Yahoo, `auto_adjust=False`, then `Adj Close` | Converge | Both are split- and dividend-adjusted |
| Panel | 2010-01-04 to 2026-09-30 | 2010-01-04 to 2024-12-31 | Converge on start · Diverge on end · **Brief** | Theirs misses the latest 21 months. The brief asks for the latest available data |
| Extraction date | Stated (2026-10-19); downloads cut at a fixed `end="2026-10-01"` | Not stated; `end="2025-01-01"` | Diverge · **Brief** | The brief asks for the extraction date to be stated |
| Calendar | NYSE sessions from `SPY`; off-calendar prints dropped and counted (none) | Union of all tickers' dates | Diverge | With futures in the panel, CME sessions on NYSE holidays become rows where every stock is forward-filled and returns zero. This needs checking on their panel (not verifiable from the saved output) |
| Gaps | Forward-fill up to 3 sessions; longer gaps reported (none) | Forward-fill up to 2; reports 0 missing | Converge | — |
| Risk-free | `^IRX`, daily | 0 | Diverge | Raises every Sharpe and Sortino by roughly the T-bill yield over volatility. Matters most after 2022, when bills paid about 5%. Also changes MSR (§5) |
| Benchmark | `SPY` (USD, investable); `^GSPC` quoted as the non-investable index | `CSSPX.MI`: iShares S&P 500 UCITS ETF, **EUR-quoted** on Borsa Italiana | Diverge · **Brief** | Its returns carry EUR/USD moves that the USD strategies do not, and it trades on the Italian calendar. Its first sessions (from 2010-05-19) repeat one stale price. The brief's index-vs-investable distinction is not made |
| Stylised-facts share | `JPM` | — | Only ours | — |

---

## 4. Experiment design

| Item | Ours | Theirs | Label | Consequence |
| --- | --- | --- | --- | --- |
| Experiments | 100 | 100 | Converge | — |
| Seed | 20261001 | 1904 | — | Recorded on both sides, as the brief asks |
| Dataset length | **3 years** | **5 years** | Diverge · **Brief** | The brief says "100 three-year datasets" |
| Estimation / evaluation | 2 years / 1 year | 2 years / 3 years | Diverge | Three-year evaluations overlap more with each other, so the 100 runs carry less independent information. They also blend crash and recovery in one window (§8) |
| Estimation update | First estimate on the 2 years, then a trailing **1 year** | Rolling **2 years** throughout | Diverge | A longer window gives smoother weights. This is the main reason their optimiser turnover is lower (§6) |
| Rebalancing | Quarterly, every 63 sessions | Quarterly, every 63 sessions | Converge | — |
| Execution lag | Formed at close *t*, traded at close *t*+1 | Estimated on prices up to *t*−1, earns from the close of *t* | Converge | Both use one session of lag, though only ours asserts it (§5) |
| Subset | 10 of 25, **2 per sector** | 10 of 25, **uniform** | Diverge | A uniform draw lets the sector mix vary, so some runs have no defensive asset and others hold three banks. This confounds strategy differences with composition (definitions §9, workstream C) |
| Same windows and subsets for all strategies | Yes | Yes | Converge | — |
| Evaluation years covered | 2012-01 to 2026-09 | Starts 2012–2021, ends by 2024-12 | Diverge | Theirs has no 2025–26 evaluation |

---

## 5. Engine mechanics

| Item | Ours | Theirs | Label |
| --- | --- | --- | --- |
| Portfolio returns | Simple returns, compounded | Simple returns, compounded | Converge |
| Weight drift between rebalances | Yes | Yes | Converge |
| Initial portfolio | Bought from cash; cost charged; its 100% turnover excluded from reported turnover | Identical | Converge |
| Cost application | Multiplicative: (1 − c₀)(1 + g)(1 − c) − 1 | Subtracted from the first day's return | Converge (second-order difference) |
| Look-ahead protection | Guard that **raises**, plus deliberate-leak tests | Correct by construction; not tested | Only ours |
| Optimisation failure | Logged; hold drifted weights (EW if none yet); run kept | `RuntimeError` stops the whole notebook | Diverge · **Brief** ("do not silently remove") |
| Weight-sum check | `_as_weights` validation | Raises if off by more than 1e-4 | Converge |
| Cost scenarios | Each weight decision computed once and replayed at 2×, verified identical | Full re-run for each fee level (7 × ≈ 2.7 min) | Converge on results; ours is faster |
| Reproducibility | Fixed panel bounds, rebuild asserted bit-identical | Live download, no end-date lock, local Windows paths | Diverge |

---

## 6. Strategies

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
the highest volatility of any strategy (26%) and the highest turnover (237%/yr). Ours documents how often MV
lands on a single asset (32.3% of days, Table 5.3) and on MSR (13 of 400 windows). Theirs does not check
either.

**MSR.** With r_f = 0, theirs maximises return over volatility rather than excess return over volatility.
Their MSR is the weakest strategy against 1/N (beats it in 17% of runs).

---

## 7. Costs, turnover and metrics

| Item | Ours | Theirs | Label |
| --- | --- | --- | --- |
| Cost level | 2–3 bp one-way per asset, from liquidity | Flat 15 bp, grid 5–50 bp | Diverge |
| Cost convention | bp × \|Δw\| summed over assets | fee × Σ\|Δw\| | Converge |
| Turnover | Annualised two-way, Σ\|Δw\| per year | Annualised two-way, Σ\|Δw\| per year | Converge |
| Annual return | Geometric | Arithmetic mean × 252 | Diverge |
| Volatility | sd × √252 | sd × √252 (`quantstats`) | Converge |
| Sharpe, Sortino | Excess over `^IRX` | r_f = 0 (`quantstats`) | Diverge |
| Max drawdown | From wealth 1 at the start of the evaluation | From the first day's wealth (a loss on day 1 is missed); 3-year path | Diverge (minor) |
| Sterling | Return / (\|max DD\| + 10%) | Return / average drawdown | Diverge |
| Calmar | Return / \|max DD\| | `quantstats` CAGR / \|max DD\| | Converge |
| Extra metrics | — | Daily win rate, skew, kurtosis, VaR, CVaR | Only theirs |
| Summary across runs | Medians, IQR, P10/P90 | **Means**; medians only in the box plots | Diverge · **Brief** |
| Paired win rate vs EW | Sharpe, plus Δ return, vol and drawdown (Table 4.5) | Seven metrics, vs 1/N, Quintile and the ETF | Converge |

Their column called *Win Rate* is the share of **days** with a positive return. Ours, *Beats EW*, is the
share of **experiments** in which a strategy beats EW. The names should not be merged.

---

## 8. Robustness and dependence

| Item | Ours | Theirs | Label |
| --- | --- | --- | --- |
| Period dependence | Paired Δ Sharpe vs EW by evaluation year (Figure 5.1); March 2020 in the evaluation year / in the estimation period only / neither (Table 5.2) | Paired win rate and Δ Sharpe by out-of-sample start year, every strategy against three benchmarks | Converge in idea |
| Subset dependence | Each asset held vs not (Figure 5.2); near-collinear pair, re-checked in crash-free windows | Each asset held vs not, Sharpe win rate and Δ Sharpe | Converge in idea |
| Noise yardstick | ±2 standard errors stated with every split | None | Only ours |
| Cost stress | 2×: no rank moves | 5–50 bp: no rank moves on return | Converge |
| Rebalancing policy | — | Buy-and-hold vs quarterly | Only theirs |

**Where the crash falls cannot be read from their split.** Each of their evaluation windows is three years
long, so a window that contains March 2020 usually contains the recovery too. Their ERC-vs-1/N table shows
wins for 2017–18 starts (15 of 16 in 2018) and losses for 2019–21 starts, but the 2019 and 2020 starts
contain the crash *and* the rebound. Our finding, that optimisers gain on EW when the crash is in the
evaluation year and lose when it is only in the estimation data, needs one-year evaluations to show.

---

## 9. Results compared

Theirs: quarterly rebalancing at 15 bp, 100 runs. Ours: net of costs, 100 experiments. Per-run returns and
volatilities are not comparable in level (3-year vs 1-year windows, arithmetic vs geometric, r_f = 0 vs
`^IRX`). Win rates and rankings are comparable.

### 9.1 Share of experiments in which the strategy beats EW (paired)

| Strategy | Sharpe — ours | Sharpe — theirs | Lower vol — ours | Lower vol — theirs | Shallower max DD — ours | Shallower max DD — theirs |
| --- | --- | --- | --- | --- | --- | --- |
| GMV | 42% | 35% | 98% | 100% | 63% | 67% |
| MV | 30% | 33% | 1% | 0% | 8% | 9% |
| MSR | 30% | 17% | 15% | 34% | 24% | 40% |
| IV | 39% | 47% | 100% | 100% | 80% | 80% |
| ERC | 46% | 48% | 100% | 100% | 78% | 74% |
| MDP | 45% | 52% | 92% | 88% | 72% | 67% |
| MDC | 44% | **56%** | 67% | 76% | 56% | 66% |

**Converge.** Twelve of the 21 cells are within 5 points, and every risk column is ordered the same way:
risk-based strategies win on risk and lose on return, and MV/MSR lose on both. The clear gaps:

- **MSR, all three columns (Sharpe 30% vs 17%):** their r_f = 0 and 2-year μ make it a different portfolio.
- **MDC (Sharpe 44% vs 56%, drawdown 56% vs 66%) and IV (Sharpe 39% vs 47%):** no single cause identified.
  Two standard errors on a win rate near 50% over 100 experiments are about ±10 points, before allowing for
  overlap, so gaps of this size are within what a different draw of windows and subsets can produce.

### 9.2 Rankings

| | Ours: median net Sharpe | Theirs: mean Sharpe, 15 bp |
| --- | --- | --- |
| 1 | MDC 1.02 | 1/N 0.903 |
| 2 | MDP 1.01 | ERC 0.900 |
| 3 | EW 1.00 | IV 0.899 |
| 4 | ERC 0.99 | MDC 0.884 |
| 5 | IV 0.99 | MDP 0.875 |
| 6 | GMV 0.93 | GMV 0.765 |
| 7 | MSR 0.69 | Quintile 0.717 |
| 8 | MV 0.57 | MV 0.680 |
| 9 | — | MSR 0.630 |

**Diverge in order, converge in shape.** Both have the same three tiers: EW and the risk-based strategies
within a few hundredths of each other, then GMV, then MV and MSR well behind. EW's position in the top tier
depends on the statistic used. Ours reads neighbours within about 0.01 as ties (definitions §9). On that
reading, both top fives are a tie (ours span 0.03, theirs 0.03).

### 9.3 Turnover (annualised two-way, %/yr)

| | EW | IV | ERC | MDP | MDC | GMV | MSR | MV | Quintile |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ours | 20 | 27 | 31 | 78 | 78 | 87 | 265 | 349 | — |
| Theirs | 25 | 25 | 26 | 54 | 56 | 59 | 193 | 237 | 207 |

**Converge in ranking, diverge in level.** The order is the same. Their optimisers trade about a third less,
which is what a 2-year estimation window should do against a 1-year one.

### 9.4 Costs

**Converge.** Neither side finds a cost level that reorders strategies. Ours: doubling 2–3 bp moves Sharpe
by under 0.01. Theirs: at 50 bp the return ranking is the same as at 0 bp, and the heaviest cost (MV) is
1.35 pp/yr.

### 9.5 Rebalancing (theirs only)

Buy-and-hold for three years beats quarterly rebalancing on return for MSR (13.4% vs 10.2%), MV (20.0% vs
18.3%) and Quintile (18.9% vs 16.5%). It makes little difference for EW and the risk-based strategies. For
the return-driven optimisers, re-estimating μ every quarter costs more than it adds, even before fees. Ours
has no equivalent.

### 9.6 Conclusions drawn

| | Ours | Theirs |
| --- | --- | --- |
| Headline | No strategy beats EW in a clear majority; risk-based strategies buy lower risk for 1–2 pp of return | Markowitz highest return without rebalancing; "Quintile" highest after fees (but see §10, item 3) |
| Recommendation | ERC for a capital-preservation investor, EW for a return-seeking one | None |

---

## 10. Defects in the colleague's notebook

Found by reading the code against its saved output. None changes the convergence in §9.

| # | Where | Defect | Effect |
| --- | --- | --- | --- |
| 1 | Cell 35, `Weight Evolution GMVP Run 3.png` | Title says GMVP; code runs `maximum_decorrelation_portfolio`. It also reads `datasets["dataset 2"]` (keys are 1-based), while the wealth chart for "Run 3" uses dataset 3 | The figure shows MDC on a different run from its caption and from its companion chart |
| 2 | Cell 27, sheet *Performance - Quarterly 10bps* | `FEES = 0.0015`; the sheet holds the 15 bp run | Mislabelled table in both summary workbooks |
| 3 | Cell 15, conclusion 2 | "After fees, the highest performing strategy appears to be the Quintile." Their own table has Markowitz higher on return (17.9% vs 16.2%) and 1/N highest on Sharpe | The conclusion matches no column |
| 4 | Cells 3, 14 | Benchmark `CSSPX.MI` is EUR-quoted and on the Italian calendar; the wealth chart fills its missing days with 0 | Benchmark rows carry FX and calendar noise |
| 5 | Cell 3 | Futures and stocks on a union calendar with forward fill | Possible zero-return rows for stocks on CME-only sessions; unverified |
| 6 | Cells 6, 11 | Optimiser failure raises and stops the run | Brief requires failures to be logged; harmless here only because none occurred |
| 7 | Cell 14 | Drawdown peak starts at the first day's wealth, not at 1 | A loss on day 1 is left out of max drawdown |
| 8 | Cell 1 | `file_path = r""`, no requirements file, live download with no end lock | Not reproducible as delivered |

---

## 11. Decisions for the group

1. **Keep this repo as the submission pipeline.** It meets the brief's explicit requirements where theirs
   departs from them: three-year datasets, latest data, failure logging, medians, and the index-vs-investable
   distinction. It also covers the parts theirs does not (data, stylised facts, F5–F6).
2. **Cite the colleague's work as an independent replication** in report §6. Use §9.1 of this page: two
   implementations with different windows, risk-free rate, costs and estimation windows reach the same paired
   conclusions. That is a robustness result, and it is free.
3. **Consider adopting from theirs** (each a choice, not a requirement):
   - a **no-rebalancing scenario** for the recommended strategy and EW (optional extension F; §9.5 suggests it
     matters for MV and MSR);
   - a **wider cost grid** as a one-line addition to Table 5.1, since the replay makes extra cost levels free;
   - the **Quintile** strategy as a second naive benchmark. It would need to be fixed before any result is
     seen, per definitions §7.
4. **Tell the colleague about §10**, particularly items 1–3 if their figures or conclusions are going into
   anything shared.
5. Any adoption goes into `project-definitions.md` §8 first, then the notebooks, in order.
