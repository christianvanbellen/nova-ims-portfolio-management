# Independent replication — file inventory

**Recorded:** 2026-10-17, revised 2026-10-21 for the colleague's final version · **Folder:**
[`delivered/`](delivered/) · **Comparison:** [`comparison.md`](comparison.md) · **Index:** [`README.md`](README.md)

What the two bodies of work consist of, file by file. §1 is the colleague's folder, §2 this repository,
§3 how the two line up. The final version replaced the first delivery in full; the earlier files remain in
git history. Nothing in `delivered/` was modified, renamed or re-run; the files were only sorted into
`tables/`, `figures/` and `data/`. Contents were read from the saved notebook outputs and the workbooks as
delivered.

---

## 1. `delivered/` — the colleague's backtest

Ten files, 4.4 MB, dated 2026-10-19 to 2026-10-20. One notebook produced everything; the other nine files
are its exports. The notebook was run on Windows (Python 3.14.8, yfinance 1.7.0) and its output paths point
to a local folder named *"10 assets, 5 year dataset with 3 year testing and 2 year rolling window"*. That
folder name is the design.

### 1.1 Files

| File | Type | Size | Produced by | What it is |
| --- | --- | --- | --- | --- |
| `Backtesting_Implementation.ipynb` | Jupyter notebook | 1.7 MB | — | The whole implementation: download and snapshot, nine strategies, sampler, backtest loop, metrics (mean and median), win rates, fee grid, charts. 38 cells (17 code, 21 markdown). Outputs saved, three figures embedded |
| `data/Data_Utilized.xlsx` | Workbook, 3 sheets | 1.5 MB | Cell 3 | The data snapshot: download timestamp, adjusted closes of the 25 assets, and the S&P 500 index. 4,211 sessions, 2010-01-04 to 2026-09-30, no missing values. Cell 5 reads it back |
| `tables/portfolio_backtest_summary.xlsx` | Workbook, 10 sheets | 32 KB | Cell 29 | Mean and median metrics per strategy for each scenario, the S&P 500 row, fee sensitivity of annual and cumulative return, turnover |
| `tables/Table Testing Fees.xlsx` | Workbook, 1 sheet | 27 KB | Hand-made from the above | The annual-return fee table, a pivot of the cost at each fee level, and a colour legend ("Gain / Stay the same / Lost with rebalancing"). The presentation version |
| `tables/strategy_comparison_analysis(No Rebalancing).xlsx` | Workbook, 53 sheets | 104 KB | Cell 23 | Paired win rates and per-asset and per-period breakdowns, buy-and-hold scenario |
| `tables/strategy_comparison_analysis(Rebalancing with Fees).xlsx` | Workbook, 53 sheets | 104 KB | Cell 25 | The same for quarterly rebalancing at 15 bp |
| `figures/Median Sharpe Ratio and Max Drawdown.png` | Figure, 2180×991 | 100 KB | Cell 31 | Horizontal bars: median Sharpe and median max drawdown per strategy, three scenarios, S&P 500 as a black bar |
| `figures/Sharpe Ratio Distributions across runs.png` | Figure, 2580×993 | 148 KB | Cell 32 | Box plots of Sharpe across the 100 runs, one panel per scenario, sorted by median, S&P 500 in black |
| `figures/Cumulative Returns and Drawdown Evolution on Run 3.png` | Figure, 2480×1189 | 804 KB | Cell 35 | Wealth and drawdown paths of all nine strategies plus the S&P 500 for run 3, three scenarios (2×3 grid) |
| `figures/Weight Evolution Maximum Decorrelation Run 3.png` | Figure, 1782×680 | 52 KB | Cell 37 | Stacked MDC weight bars every 20 sessions, run 3. Not embedded in the notebook (exported by hand) |

### 1.2 Notebook, cell by cell

| Cells | Section | Content |
| --- | --- | --- |
| 0–1 | Setup | Imports, yfinance version. Comments state the conventions: risk-free = 0, ×252 annualisation, forward fill (with a note on why not interpolation), and an open question: *"Survivorship bias ????"*. Hard-coded Windows `file_path` |
| 2–3 | Loading data | 25 symbols via `yfinance`, 2010-01-01 to 2026-10-01 (exclusive), `Adj Close`, missing values printed before and after a forward fill of up to 2 days. Benchmark `^GSPC`. Writes `Data_Utilized.xlsx` with a timestamp. Run once; skip on later runs |
| 4–5 | Loading data from Excel | Reads prices and benchmark back from `Data_Utilized.xlsx` |
| 6–8 | Portfolio definitions | Nine weight functions plus the `portfolios` dict |
| 9–11 | Sampler | Seed 1904; 100 datasets of 5 × 252 sessions, 10 assets drawn uniformly from 25 |
| 12–13 | Backtest | `backtest_with_drift`, then three scenarios × nine strategies × 100 datasets |
| 14–17 | Performance | `performance_metrics` (14 metrics, partly via `quantstats`; drawdown peak floored at 1), `stat_performance_metrics` for mean or median across runs, six tables plus the S&P 500 (mean and median). Written conclusions (cell 17) |
| 18–19 | Turnover | Annualised two-way turnover, mean and median |
| 20–21 | Diagnostics | Daily win rate, skew, kurtosis, VaR per strategy |
| 22–25 | Win rates and breakdowns | Paired win rates against 1/N, Quintile and the S&P 500 on eight metrics (adds median calendar-year return); per-asset and per-start-year tables; Excel export |
| 26–27 | Fee sensitivity | Quarterly backtest re-run at 5, 10, 15, 20, 30, 40 and 50 bp (≈ 2.9 min each); tables on medians |
| 28–29 | Save tables | `portfolio_backtest_summary.xlsx` |
| 30–33 | Charts | Bar chart (medians) and box plots; written conclusions on outliers (cell 33) |
| 34–37 | Example run | Wealth and drawdown paths and MDC weight evolution, both on run 3 |

### 1.3 Workbook sheets

**`data/Data_Utilized.xlsx`**

| Sheet | Rows × cols | Content |
| --- | --- | --- |
| Download Date-Time Info | 1 × 1 | 2026-10-18 17:17:48 (the notebook output prints 2026-10-19 00:36; comparison §11, item 9) |
| Data_Portfolio-Adj Closed Price | 4,211 × 25 | Adjusted closes of the 25 assets |
| Data_SP500-Adj Closed Price | 4,211 × 1 | `^GSPC` adjusted close, which for an index is the price level (no dividends) |

**`tables/portfolio_backtest_summary.xlsx`**

| Sheet | Rows × cols | Content |
| --- | --- | --- |
| Mean Stats-No Rebalancing | 9 × 14 | Mean across 100 runs: average annual return, cumulative return, volatility, Sharpe, Sortino, Calmar, Sterling, average and max drawdown, daily win rate, skew, kurtosis, VaR 95%, CVaR 95% |
| Mean Stats-Quarterly 0bps | 9 × 14 | Same, quarterly rebalancing, no costs |
| Mean Stats-Quarterly 15.0bps | 9 × 14 | Same, quarterly at 15 bp |
| Median Stats-… (three sheets) | 9 × 14 each | The same three scenarios, medians across runs |
| SP500 Benchmark | 2 × 8 | Mean and median across the 100 windows for `^GSPC` buy-and-hold |
| Test Fees - Returns | 9 × 16 | Median annual return: no rebalancing, 0 bp, and 5–50 bp, plus the cost at each level |
| Test Fees - Cumulative Returns | 9 × 16 | The same for median cumulative return, return and cost columns interleaved |
| Turnover | 9 × 4 | Annualised two-way turnover, mean and median, no rebalancing vs quarterly |

**`strategy_comparison_analysis(…).xlsx`** (both files share this layout, 53 sheets):

| Sheets | Count | Content |
| --- | --- | --- |
| Win Rate vs 1N / vs Quintile / vs SP500 ETF | 3 | Share of the 100 runs in which each strategy beats the benchmark in the same run, on average and median annual return, volatility, Sharpe, Sortino, Calmar, Sterling and max drawdown |
| Stocks vs {1N, Q, ETF} {strategy} | 25 | Per asset: runs that hold it, Sharpe win rate with and without it, mean Sharpe difference with and without it. Assets in fewer than 5 runs are dropped |
| Periods vs {1N, Q, ETF} {strategy} | 25 | Per out-of-sample start year (2012–2023): runs, wins, win rate, mean and median Sharpe difference |

Sheet names are cut to Excel's 31 characters, so some end mid-word (`Periods vs 1N Inverse Volatilit`). The
"SP500 ETF" sheets compare against `^GSPC`, the price index.

### 1.4 What is not in the folder

- No environment file. The notebook needs `quantstats`, `riskparityportfolio`, `tqdm` and `openpyxl`, none
  of which is in this repo's `pyproject.toml`. `file_path` is hard-coded to the colleague's Windows folder.
- No stylised-facts or data-description work. The folder covers the backtest only (comparison §3).

### 1.5 Changes from the first delivery

The final version replaced every file. In short (full list in comparison §2):

- **New:** `data/Data_Utilized.xlsx` (data snapshot) and `tables/Table Testing Fees.xlsx` (replaces the
  hand-edited copy of the summary workbook).
- **Renamed by the colleague:** the bar chart is now *Median Sharpe Ratio and Max Drawdown* (it plots
  medians), and the weight chart *Weight Evolution Maximum Decorrelation Run 3* (title now matches the code).
- **Notebook:** two cells added (load from Excel); gold and silver via `GLD`/`SLV`; data to 2026-09-30;
  benchmark `^GSPC`; medians alongside means everywhere; drawdown peak floored at 1; sheet names follow
  `FEES`. Written conclusions unchanged.
- **Summary workbook:** 6 sheets became 10 (median sheets and the S&P 500 sheet added).
- **Win-rate workbooks:** one metric added (median annual return); period sheets now run to 2023 starts.

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
| `notebooks/01_investment_universe.ipynb` | Workstream A: Tables 1.1–1.3, A1.1–A1.3, Figures 1.1–1.2 |
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
| 1 — universe, data, returns treatment | `01_investment_universe`, report §2 | Download cells and data snapshot; no documentation |
| 1 — stylised facts | `02_stylised_facts`, report §3 | — |
| 2 — strategies | `04_strategies` | Cell 8 (plus an extra Quintile strategy) |
| Methodology — backtest design | `03_backtest_engine`, `05_experiments` | Cells 11 and 13 |
| Evaluate performance | `06_performance` | Cells 16–21, 31–32, `portfolio_backtest_summary.xlsx` |
| Period and subset dependence | `07_robustness` (F2–F4) | Cells 23 and 25, the two 53-sheet workbooks |
| Costs, less favourable assumptions | `07_robustness` (F1, 2× costs) | Cell 27 (5–50 bp grid) |
| Concentration, limitations | `07_robustness` (F5–F6) | — |
| Rebalancing policy (optional extension F) | — | No-rebalancing vs quarterly scenario throughout |
| Recommendation, report | Not started (G) | Short written conclusions in cells 17 and 33 |
