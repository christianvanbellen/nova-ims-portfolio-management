# Group work division — draft and reconciliation

**Recorded:** 2026-10-07 · **Compared against:** [`group-project-plan.md`](group-project-plan.md) and
[`project-definitions.md`](project-definitions.md) as of the same date · **Brief:** `project-description.md`

This page keeps the group's draft of how the project splits into parts, and sets it against this
repository's plan. §1 is the draft as the group wrote it. §2 maps each part to the plan's workstreams.
§3 lists every point where the two differ, and §4 lists what the group needs to decide.

---

## 1. The group's draft (verbatim)

Reproduced as received. The only edit is joining lines that the PDF copy had broken in mid-sentence.

> **Part 1a**
> - Choose a few assets, shares, stocks, etf, commodities
> - Download market data for min 15 years until today (state source, extraction date)
> - Explain the selection, shorter histories or missing observations
>
> **Part 1b**
> - Calculate daily, weekly and monthly log returns using adjusted closing prices (if available)
> - Derive weekly and monthly returns from period-end prices or by summing daily log returns
> - Explain how dividends, corporate actions, currencies and trading calendars are treated. Distinguish
>   non-investable indices from investable products that track them
>
> **Part 1c**
> - Select one asset and investigate the following stylised facts at daily, weekly and monthly basis
> - Use suitable charts, descriptive statistics (and where appropriate, statistical tests)
> - Assess whether the evidence supports each feature; do not assume that every feature must hold:
> - Little or no serial correlation in raw returns
> - Non-normal unconditional return distribution and fat tails, particularly at daily frequency
> - Asymmetry in return distribution, including possible negative skewness
> - Volatility clustering, assessed through absolute or squared returns
> - Leverage effects or asymmetric volatility responses to positive and negative returns
> - Conditional non-normality, assessed using standardised residuals from a suitable volatility model
>
> **Part 2**
> - Use daily historical data and a rolling-window, walk-forward backtest to compare the following
>   strategies:
> - Equally weighted portfolio
> - Markowitz mean-variance portfolio
> - Global minimum variance portfolio
> - Maximum sharpe ratio portfolio
> - Inverse-volatility portfolio; risk parity portfolio with equal risk contributions
> - Most diversified portfolio, maximum decorrelation portfolio. Specify objective and
>   shortcomings/constraints of each strategy. For the Markowitz portfolio, state the target return or
>   risk-aversion parameter so that it is distinct from the minimum-variance and maximum Sharpe ratio
>   portfolios. Distinguish inverse-volatility weighting from equal risk contributions when assets are
>   correlated.

---

## 2. How the draft maps to the plan

The draft follows the brief's *Minimum tasks* (sections 1 and 2). The plan is split by workstream and
by output. Status is taken from the definitions changelog (§8).

| Draft part | Plan workstream / tasks | Notebook | Report section | Repo status |
| --- | --- | --- | --- | --- |
| 1a — selection and download | A1–A5, A9 (selection prose) | `01_investment_universe` | 2. Data | **Done** (2026-10-01) |
| 1b — returns and data treatment | A5b, A6, A9 (treatment prose) | `01_investment_universe` | 2. Data | **Done** (Table 1.3 added 2026-10-07) |
| 1c — stylised facts | B1–B14 | `02_stylised_facts` | 3. Stylised facts | **Done** (2026-10-05) |
| 2 — strategies | D1–D12 | `04_strategies` | 4. Methods | Not started |
| 2 — "rolling-window, walk-forward backtest" (one line) | C1–C9 | `03_backtest_engine` | 4. Methods | Not started |
| *Not in the draft* | E1–E10 — experiments and performance | `05_experiments`, `06_performance` | 5. Results | Not started |
| *Not in the draft* | F1–F6 — robustness and limitations | `07_robustness` | 6. Robustness | Not started |
| *Not in the draft* | G1–G6 — report, recommendation, submission | — | 1, 7, appendices | Not started |

Draft prose for Parts 1a–1c already exists in [`report/01_investment_universe.md`](report/01_investment_universe.md)
and [`report/02_stylised_facts.md`](report/02_stylised_facts.md).

---

## 3. Divergences

Ordered by how much they affect the mark. **Gap** means the brief requires something that the draft
leaves out. **Choice** means the draft leaves a decision open and the plan has already made it.
**Wording** means the draft's phrasing differs from the brief in a way that could lead someone to the
wrong output.

### 3.1 Gaps — required by the brief, missing from the draft

| # | Item | Brief | Plan | Why it matters |
| --- | --- | --- | --- | --- |
| G-1 | **Backtesting design.** 100 random three-year windows × asset subsets, fixed seed, 2y estimation / 1y evaluation, trailing 1y refit, quarterly rebalance | *Methodology — Backtesting design* | C1–C2, C9; definitions §7 | The draft reduces it to one line. This is the core of Part 2 and the largest piece of engineering in the project |
| G-2 | **No look-ahead.** Weights use data available at *t* only; trades execute after | Same | C3 (assertion plus a deliberate-leak test) | A leak invalidates every result. Someone has to own it |
| G-3 | **Weight drift and simple-return compounding** | Same | C4; definitions §5 | The draft mentions log returns only. Portfolio returns need **simple** returns |
| G-4 | **Transaction costs, before and after, plus a less favourable cost scenario** | Same | C5, E7, F1; definitions §6 (2× costs) | Explicitly graded. The draft never mentions costs |
| G-5 | **Turnover** | Same | C7, E1–E3 | Required in the results tables |
| G-6 | **Optimisation failures logged, no runs dropped** | Same | C6, E10 (Table A.1) | The brief says "do not silently remove unsuccessful runs" |
| G-7 | **Performance metrics and their conventions.** Annualised return and volatility, Sharpe, max drawdown, Sterling (Sortino and Calmar optional); annualisation, risk-free rate and drawdown denominator defined | *Evaluate performance* | E1–E2 (Table 4.1) | Missing from the draft |
| G-8 | **Summary across 100 experiments.** Medians, dispersion, win rate against EW | Same | E3–E6 | Missing from the draft |
| G-9 | **Period and subset dependence; overlapping windows are not independent** | Same | F2–F4, F6 | Missing from the draft |
| G-10 | **Survivorship bias and reliance on today's universe** | *Backtesting design* | F6 | Missing from the draft |
| G-11 | **Recommendation.** One strategy, a stated investor objective, the evidence, the conditions for reconsidering | *Evaluate performance* | G-section; report §1 and §7 | This is what the brief's purpose statement asks for. It needs an owner |
| G-12 | **Report assembly, consistency pass, reproducibility appendix, submission** | Implicit | G1–G6 | Someone has to merge and submit by 30 October |

**Net effect:** the draft covers roughly the first half of the work. Workstreams C (partly), E, F and G
(the backtest machinery, results, robustness and report) are not assigned to anyone. These are also
the critical path: plan §9 has E as the long pole.

### 3.2 Choices — open in the draft, already decided in the plan

| # | Topic | Draft says | Plan decided | Where |
| --- | --- | --- | --- | --- |
| C-1 | Universe | "a few assets, shares, stocks, etf, commodities" | Six assets: `GC=F`, `GOVT`, `TSM`, `VNQ`, `RNMBY`, `BTC-USD`. Includes a government bond ETF, a REIT ETF and a **cryptoasset**, none of which the draft lists | Definitions §1 |
| C-2 | 15-year minimum | "min 15 years until today" | Panel spans 15 years (from 2011-10-01), but the **six-asset intersection is only 12.0 years** (from 2014-09-17, set by `BTC-USD`); `GOVT` and `RNMBY` are also under 15y. Handled with staggered entry and disclosed | Definitions §3–4 |
| C-3 | Benchmark / index vs investable | Restates the brief's requirement | S&P 500 held outside the universe: `^GSPC` (non-investable index) vs `SPY` (investable tracker). `GC=F` and `BTC-USD` labelled as proxies, with `GLD`/`IAU` and the 2024 spot ETFs as investable counterparts | Definitions §1–2 |
| C-4 | Weekly/monthly construction | "period-end prices **or** summing daily log returns" | **Summing daily log returns**. Weeks end on Friday, months on the last trading day; stylised facts use complete periods only | Definitions §5, changelog 2026-10-05 |
| C-5 | Trading calendar | Restates the requirement | NYSE calendar from `SPY`. `BTC-USD` weekend observations dropped, not aggregated (disclosed as understating its risk) | Definitions §4 |
| C-6 | Stylised-facts asset | "Select one asset" | `TSM` | Definitions §1 |
| C-7 | Markowitz parameter | "state the target return or risk-aversion parameter" | Risk aversion **λ = 3**, fixed before running, checked to give weights distinct from GMV and MSR | Plan D3, D12 |
| C-8 | Constraints | "Specify … constraints" | Long-only, fully invested, no leverage, common to all eight strategies | Definitions §7 |
| C-9 | Risk-free rate | Not mentioned | `^IRX`, 13-week T-bill | Definitions §5 |

If the group wants a different answer on any of these, change [`project-definitions.md`](project-definitions.md)
first. Parts 1a–1c are already built on these choices, so changing C-1, C-2, C-4 or C-6 means re-running
notebooks 01–02 and redrafting report sections 2–3.

### 3.3 Wording — draft and brief differ

| # | Draft | Brief | Consequence |
| --- | --- | --- | --- |
| W-1 | 1c: "Select one **asset**" | "Select one **share**" | Picking gold, BTC or an ETF for the stylised facts would not meet the brief. `TSM` is a share, so the repo complies |
| W-2 | 1c: "(and where appropriate, statistical tests)", in parentheses | "descriptive statistics and, where appropriate, statistical tests" | The parentheses read as optional. The plan treats the tests as core (JB, robust portmanteau, ARCH-LM, GARCH / GJR, residual tests), since each verdict in Table 2.5 needs one |
| W-3 | Part 2 lists IV + ERC and MDP + MDC as one bullet each, so it reads as **six** strategies | Brief items (e) and (f) each name two portfolios | There are **eight** strategies. The plan implements all eight (D1–D8) |
| W-4 | Part 2: "Specify objective and **shortcomings**/constraints" | "Specify each strategy's objective and constraints" | Here the draft asks for **more** than the plan. Table 3.2 (D10) has no shortcomings column. Proposed: add one. It costs little and feeds the trade-off discussion the brief asks for |
| W-5 | 1b: "log returns" only | Log returns for stylised facts; **simple** returns for portfolio compounding | See G-3. The repo already builds both (A6) |

### 3.4 Not a divergence, but missing from the draft

- **Owners.** The draft splits the work into parts but names no person for any part. Plan task G1
  (section owners plus one document owner who merges) is still open.
- **Dates.** The draft has no schedule. The plan's schedule (§9) puts Parts 1a–1c in weeks 1–2, which
  is already met, and leaves weeks 3–5 for the backtest, results and report.
- **Output conventions.** Table and figure formats, strategy and asset ordering, and fixed colours
  (plan §1). Without these, parts written by different people will not fit together.

---

## 4. Decisions for the group

1. **Extend the draft with a Part 3** (or rename the parts) that covers the backtest engine, experiments
   and performance, robustness, and the report, i.e. G-1 to G-12. Proposed split, along plan workstreams:
   - Part 2a — backtest engine (C)
   - Part 2b — eight strategies, including shortcomings (D)
   - Part 3a — experiments and performance (E)
   - Part 3b — robustness and limitations (F)
   - Part 4 — recommendation, report assembly and submission (G)
2. **Assign owners**, by name, to each part, plus one document owner (G1).
3. **Confirm or override** choices C-1 to C-9. In particular, the 12-year intersection (C-2) and the
   open `RNMBY` → `LMT` question (definitions §1).
4. **Treat Parts 1a–1c as done in this repo** and use the remaining time on Parts 2 onwards, unless
   someone is building them independently. If so, say so now, so the two versions do not diverge.
5. **Adopt W-4.** Add a shortcomings column to Table 3.2.

Once decided, record the outcome in the definitions changelog and update this page.
