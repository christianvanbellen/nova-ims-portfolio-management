# Project definitions

**Last updated:** 2026-10-01 · **Source of truth for the brief:** `project-description.md`

What we analyse and under which conventions. The plan and the notebooks assume this page. If something
changes, change it here first and note it in §8.

---

## 1. Investable universe

Six assets, all quoted in **USD on US venues**, so the pipeline needs no currency conversion.

| Ticker | Name | Asset class | Instrument |
| --- | --- | --- | --- |
| `GC=F` | Gold, COMEX continuous front-month | Commodity | Futures proxy |
| `GOVT` | iShares US Treasury Bond ETF | Government bonds | ETF |
| `TSM` | Taiwan Semiconductor | Equity — semiconductors | ADR |
| `VNQ` | Vanguard Real Estate Index Fund ETF | Real estate / REITs | ETF |
| `RNMBY` | Rheinmetall AG | Equity — defence | ADR |
| `BTC-USD` | Bitcoin | Cryptoasset | Spot proxy |

Strategies allocate **only** to these six.

**Stylised-facts share** (the brief asks for one): **`TSM`** — the most liquid single stock in the set.

**Proxy labels the brief requires.** `GC=F` is a futures series, not a holding; the investable
counterpart is `GLD` or `IAU`. `BTC-USD` is a spot rate, not investable through a US product before the
January 2024 spot ETFs. Both are labelled as proxies wherever they appear.

**Open:** `RNMBY` is thinly traded (§3). The team is considering `LMT` as a substitute. Swapping it is a
one-line edit — nothing downstream hardcodes a ticker.

---

## 2. Benchmark — S&P 500

Held **outside** the universe. No strategy may allocate to it.

| Ticker | What it is | Use |
| --- | --- | --- |
| `^GSPC` | S&P 500 price index, **non-investable** | Quoted when describing "the market" |
| `SPY` | SPDR S&P 500 ETF, **investable tracker** | Every performance comparison; also defines the NYSE calendar |

Use `SPY` in performance tables — `^GSPC` excludes dividends and would understate the benchmark.

The brief's *own* benchmark for the 100-experiment comparison is the **equally weighted portfolio** of
the six assets. The S&P 500 is the external reference. Report both; they answer different questions.

---

## 3. Data availability (Yahoo Finance, measured 2026-10-01)

| Ticker | First obs. | Years | Obs./yr | Median volume | ≥15y? |
| --- | --- | --- | --- | --- | --- |
| `TSM` | 1997-10-09 | 29.0 | 251 | 8,937,900 sh | Yes |
| `GC=F` | 2000-08-30 | 26.1 | 251 | 198 contracts | Yes |
| `VNQ` | 2004-09-29 | 22.0 | 252 | 3,207,200 sh | Yes |
| `GOVT` | 2012-02-24 | 14.6 | 252 | 2,650,750 sh | No |
| `RNMBY` | 2012-11-26 | 13.8 | 252 | 1,500 sh | No |
| `BTC-USD` | 2014-09-17 | 12.0 | 365 | — | No |
| `^GSPC` | 1927-12-30 | 98.8 | 251 | — | Yes |
| `SPY` | 1993-01-29 | 33.7 | 252 | 62,709,000 sh | Yes |
| `^IRX` | 1960-01-04 | 66.7 | 250 | — | Yes |

Three consequences to carry into the report:

1. The **six-asset intersection is 12.0 years** (from 2014-09-17), short of the brief's 15-year minimum.
   §4 states how we handle it.
2. `BTC-USD` trades 365 days/year, the rest ~252. §4 resolves the calendar mismatch.
3. `RNMBY` trades ~1,500 shares/day. Thin trading biases measured volatility down, so we test for stale
   prices (share of zero-return days) and disclose the result.

---

## 4. Panel and calendar

| Convention | Decision |
| --- | --- |
| Panel start | `2011-10-01` — 15 years of span, per the brief |
| Panel end | Latest session available at extraction |
| Staggered entry | Assets enter on their own first observation; pre-entry cells stay `NaN`, never zero- or back-filled |
| Full-panel date | `2014-09-17` — first date all six have data; anything needing the complete matrix starts here |
| Sampler rule | A random window is drawn only from dates where every asset **in that drawn subset** has data |
| Trading calendar | NYSE sessions, defined as the dates `SPY` trades; all series reindexed to it |
| `BTC-USD` | Weekend/holiday observations dropped, not aggregated — understates its risk, which we disclose |
| Interior gaps | Forward-fill up to 3 sessions; anything longer is reported, not patched |

The report must state **both** the 15-year span and the 12.0-year six-asset intersection.

---

## 5. Returns and prices

| Item | Decision |
| --- | --- |
| Source | Yahoo Finance via `yfinance`, downloaded live each run; nothing written to disk |
| Prices | `auto_adjust=True` — adjusted for splits and dividends (material for `GOVT` and `VNQ`). Effect quantified in **Table 1.3** against the price-only series. Dividends are reinvested gross of withholding tax; `GC=F` carries no roll adjustment |
| Log returns | `ln(P_t) − ln(P_{t−1})` — all stylised-facts analysis |
| Simple returns | `P_t/P_{t−1} − 1` — all portfolio compounding and performance stats |
| Weekly / monthly | Sum of daily log returns; weeks end Friday, months on the last trading day |
| Currency | All USD, no conversion. FX risk remains inside `TSM` (TWD) and `RNMBY` (EUR) returns and is not separately modelled |
| Risk-free | `^IRX`, 13-week T-bill yield, annualised percent — ÷100 for decimal, ÷252 for daily |
| Annualisation | 252 days. Return ×252, volatility ×√252 |

---

## 6. Transaction costs (proposed)

One-way, in basis points of traded notional, applied to turnover at each rebalance.

| Asset | bp | Why |
| --- | --- | --- |
| `GOVT` | 2 | Tight-spread bond ETF |
| `GC=F` | 2 | Deep futures market |
| `VNQ` | 3 | Large REIT ETF |
| `TSM` | 5 | Liquid ADR |
| `BTC-USD` | 25 | Spread plus exchange fee |
| `RNMBY` | 30 | Thin ADR |

The brief requires results **before and after** costs, plus a re-run at **2×** these figures to test
whether the ranking holds.

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
| Rebalancing | Quarterly — every 63 sessions; opening trade at the close of the last estimation session |
| Execution lag | 1 session — weights formed at close *t*, traded at close *t*+1, earning from *t*+2 |
| Initial portfolio | Bought out of cash; its cost is charged, its 100% turnover is excluded from reported turnover |
| Optimisation failure | Logged; hold the drifted weights (equal weight if none yet); the run is never dropped |
| Subset size | 4 of 6 assets |
| Constraints | Long-only, fully invested, no leverage |
| Trading days/year | 252 |

The seed is fixed now and is not re-rolled after seeing results.

---

## 8. Changelog

| Date | Change |
| --- | --- |
| 2026-10-01 | Initial baseline. Supersedes the earlier seven-asset draft in `notebooks/01_investment_universe.ipynb`. |
| 2026-10-01 | Workstream A complete. The universe, benchmark, calendar and cost conventions above now live in code at `src/config.py`, which every notebook imports — change this page first, then that module. `notebooks/01_investment_universe.ipynb` rebuilt against the six-asset universe and runs clean top-to-bottom. The §3 table is reproduced as **Table 1.1** by `src.data.availability_table`; its volume column is a **full-history** median, which is the basis the figures above use. |
| 2026-10-05 | Workstream B complete. `notebooks/02_stylised_facts.ipynb` runs clean top-to-bottom; statistics, tests, GARCH models and the verdict rules live in `src/stylised.py`, figures in `src/viz.py`. Conventions added: weekly/monthly stylised-facts series use **complete periods only** (first period and any trailing stub dropped); the serial-correlation verdict uses a **heteroskedasticity-robust** portmanteau, since plain Ljung–Box over-rejects under volatility clustering; GARCH models are fitted on percent log returns with a constant mean. Draft prose in `docs/report/02_stylised_facts.md`. |
| 2026-10-07 | Dividend treatment made visible. **Table 1.3** (`src.data.adjustment_table`, notebook 01 §A5b) compares adjusted with price-only returns for the six assets, `SPY` and `^GSPC`; report §2.1–2.2 now cite it. Corrected two claims in the draft: unadjusted `VNQ` still grows ×1.9 (it is `GOVT` that goes backwards), and there are no split or ADR ratio events over the panel. Notebook 01 re-run with extraction date 2026-10-07; report §2 figures refreshed to match. |
| 2026-10-07 | Workstream C complete. `notebooks/03_backtest_engine.ipynb` runs clean top-to-bottom, with all 10 unit tests passing and both deliberate-leak tests raising `LookAheadError`. The sampler, walk-forward loop, cost model and failure log live in `src/backtest.py`. §7 gains the timing conventions the loop fixes: first estimate, one-session execution lag, opening trade from cash, failure fallback. The sampled experiments are reproducible under the seed **and** the extraction date, because the eligible window starts grow with the panel. |
