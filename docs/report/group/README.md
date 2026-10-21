# Group report — working draft

The group's shared report, *From Return Patterns to Portfolio Performance*. It is written collaboratively
outside this repository; this folder keeps a snapshot of it so the text can be checked against the
pipeline. **Snapshot of 2026-10-21.**

| File | What it is |
| --- | --- |
| [`group-report.pdf`](group-report.pdf) | The draft as rendered (≈ 30 pages). Use it for layout, tables and figures |
| [`group-report.md`](group-report.md) | The same draft exported to Markdown, so it can be searched and diffed. Two figures are embedded as base64 images (hence 1.3 MB). Some export artefacts: table rows reading `undefined`, run-together headings, missing formulas |

## Ground rules

- **Read-only.** Edits go into the shared document, not here. To update, replace both files with a new
  export under the same names; earlier snapshots stay in git history. Update the date above and the status
  table below.
- **The pipeline is the source of numbers.** Every figure the report states should come from a notebook in
  [`notebooks/`](../../../notebooks/) or, where the group adopts it, from the colleague's backtest in
  [`replication/`](../../../replication/README.md). Our own section drafts are in
  [`docs/report/`](../) (`01_investment_universe.md`, `02_stylised_facts.md`).

## Status of the snapshot

| Section | State | Source of its numbers |
| --- | --- | --- |
| 1 Executive summary, recommendation | Skeleton with placeholders (`[X]%`, `Strategy X`) | — |
| 2 Data | Written | Matches our universe and panel (workstream A). Extraction details are the colleague's (18 Oct, yfinance 1.7.0, stored copy) |
| 3.1 Stylised facts: methods | Written, with leftover template text | — |
| 3.2 Strategy definitions | Written | Colleague's specification (φ = 1, r_f = 0, Quintile) |
| 3.3 Backtest assumptions | One paragraph with placeholders (`[K]`, `[seed]`) | — |
| 3.4 Performance measures, inference | Written | Colleague's metric definitions |
| 4.1 Stylised facts: results | Written, Tables 3–9 | Exxon Mobil (`XOM`); not produced by this repo's notebook 02 |
| 4.2 Strategy performance | Empty | — |
| 4.3 Implications | Written, net-of-cost table | Colleague's **first delivery** (2026-10-16) |
| "Main comparison table" | Template | — |
| 5.1 Robustness | Skeleton with placeholders | — |
| 5.2 Limitations | Written | — |
| 6 Conclusions | Partly written, placeholders | — |
| 7 References | Three lecture-slide entries | — |
| 8 Appendices A–E | Headings only | — |
| Correlation matrix (after §8) | Written, two figures | Our workstream A (Figure 1.2 heatmap) |

## Open issues found in this snapshot

Things to resolve in the shared document before submission. References are to the report's own sections.

1. **Stylised-facts share.** The report analyses `XOM`; this repo's workstream B, definitions and report
   draft use `JPM` (definitions §1, C-6). Both are shares, so either meets the brief, but the group has to
   pick one and the numbers must come from a notebook that the repo can re-run.
2. **§3.1 contradicts itself on the volatility model.** §3.1.4 (Fact 6) says no GARCH-type model is
   estimated and a 60-day rolling volatility is used instead. The summary paragraphs at the end of §3.1,
   §3.1.5 and §6.1 cite GJR-GARCH, GARCH-standardised residuals and a Student-t ν ≈ 7.
3. **Stylised-facts conclusions disagree with §4.1.** §4.1.7 finds four of six facts supported and negative
   skewness *not* supported. The end of §3.1, §1.2 (point 1) and §6.1 say five of six, and that negative
   skewness is present. §3.1.1 and §3.1.2 share a heading.
4. **Part II figures are stale.** The §4.3 table and bullets (1/N Sharpe 0.903, ETF 14.33%, MDC beats 1/N in
   56%, MSR 17%) are from the colleague's first delivery. The final version changes them (1/N mean Sharpe
   0.944, best win rate 48%, MSR 27%) and adds medians, which the brief asks for. See
   [`replication/comparison.md`](../../../replication/comparison.md) §2 and §10.
5. **Backtest design is described three ways.** §3.3 says five-year periods evaluated "on the final year";
   §4.3 says "1 year of out-of-sample trading"; §3.4 says "3-year blocks". The colleague's backtest
   evaluates three years after a two-year estimation window; ours evaluates one year in three-year
   datasets, as the brief states.
6. **Benchmark wording.** The report calls it an "S&P 500 ETF". In the colleague's final version it is the
   S&P 500 price index without dividends (comparison §11, item 4).
7. **Recommendation does not fit its own evidence.** §1.3 recommends mean–variance, but the reasons it gives
   (lower volatility, risk-only estimates) describe a risk-based strategy, and both backtests have MV with
   lower volatility than 1/N in 0–1% of runs. The stated objective says monthly rebalancing; both backtests
   rebalance quarterly.
8. **Inference methods not implemented.** §3.4 describes a cluster bootstrap by start year and a paired
   Wilcoxon test. Neither exists in this repo or in the colleague's notebook.
9. **Counts and cross-references.** §6.1 says eight strategies (the report compares nine with Quintile).
   Section pointers are off: stylised facts are cited as "Section 3", the backtest as "Section 5",
   limitations as "Section 6" (they are §4.1, §4.2–4.3 and §5.2).
10. **Placeholders with numbers from this repo.** The §4.1.7 correlation brackets (`[0.73]`, `[0.38]`,
    `[0.36]`, `[0.16]`) and the §5.1 bullets (cost level, sub-periods, asset subsets) can be filled from
    workstreams A and F. Note that the report's correlation appendix already gives financials at 0.74.
