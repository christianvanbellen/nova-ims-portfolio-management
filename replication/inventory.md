# Independent replication — file inventory

**Recorded:** 2026-10-17 · **Folder:** [`delivered/`](delivered/) (untracked, added as received) ·
**Comparison:** [`comparison.md`](comparison.md) · **Index:** [`README.md`](README.md)

What the two bodies of work consist of, file by file. §1 is the colleague's folder, §2 this repository,
§3 how the two line up. Nothing in `delivered/` was modified, renamed or re-run;
the files were only sorted into `tables/` and `figures/`. Contents were read from the saved notebook outputs
and the workbooks as delivered.

---

## 1. `delivered/` — the colleague's backtest

Nine files, 2.8 MB, all dated 2026-10-16. One notebook produced everything; the other eight files are its
exports. The notebook was run on Windows (Python 3.14) and its output paths point to a local folder named
*"10 assets, 5 year dataset with 3 year testing and 2 year rolling window"*. That folder name is the design.

### 1.1 Files

| File | Type | Size | Produced by | What it is |
| --- | --- | --- | --- | --- |
| `Backtesting_Implementation.ipynb` | Jupyter notebook | 1.6 MB | — | The whole implementation: download, nine strategies, sampler, backtest loop, metrics, win rates, fee grid, charts. 36 cells (17 code, 19 markdown). Outputs saved, four figures embedded (hence the size) |
| `tables/portfolio_backtest_summary.xlsx` | Workbook, 6 sheets | 23 KB | Cell 27 | Mean metrics per strategy for each scenario, fee sensitivity of annual and cumulative return, turnover |
| `tables/(Tables)portfolio_backtest_summary_20261016.xlsx` | Workbook, 5 sheets | 60 KB | Hand-edited copy of the above | Same tables re-sorted by Sharpe and with columns reordered. A *Testing fees* sheet adds pivoted fee tables and a colour legend ("Gain / Stay the same / Lost with rebalancing"). The presentation version |
| `tables/strategy_comparison_analysis(No Rebalancing).xlsx` | Workbook, 53 sheets | 124 KB | Cell 21 | Paired win rates and per-asset and per-period breakdowns, buy-and-hold scenario |
| `tables/strategy_comparison_analysis(Rebalancing with Fees).xlsx` | Workbook, 53 sheets | 104 KB | Cell 23 | The same for quarterly rebalancing at 15 bp |
| `figures/Average Sharpe Ratio and Max Drawdown.png` | Figure, 2180×991 | 99 KB | Cell 29 | Horizontal bars: mean Sharpe and mean max drawdown per strategy, three scenarios, S&P 500 ETF as a black bar |
| `figures/Sharpe Ratio Distributions across runs.png` | Figure, 2580×993 | 150 KB | Cell 30 | Box plots of Sharpe across the 100 runs, one panel per scenario, sorted by median, ETF in black |
| `figures/Cumulative Returns and Drawdown Evolution on Run 3.png` | Figure, 2480×1189 | 731 KB | Cell 33 | Wealth and drawdown paths of all nine strategies plus the ETF for run 3, three scenarios (2×3 grid) |
| `figures/Weight Evolution GMVP Run 3.png` | Figure, 1782×680 | 52 KB | Cell 35 | Stacked weight bars every 20 sessions. **Mislabelled:** the code plots the maximum-decorrelation portfolio on `dataset 2`, not GMVP on run 3 (comparison §10) |

### 1.2 Notebook, cell by cell

| Cells | Section | Content |
| --- | --- | --- |
| 0–1 | Setup | Imports. Comments state the conventions: risk-free = 0, ×252 annualisation, forward fill (with a note on why not interpolation), and an open question: *"Survivorship bias ????"* |
| 2–3 | Loading data | 25 symbols via `yfinance`, 2010-01-01 to 2025-01-01, `Adj Close`, forward fill up to 2 days. Benchmark `CSSPX.MI` |
| 4–6 | Portfolio definitions | Nine weight functions plus the `portfolios` dict |
| 7–9 | Sampler | Seed 1904; 100 datasets of 5 × 252 sessions, 10 assets drawn uniformly from 25 |
| 10–11 | Backtest | `backtest_with_drift`, then three scenarios × nine strategies × 100 datasets (≈ 7 min) |
| 12–15 | Performance | `performance_metrics` (14 metrics, partly via `quantstats`), mean across runs, three tables plus the ETF. Written conclusions |
| 16–17 | Turnover | Annualised two-way turnover table |
| 18–19 | Diagnostics | Daily win rate, skew, kurtosis, VaR per strategy |
| 20–23 | Win rates and breakdowns | Paired win rates against 1/N, Quintile and the ETF on seven metrics; per-asset and per-start-year tables; Excel export |
| 24–25 | Fee sensitivity | Quarterly backtest re-run at 5, 10, 15, 20, 30, 40 and 50 bp (≈ 19 min) |
| 26–27 | Save tables | `portfolio_backtest_summary.xlsx` |
| 28–31 | Charts | Bar chart and box plots; written conclusions on outliers |
| 32–35 | Example run | Wealth and drawdown paths, weight evolution |

### 1.3 Workbook sheets

**`portfolio_backtest_summary.xlsx`**

| Sheet | Rows × cols | Content |
| --- | --- | --- |
| Performance - No Rebalancing | 9 × 14 | Mean across 100 runs: average annual return, cumulative return, volatility, Sharpe, Sortino, Calmar, Sterling, average and max drawdown, daily win rate, skew, kurtosis, VaR 95%, CVaR 95% |
| Performance - Quarterly 0bps | 9 × 14 | Same, quarterly rebalancing, no costs |
| Performance - Quarterly 10bps | 9 × 14 | Same, quarterly with costs. **Holds the 15 bp run, not 10 bp** (`FEES = 0.0015`; its 1/N return 13.07% equals the 15 bp column of the fee sheet) |
| Annual Returns - Fees | 9 × 16 | Average annual return: no rebalancing, 0 bp, and 5–50 bp, plus the cost at each level |
| Cumulative Returns - Fees | 9 × 16 | The same for cumulative return |
| Turnover | 9 × 2 | Annualised two-way turnover, no rebalancing vs quarterly |

**`(Tables)portfolio_backtest_summary_20261016.xlsx`**: the three performance sheets re-sorted, *Testing fees*
(the annual-return fee table plus two pivots and a colour legend), and *Turnover*. Same numbers, nothing new
computed.

**`strategy_comparison_analysis(…).xlsx`** (both files share this layout, 53 sheets):

| Sheets | Count | Content |
| --- | --- | --- |
| Win Rate vs 1N / vs Quintile / vs SP500 ETF | 3 | Share of the 100 runs in which each strategy beats the benchmark in the same run, on return, volatility, Sharpe, Sortino, Calmar, Sterling and max drawdown |
| Stocks vs {1N, Q, ETF} {strategy} | 25 | Per asset: runs that hold it, Sharpe win rate with and without it, mean Sharpe difference with and without it. Assets in fewer than 5 runs are dropped |
| Periods vs {1N, Q, ETF} {strategy} | 25 | Per out-of-sample start year (2012–2021): runs, wins, win rate, mean and median Sharpe difference |

Sheet names are cut to Excel's 31 characters, so some end mid-word (`Periods vs 1N Inverse Volatilit`).

### 1.4 What is not in the folder

- No data file. Prices are downloaded live, with no end date fixed beyond 2025-01-01, so a re-run gets
  whatever Yahoo serves that day.
- No environment file. The notebook needs `quantstats`, `riskparityportfolio`, `tqdm` and `openpyxl`, none
  of which is in this repo's `pyproject.toml`. `file_path` is an empty string to be filled in by hand.
- No stylised-facts or data-description work. The folder covers the backtest only (comparison §1).

---

## 2. This repository

Tracked files only, excluding the course material in `classes/`.

| Path | What it is |
| --- | --- |
| `project-description.md` | The brief, transcribed |
| `docs/project-definitions.md` | Universe, conventions, fixed parameters, changelog, lessons. Source of truth |
| `docs/group-project-plan.md` | Workstreams A–G, every table and figure specified, schedule, checklist |
| `docs/group-work-division.md` | The group's draft split, set against the plan |
| `docs/report/01_investment_universe.md`, `02_stylised_facts.md` | Draft report sections 2 and 3 |
| `src/config.py` | Universe (25 assets with sector and cost), seed, window, subset rule, λ, lag, panel bounds, extraction date |
| `src/data.py` | Download, calendar, panel, returns, data-quality tables |
| `src/stylised.py` | Stylised-fact tests and GARCH-family fits |
| `src/backtest.py` | Sampler, walk-forward loop, look-ahead guard, cost model, failure log, design tables |
| `src/strategies.py` | The eight strategies, exact QP solver, Spinu ERC, Ledoit–Wolf switch, Table 3.2 |
| `src/performance.py` | 800-run grid, cost replay, metrics, Tables 4.1–4.5 |
| `src/robustness.py` | Period, crisis, subset and asset splits; concentration; limitations measures |
| `src/viz.py`, `src/fmt.py` | Shared chart and table formatting |
| `notebooks/01_investment_universe.ipynb` | Workstream A: Tables 1.1–1.3, A1.1–A1.2, Figures 1.1–1.2 |
| `notebooks/02_stylised_facts.ipynb` | Workstream B on `JPM`: Tables 2.1–2.5, A2.x, Figures 2.1–2.5 |
| `notebooks/03_backtest_engine.ipynb` | Workstream C: Table 3.1, A3.x, 10 unit tests including deliberate-leak tests |
| `notebooks/04_strategies.ipynb` | Workstream D: Table 3.2, weight diagnostics, 10 unit tests |
| `notebooks/05_experiments.ipynb` | Workstream E: builds the 800-run results frame and checks it reproduces bit for bit |
| `notebooks/06_performance.ipynb` | Workstream E: Tables 4.1–4.5, A4.1, A.1, Figures 4.1–4.4 |
| `notebooks/07_robustness.ipynb` | Workstream F: Tables 5.1–5.3, A5.1–A5.2, Figures 5.1–5.2 |
| `pyproject.toml`, `uv.lock` | Locked environment |

Results are not written to disk. Every table is printed by the notebook that builds it, and the panel is cut
at the fixed panel end (`end="2026-10-01"`, exclusive) so a re-run reproduces it.

---

## 3. How the two line up

| Brief part | This repo | `delivered/` |
| --- | --- | --- |
| 1 — universe, data, returns treatment | `01_investment_universe`, report §2 | Download cell only; no documentation |
| 1 — stylised facts | `02_stylised_facts`, report §3 | — |
| 2 — strategies | `04_strategies` | Cell 6 (plus an extra Quintile strategy) |
| Methodology — backtest design | `03_backtest_engine`, `05_experiments` | Cells 9 and 11 |
| Evaluate performance | `06_performance` | Cells 14–19, 29–30, `portfolio_backtest_summary.xlsx` |
| Period and subset dependence | `07_robustness` (F2–F4) | Cells 21 and 23, the two 53-sheet workbooks |
| Costs, less favourable assumptions | `07_robustness` (F1, 2× costs) | Cell 25 (5–50 bp grid) |
| Concentration, limitations | `07_robustness` (F5–F6) | — |
| Rebalancing policy (optional extension F) | — | No-rebalancing vs quarterly scenario throughout |
| Recommendation, report | Not started (G) | Short written conclusions in cells 15 and 31 |
