# Plan — report §5, Robustness checks and limitations

**Drafted:** 2026-10-22 · **Report snapshot:** [`group-report.pdf`](group-report.pdf) (2026-10-21) ·
**Evidence:** the colleague's final backtest, [`replication/delivered/`](../../../replication/delivered/)
(2026-10-20; cell map in [`replication/inventory.md`](../../../replication/inventory.md) §1.2) ·
**Index:** [`README.md`](README.md)

How §5 will be filled. §§1–4 are the plan, built only on the colleague's code and outputs. The three
sections after it are kept apart on purpose:

- **§5 Opportunities:** additions inspired by this repo's workstream F that the colleague's work does not
  surface. Not part of the plan unless the group adopts them.
- **§6 Support gaps:** where the colleague's auxiliary tables do *not* fully support what §5 has to say.
- **§7 Possible contradictions:** statements elsewhere in the report that §5 could contradict, and how to
  handle each.

All numbers below were read from the delivered workbooks. "Quarterly" means quarterly rebalancing at 15 bp
(the report's main scenario); "buy-and-hold" means the no-rebalancing scenario. Win rates are the share of
the 100 runs in which a strategy beats 1/N on Sharpe in the same run.

---

## 1. What §5 must cover

| Requirement | Source | Covered by |
| --- | --- | --- |
| Test whether rankings change under less favourable cost assumptions | Brief, *Backtesting design* | §2.1 |
| Show whether conclusions depend on the sampled period or asset subset | Brief, *Evaluate performance* | §2.3, §2.4 |
| Overlapping windows are not 100 independent tests | Brief, *Evaluate performance* | §2.6, §3 |
| Document optimisation failures; do not silently remove runs | Brief, *Backtesting design* | §3 (item 8) |
| Discuss survivorship bias and reliance on today's universe | Brief, *Backtesting design* | §3 (item 3) |
| Sensitivity to periods, market conditions, costs, rebalancing frequency, parameters, alternative specifications; **checks completed vs checks not performed** | Report template, §5.1 | §2.0, §2.1–2.5 |
| Sample size, dependence, selection bias, multiple testing, model risk, capacity, liquidity, benchmark comparability; how each affects confidence | Report template, §5.2 | §3 |

## 2. §5.1 Robustness checks — planned content

Keep the skeleton's shape (one bold lead-in bullet per check, then an overall sentence), but give each check
a short paragraph, because each now has real numbers. Main text about 1.5 pages. Full tables go to
Appendix D. Proposed exhibits are numbered 10–12, after Table 9 (§4.1.7); renumber when the report's
numbering is fixed.

### 2.0 Opening paragraph and Table 10: checks completed vs not performed

One paragraph: every check reuses the same 100 runs (seed 1904, same dates and subsets for every strategy),
so the checks are **paired and descriptive, not independent tests** (links to §3.4 and §5.2).

**Table 10 — Robustness checks.** Rows: transaction costs (5–50 bp; done), rebalancing policy (buy-and-hold
vs quarterly; done), sample period (out-of-sample start year; done), asset subset (each asset held vs not;
done), reference benchmark (1/N, Quintile, S&P 500; done), risk aversion φ (not performed), estimation
window length (not performed), risk-free rate (not performed), covariance shrinkage (not performed),
monthly or threshold rebalancing (not performed). The template asks for this split explicitly. The
"not performed" rows feed §5.2 and §6.

### 2.1 Transaction costs

- **Evidence:** `Table Testing Fees.xlsx`, and the *Test Fees - Returns* sheet of
  `portfolio_backtest_summary.xlsx` (median annual return at 0, 5, 10, 15, 20, 30, 40, 50 bp).
- **Finding:** the return ranking is identical from 0 to 50 bp. Cost at 50 bp (pp per year): Markowitz
  1.49, Quintile 1.27, Max Sharpe 1.25; GMVP 0.43, MDC 0.44, MDP 0.39; risk parity 0.30, inverse volatility
  and 1/N 0.28. The costs scale with turnover (quarterly mean: Markowitz 240%, Quintile 219%, Max Sharpe
  189%, against 26–27% for 1/N, IV and ERC).
- **Derived, no new code:** costs are linear in the fee, so a break-even fee can be stated. Markowitz's
  4.6 pp median-return lead over 1/N at 0 bp shrinks by about 0.024 pp per bp, so it would vanish only
  near 190 bp. This answers §3.4's "break-even fee" promise. Label it as a linear extrapolation.
- **Draft sentence:** "Raising the cost from 5 to 50 basis points per unit of turnover leaves the return
  ranking unchanged. The three high-turnover strategies lose 1.2–1.5 percentage points a year at 50 bp, the
  others at most 0.44."
- **Caveat:** the ranking is on return only. See §6, item 1, before saying anything about Sharpe.

### 2.2 Rebalancing policy (buy-and-hold vs quarterly)

- **Evidence:** median and mean stats sheets for both scenarios; turnover sheet; the two
  `strategy_comparison_analysis` workbooks.
- **Finding:** rebalancing helps 1/N, IV and MDC (median Sharpe +0.03) and hurts the return-driven
  strategies most. Median Sharpe, buy-and-hold vs quarterly: Markowitz 0.83 vs 0.67, Max Sharpe 0.83 vs
  0.65, Quintile 0.83 vs 0.72. ERC, MDP and GMVP are slightly *lower* with rebalancing (−0.01 to −0.03).
  Re-estimating expected returns every quarter costs those strategies more than it adds, even before fees.
- **The core conclusions survive the policy change.** Under buy-and-hold, no strategy beats 1/N on Sharpe
  in a clear majority either (highest: MDC 56%, MDP 53%). IV and ERC have lower volatility than 1/N in 100%
  of runs under both policies, and shallower drawdowns in 81–86% under buy-and-hold.
- **Ties to:** §4.1.7 (estimation error in expected returns) and the brief's optional extension F.

### 2.3 Sample period

- **Evidence:** *Periods vs 1N …* sheets (out-of-sample start years 2012–2023, 5–15 runs per year).
  Present them **grouped**, because single years are too thin:

  **Table 11 — Share of runs beating 1/N on Sharpe, by out-of-sample start (quarterly, 15 bp)**

  | Start | Runs | MV | GMVP | MSR | IV | ERC | MDP | MDC | Quintile |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | 2012–16 | 29 | 17% | 24% | 14% | 34% | 28% | 38% | 55% | 24% |
  | 2017–18 | 22 | 64% | 59% | 68% | 73% | 91% | 77% | 73% | 64% |
  | 2019–21 | 34 | 26% | 26% | 15% | 41% | 35% | 38% | 38% | 24% |
  | 2022–23 | 15 | 7% | 40% | 20% | 40% | 33% | 27% | 20% | 20% |

- **Finding:** conclusions depend on the period. 2017–18 starts are the only group in which every strategy
  beats 1/N in a majority of runs. Their evaluation windows (2017–2021) contain the 2020 crash after a calm
  estimation period. In every other group, no strategy beats 1/N in a majority, except MDC at 55% in
  2012–16 (barely above half). After 2022 the return-driven strategies fail most clearly (Markowitz
  7%), during the rate shock and the concentrated equity rally that followed.
- **No noise yardstick in the prose** (decided 2026-10-22): a binomial standard error assumes independent
  runs, which these are not, and the colleague's code computes none. Groups are described by size and
  read with caution instead.
- **Draft sentence:** "Whether any strategy beats the equally weighted portfolio depends on the period. In
  the 22 runs starting in 2017–18, every strategy beat it in most runs, risk parity in 91%. In the other 78
  runs, none did so convincingly."
- Full per-year table (all strategies, both policies, also vs Quintile and S&P 500) goes to Appendix D.

### 2.4 Asset subset

- **Evidence:** *Stocks vs 1N …* sheets. Each asset is held in 33–49 of the 100 runs, which matches §2.3's
  statement.
- **Finding:** one asset stands out. Holding **gold (GLD)** raises the Sharpe win rate against 1/N by
  +0.24 to +0.42 for GMVP, IV, ERC, MDP and MDC (ERC: 62% with gold, 33% without). **JPM** also helps GMVP, IV, ERC and
  MDP (+0.16 to +0.28). Holding **Treasuries (TLT)** does *not* help: −0.10 to −0.19 for
  ERC, MDP and MDC. The same assets lead under buy-and-hold. Most other asset effects are within noise.
- **No noise yardstick** (as in §2.3). Gold is singled out because it is the largest and most consistent
  effect: largest positive difference for four of five risk-based strategies, positive for all five under
  both policies.
- **Exhibit:** **Table 12 — Assets with the largest effect on the win rate vs 1/N**: GLD, JPM, TLT, VNQ,
  PEP, ABT, for the risk-based strategies. The full 25 × 8 grid goes to Appendix D.
- **Interacts with** the correlation appendix (see §7, item 6).

### 2.5 Reference benchmark

- **Evidence:** *Win Rate vs Quintile* and *Win Rate vs SP500 ETF* sheets.
- **Finding:** the reading does not depend on using 1/N as the reference. Against Quintile, every
  risk-based strategy wins on Sharpe in 54–66% of runs (1/N in 68%). Against the S&P 500, 1/N, IV, ERC,
  MDP and MDC win in 65–76% of runs, but this comparison is flattered (§6, item 3) and should carry the
  caveat in the same sentence.

### 2.6 Overall statement

Close §5.1 with a short paragraph listing what holds and what does not:

1. **Holds under every check run:** no strategy beats 1/N on Sharpe in a clear majority of runs (best 48%
   quarterly, 56% buy-and-hold). IV and ERC carry lower volatility than 1/N in 100% of runs. The
   return-driven strategies (Markowitz, Max Sharpe, Quintile) are the most cost-sensitive and lose to 1/N
   in most start periods.
2. **Depends on the check:** whether any strategy beats 1/N depends on the period (2017–18) and on holding
   gold. Rebalancing helps 1/N, IV and MDC and hurts the return-driven strategies.

## 3. §5.2 Limitations — planned content

The existing seven bullets stay, tightened. Each bullet should name the **direction** of the bias and what
it does to confidence (template: "explain how each limitation affects confidence"). Additions marked *new*.

1. **Historical evidence:** keep. Add that the evaluation years start in 2012, so 2008 is outside the sample.
2. **Overlapping experiments:** keep, and quantify. The 100 runs are 5-year blocks from a 16.7-year panel,
   with 3-year evaluations. Neighbouring runs share up to most of their evaluation period. Every share in
   §5.1 is therefore descriptive. Say plainly that no test treats the runs as independent (and see §7,
   item 4).
3. **Survivorship and hindsight:** keep. Direction: flatters all strategies; untested which most (§6,
   item 9).
4. **Universe composition:** keep (84% shares, one bond ETF). *New:* the uniform draw means some runs hold
   no defensive asset, so composition varies between runs and is mixed into the strategy comparison.
5. **Simplified costs:** keep. Direction: understates costs for the high-turnover strategies, so it favours
   them. §5.1 shows that even 50 bp leaves the ranking unchanged.
6. **Estimation choices:** keep, but soften "likely to disadvantage" for shrinkage, since it was not tested.
   Name what is fixed: φ = 1, 2-year rolling window, quarterly rebalancing, r_f = 0.
7. **Long-only constraint:** keep.
8. *New* — **Optimisation failures:** every optimiser stops the run on failure, and all runs completed, so
   no failure occurred and no run was removed. But the code would not have logged one (brief: "do not
   silently remove").
9. *New* — **Risk-free rate set to zero:** raises every Sharpe and Sortino and turns Max Sharpe into a
   return-over-volatility portfolio. Lower-volatility strategies would lose more Sharpe under a positive rate
   (§6, item 2).
10. *New* — **Benchmark comparability:** the S&P 500 series is the price index without dividends, so it
    understates the benchmark by about the dividend yield, 1.5–2% a year. The index is not investable; an
    ETF would also carry fees.
11. *New* — **Multiple comparisons:** 9 strategies × 8 metrics × 3 references × 2 policies, plus per-period
    and per-asset splits, with no correction. Read isolated large cells with caution.
12. *New* — **Design departure from the brief:** 5-year datasets with 3-year evaluation, where the brief
    suggests 3-year datasets with a 1-year evaluation. Longer evaluations blend crash and recovery in one
    window and overlap more (§6, item 6).
13. *New, short* — **Capacity and liquidity:** all assets are large US listings, so neither binds at the
    sizes implied. One sentence.

## 4. Style and sequence

- **Language:** match the report: British spelling (*stylised*, *analyse*), "the group" or "we"
  (the report mixes both; prefer "we", as in §4.1), bold lead-in bullets, numbers with the period and
  scenario they refer to, and figures quoted to the same precision as §4.3 (Sharpe to two decimals,
  shares as whole percentages).
- **Conventions:** say once, at the top of §5.1, that §5 uses medians and paired win rates (the brief's
  convention), while §4.3 currently reports means (§7, item 3).
- **Steps:**
  1. Draft §5.1 from §2 above and §5.2 from §3, with Tables 10–12.
  2. Move the per-year and per-asset grids to Appendix D.
  3. Resolve §6 items 1–3 with the colleague or caveat them.
  4. Check every §7 item against the then-current §1, §3.4 and §4.3 before submitting.

---

## 5. Opportunities (from this repository's workstream F; not in the colleague's work)

Ideas from our own robustness work that the colleague's implementation does not surface. Each needs either
a change to the colleague's notebook or a clearly labelled result from this repo. None is required to fill
§5.

| # | Opportunity | What it would add | Source in this repo | Effort on the colleague's code |
| --- | --- | --- | --- | --- |
| O1 | **Sharpe at every fee level** | The cost check on risk-adjusted rank, not just return (closes §6, item 1) | Table 5.1 (rank at 1× and 2×) | Export only: `metrics_by_fee` already holds every metric (cell 27) |
| O2 | **Where the crisis falls** (evaluation vs estimation only vs neither) | Explains the 2017–18 result instead of naming it. Ours: optimisers gain on EW when March 2020 is in the evaluation period and lose when it is only in the estimation data | Table 5.2, Figure 5.1 | Needs run dates; small code change. With 3-year evaluations the split is coarser |
| O3 | **Composition split** (defensive asset held or not; number of sectors) | Meaningful in *their* design because the draw is uniform. We dropped it because our two-per-sector draw makes it constant | Plan F3/F4 history | Needs per-run subsets; small code change |
| O4 | **Near-collinear pair** (correlation above 0.85 in the estimation window), re-checked within crash-free windows | Tests the correlation appendix's claim about two banks directly | Table 5.2, lessons §9 | Small code change |
| O5 | **Concentration**: max weight and effective number of assets per strategy | Supports the report's "most concentrated" claims (§6, item 10) | Table 5.3 | Weights are computed but not stored; small change |
| O6 | **Measured direction of survivorship and tax bias**: capital in later index-beaters, distribution yield, vs EW | Turns limitation 3 from assertion into evidence | Table A5.2 | Needs weights (as O5) |
| O7 | **Risk-free rate from `^IRX`** | Shows whether the top-tier order survives a positive r_f (§6, item 2) | `src/config.py`, definitions §2 | One extra download and the `rf` argument |
| O8 | **Total-return benchmark** (`SPY` adjusted or `^SP500TR`) | Fixes the flattered "beats the S&P 500" rates (§6, item 3) | Definitions §2 | One ticker change |
| O9 | **Covariance shrinkage** (Ledoit–Wolf) and **φ sensitivity** | Two "not performed" rows of Table 10 become performed | `strategies.py` switch; workstream D | New runs |
| O10 | **Monthly and threshold rebalancing** | Completes the brief's extension F, of which buy-and-hold vs quarterly is half | — (not in ours either) | New runs |
| O11 | **Independent replication as a robustness result** | Two implementations, different windows, r_f, costs and subset rules, same paired conclusions (15 of 21 cells within 5 pp) | [`replication/comparison.md`](../../../replication/comparison.md) §10.1 | None; cite this repo, labelled |
| O12 | **Noise-yardstick discipline**: count cells beyond ±2 SE against the 5% expected by chance | Makes §5.1's period and asset reading defensible | Lessons §9, workstream F | None; arithmetic on the delivered counts |

O1, O7 and O8 are the cheapest and close the three largest gaps in §6. O11 and O12 cost nothing.

---

## 6. Support gaps: where the auxiliary tables do not fully carry §5

The working hypothesis is that the colleague's auxiliary tables suffice for §5. They mostly do. They fall
short in these places, ordered by how much they matter.

| # | Needed for | What the tables give | Gap | Consequence for the text |
| --- | --- | --- | --- | --- |
| 1 | Ranking under less favourable costs | Return and cumulative return at 0–50 bp | **No Sharpe or drawdown at higher fees.** The top tier is separated by 0.004–0.03 of median Sharpe. A rough estimate (cost ÷ volatility) puts the Sharpe drag at 50 bp near 0.02 for 1/N and IV and 0.03 for MDC, enough to reorder the top tier | Say "the **return** ranking is unchanged". Do not claim the risk-adjusted ranking is unchanged without O1 |
| 2 | Risk-free assumption | r_f = 0 only | **No sensitivity.** With bills averaging roughly 1.5–2% over the evaluation years, a positive r_f takes about 0.11–0.14 off 1/N's Sharpe and 0.13–0.17 off ERC's, which would remove ERC's 0.025 median lead | Do not rank within the top tier on Sharpe. Treat it as a tie, as §4.3 already does |
| 3 | Benchmark comparability | `^GSPC` price index, labelled ETF | **No dividends.** The "beats the S&P 500" rates (65–76% for the top tier) are overstated | Caveat in the same sentence, or fix with O8 |
| 4 | Rebalancing frequency | Buy-and-hold and quarterly | **No monthly or threshold policy.** The template, §1.3 and the §5.1 skeleton mention monthly | Report "buy-and-hold vs quarterly" only; list monthly under "not performed" |
| 5 | Parameter sensitivity | One φ, one window, no shrinkage | **No parameter check at all** | Table 10 "not performed" rows; §5.2 item 6 |
| 6 | Attributing period effects to events | Grouped by out-of-sample start year | **3-year evaluations overlap the groups.** A 2019 start contains both 2020 and 2022, so the tables cannot separate the crash from the rate shock. No correlation output, so the skeleton's stock–bond correlation claim (`[−0.24]` to `[+0.30]`) has no source | Describe the groups by start year, not by event. Drop or source the correlation numbers |
| 7 | Period groups large enough to read | 5–15 runs per year | **Thin cells** (5–15 runs per year; 15–34 per group) | Group the years (Table 11); full table to the appendix only |
| 8 | Subset effects separated from period effects | Per-asset with vs without | **No per-run subsets**, so composition (O3), collinearity (O4) and within-period re-checks cannot be done | Report per-asset effects as associations; name gold as the only robust one |
| 9 | Direction of survivorship bias | Nothing | **Qualitative only** | Keep §5.2 item 3 as a stated direction, not a measured one |
| 10 | Concentration claims | One weight chart (MDC, run 3) | **No concentration measure**, yet §1.2 and §3.2 call MV and MSR "the most concentrated" | Support it with turnover (which the tables do show) or add O5 |
| 11 | Inference | Counts and shares | **No bootstrap, Wilcoxon or multiplicity adjustment**, although §3.4 describes them | §5 stays descriptive, and §3.4 must change (§7, item 4) |
| 12 | Dispersion | Sharpe box plots; mean and median only in tables | **No IQR table** for other metrics | Use the box plots for dispersion. Enough for §5 |
| 13 | Volatility and drawdown by period | Period sheets are Sharpe only | **Cannot show** that the lower-volatility result holds in every period, only overall | State the overall 100% and say the period split covers Sharpe only |

---

## 7. Possible contradictions with the rest of the report

Statements elsewhere in the current draft that §5's evidence could contradict. §5 should not silently
disagree: either the other section changes, or §5 interacts with it explicitly.

| # | Where | Current statement | What §5's evidence says | Handling |
| --- | --- | --- | --- | --- |
| 1 | §1.3 | Recommends the Markowitz mean–variance portfolio | Markowitz is the most cost-sensitive strategy, beats 1/N on Sharpe in 29% of runs, fails in 10 of 12 start years and in 93% of 2022–23 runs | **Main conflict.** Raise with the group before §5 is written; §5 cannot be phrased to support it |
| 2 | §1.3; §5.1 skeleton | Investor "rebalances monthly"; "quarterly instead of monthly reduced turnover by [x]%" | Only buy-and-hold vs quarterly was run | Change both to quarterly; drop the monthly bullet |
| 3 | §4.3 | Means; 1/N Sharpe 0.903; best win rate 56% (MDC); MSR 17%; "rebalancing improves the Sharpe ratio of the diversified strategies" | Final version: best win rate 48%, MSR 27%. On medians, rebalancing *lowers* ERC's and MDP's Sharpe slightly | Update §4.3 to the final version first. State the mean/median convention. Phrase rebalancing as "helps 1/N, IV and MDC; hurts the return-driven strategies" |
| 4 | §3.4 | Cluster bootstrap by start year, paired Wilcoxon test, "multiplicity adjustments described above" | None exists in the code | Remove from §3.4, or implement. §5 must not refer to them |
| 5 | §3.3, §3.4, §4.3 | "evaluated on the final year", "1 year of out-of-sample trading", "3-year blocks drawn from the same 15 years" | 5-year datasets, 3-year evaluation, 16.7-year panel | Align all three; §5.2 item 12 states the departure from the brief |
| 6 | Correlation appendix | "The contrast should be largest when a subset includes a true diversifier (GLD or TLT)"; two banks as "the first place to look" for unstable weights | Holds for gold; **not for Treasuries** (ERC/MDP/MDC win less often with TLT). Holding JPM *raises* the risk-based win rates | **Interact, don't contradict.** §5.1 reports that the prediction holds for gold but not Treasuries, and offers a possible reason (the 2022 bond drawdown, and 1/N holding TLT too) as a hypothesis, not a finding |
| 7 | §5.1 skeleton | "Risk-based strategies lost much of their advantage after 2022"; "benefit concentrated in subsets containing Treasuries and gold" | They had little advantage before 2022 either, except in 2017–18 starts. Gold yes, Treasuries no | Rewrite both bullets from §2.3 and §2.4 |
| 8 | §5.2 | "Using sample estimates without shrinkage is likely to disadvantage the optimisation-based strategies" | Not tested | Soften to "may"; list shrinkage as not performed |
| 9 | §1.2 point 5 | "Rankings changed noticeably … [around market stress / in periods of rising rates]" | Consistent: 2017–18 starts favour every strategy over 1/N; 2022–23 starts hurt the return-driven ones | Fill from §2.3, worded by start period (§6, item 6) |
| 10 | §4.3 | "Costs … leave the return ranking unchanged across the 0–50 bps range tested" | Consistent | Keep. §5 must not stretch it to Sharpe (§6, item 1) |
| 11 | §1.2 caveat; §6.1 | Limitations "discussed in Section 6"; "eight portfolio construction strategies" | Limitations are §5.2; nine strategies with Quintile | Fix the cross-reference and the count |
| 12 | §4.3 table | S&P 500 ETF row 14.33%, Sharpe 0.880 (first delivery, EUR-quoted ETF) | Final benchmark is `^GSPC` (median Sharpe 0.71) | Update §4.3; §5 uses the final series with the dividend caveat |
| 13 | §2.3 | Each asset appears in about 33% to 50% of runs | Consistent (33–49) | None |
