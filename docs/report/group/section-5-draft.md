# Report §5 — draft prose

**Drafted:** 2026-10-22, from [`section-5-plan.md`](section-5-plan.md) · **Numbers:** the colleague's final
backtest, [`replication/delivered/`](../../../replication/delivered/) (2026-10-20) · Paste-ready for the shared
document. Table numbers 10–14 are provisional. Review comments for the group are at the end.

---

# **5. Robustness Checks and Limitations**
## **5.1 Robustness checks**
This section examines whether the conclusions of Section 4 depend on the assumptions behind them. Every check
reuses the same 100 backtest windows (seed 1904), with the same dates and asset subsets for every strategy,
so each comparison remains paired. Unless stated otherwise, results refer to quarterly rebalancing at
15 bps, and we report medians across windows and the share of windows in which a strategy beats the equally
weighted portfolio (1/N) on the Sharpe ratio. Because the windows overlap, these shares describe the results
rather than test them, and shares computed on small groups of windows should be read with particular
caution. Table 10 lists the checks performed and those that were not.

*Table 10 – Robustness checks performed and not performed*

| **Dimension** | **Check** | **Status** |
| --- | --- | --- |
| Transaction costs | 5, 10, 15, 20, 30, 40 and 50 bps per unit of turnover | Performed |
| Rebalancing policy | Buy-and-hold over the evaluation window vs quarterly rebalancing | Performed |
| Sample period | Results by out-of-sample start year, 2012–2023 | Performed |
| Asset subset | Results with and without each of the 25 assets | Performed |
| Reference benchmark | 1/N, Quintile and S&P 500 | Performed |
| Monthly or threshold rebalancing | — | Not performed |
| Risk aversion φ, estimation window length | — | Not performed |
| Risk-free rate above zero | — | Not performed |
| Covariance shrinkage | — | Not performed |
### **5.1.1 Transaction costs**
*Table 11 – Turnover, annual return and Sharpe ratio at different cost levels (quarterly rebalancing)*

| **Strategy** | **Turnover (p.a.)** | **Return, 0 bps** | **Return, 15 bps** | **Return, 50 bps** | **Cost, 15 bps (pp p.a.)** | **Cost, 50 bps (pp p.a.)** | **Sharpe, 0 bps** | **Sharpe, 15 bps** |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Markowitz | 244% | 18.46% | 18.02% | 16.97% | 0.44 | 1.49 | 0.68 | 0.67 |
| Quintile | 212% | 16.50% | 16.06% | 15.24% | 0.44 | 1.27 | 0.73 | 0.72 |
| 1/N | 25% | 13.86% | 13.77% | 13.58% | 0.08 | 0.28 | 0.89 | 0.89 |
| Inverse Volatility | 25% | 12.38% | 12.30% | 12.10% | 0.09 | 0.28 | 0.89 | 0.88 |
| Max Decorrelation | 55% | 11.87% | 11.74% | 11.44% | 0.13 | 0.44 | 0.92 | 0.91 |
| Risk Parity | 26% | 11.23% | 11.14% | 10.93% | 0.09 | 0.30 | 0.92 | 0.91 |
| Most Diversified | 53% | 10.71% | 10.59% | 10.32% | 0.12 | 0.39 | 0.91 | 0.90 |
| Max Sharpe | 190% | 10.66% | 10.29% | 9.41% | 0.38 | 1.25 | 0.68 | 0.65 |
| GMVP | 55% | 9.02% | 8.89% | 8.59% | 0.13 | 0.43 | 0.80 | 0.79 |
*Note: medians across the 100 windows. Return is each window's average annual return (mean daily return
× 252); cost is the reduction in that return relative to 0 bps. Turnover is annualised two-way turnover
excluding the initial investment. Strategies are sorted by return at 0 bps; the order is the same at every
cost level tested (5, 10, 15, 20, 30, 40 and 50 bps), shown in full in Appendix D. The Sharpe ratio was
not reported above 15 bps.*

The backtest was repeated at seven cost levels between 5 and 50 bps per unit of turnover. Across this
range, the ranking of strategies by annual return (the median across windows of each window's average
annual return) does not change (Table 11). The cost burden follows turnover. Markowitz, Quintile and Max Sharpe,
whose median turnover is 190% to 244% of the portfolio a year, lose 1.25 to 1.49 percentage points of
annual return at 50 bps. The remaining strategies, with turnover of 25% to 55% a year, lose at most 0.44
points, and 1/N, Inverse Volatility and Risk Parity about 0.3 points. Even at 50 bps, the cost to Markowitz
is about a third of its 4.6-point lead over 1/N in median annual return before costs.

Costs are also not the reason the return-driven strategies trail 1/N on a risk-adjusted basis. Without any
costs, their median Sharpe ratios are already well below that of 1/N: 0.68 for Markowitz, 0.68 for Max
Sharpe and 0.73 for Quintile, against 0.89. The cost check covers returns only. The Sharpe ratio was
reported at 0 and 15 bps but not at the higher cost levels, and because the leading strategies differ by
less than 0.03 in median Sharpe at 15 bps, small reorderings among them at higher costs cannot be
excluded.
### **5.1.2 Rebalancing policy**
*Table 12 – Buy-and-hold vs quarterly rebalancing: median Sharpe ratio and share of windows beating 1/N*

| **Strategy** | **Sharpe, buy-and-hold** | **Sharpe, quarterly 0 bps** | **Sharpe, quarterly 15 bps** | **Beats 1/N on Sharpe: B&H** | **Beats 1/N on Sharpe: Q** | **Lower vol. than 1/N: B&H** | **Lower vol. than 1/N: Q** | **Shallower max DD: B&H** | **Shallower max DD: Q** |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Markowitz | 0.83 | 0.68 | 0.67 | 49% | 29% | 0% | 0% | 14% | 12% |
| Quintile | 0.83 | 0.73 | 0.72 | 50% | 32% | 2% | 1% | 12% | 18% |
| 1/N | 0.86 | 0.89 | 0.89 | – | – | – | – | – | – |
| Inverse Volatility | 0.86 | 0.89 | 0.88 | 50% | 46% | 100% | 100% | 86% | 82% |
| Max Decorrelation | 0.88 | 0.92 | 0.91 | 56% | 48% | 69% | 71% | 65% | 67% |
| Risk Parity | 0.93 | 0.92 | 0.91 | 49% | 45% | 100% | 100% | 81% | 78% |
| Most Diversified | 0.92 | 0.91 | 0.90 | 53% | 45% | 82% | 89% | 71% | 69% |
| Max Sharpe | 0.83 | 0.68 | 0.65 | 45% | 27% | 39% | 34% | 42% | 43% |
| GMVP | 0.81 | 0.80 | 0.79 | 40% | 35% | 97% | 100% | 68% | 70% |
*Note: Sharpe ratios are medians across the 100 windows; differences quoted in the text are computed before
rounding. Win shares compare each strategy with 1/N under the same policy, in the same window: B&H =
buy-and-hold (15 bps on the initial purchase only), Q = quarterly rebalancing at 15 bps. Win shares were
not reported for quarterly rebalancing without costs. Strategies in the same order as Table 11.*

In the buy-and-hold scenario, each strategy's weights are set once at the start of the evaluation window
from the preceding two years of data, and then drift with prices for the full three years. Compared with
quarterly rebalancing, this changes the strategies in opposite directions (Table 12). For the return-driven strategies, buy-and-hold is clearly
better: the median Sharpe ratio is 0.83 against 0.67 for Markowitz, 0.83 against 0.65 for Max Sharpe and
0.83 against 0.72 for Quintile. Buy-and-hold remains better when quarterly rebalancing is run without
costs (0.68, 0.68 and 0.73), so the difference does not come from fees. These are the strategies that
re-estimate expected returns at every rebalance, which is consistent with the imprecision of mean
estimates noted in Section 4.1.7, although the backtest does not isolate that cause. For 1/N, Inverse Volatility and Max Decorrelation, quarterly rebalancing raises the
median Sharpe ratio by about 0.03, while for Risk Parity, Most Diversified and GMVP it lowers it by 0.01 to
0.03. Differences of this size are small compared with the gaps between strategy groups.

The main conclusions do not depend on the rebalancing policy. Under buy-and-hold, too, no strategy beats
1/N on the Sharpe ratio in more than 56% of windows (Max Decorrelation; Most Diversified follows at
53%). Inverse Volatility and Risk Parity have lower volatility than 1/N in every
window under both policies, and shallower maximum drawdowns in 86% and 81% of windows under buy-and-hold.
### **5.1.3 Sample period**
*Table 13 – Share of windows in which each strategy beats 1/N on the Sharpe ratio, by out-of-sample start*

| **OOS start** | **Windows** | **Markowitz** | **GMVP** | **Max Sharpe** | **Inverse Volatility** | **Risk Parity** | **Most Diversified** | **Max Decorrelation** | **Quintile** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2012–2016 | 29 | 17% | 24% | 14% | 34% | 28% | 38% | 55% | 24% |
| 2017–2018 | 22 | 64% | 59% | 68% | 73% | 91% | 77% | 73% | 64% |
| 2019–2021 | 34 | 26% | 26% | 15% | 41% | 35% | 38% | 38% | 24% |
| 2022–2023 | 15 | 7% | 40% | 20% | 40% | 33% | 27% | 20% | 20% |
| All | 100 | 29% | 35% | 27% | 46% | 45% | 45% | 48% | 32% |
*Note: quarterly rebalancing, 15 bps. Each window is evaluated over three years from its start. Groups contain
15 to 34 windows, so their shares are less precise than those for all 100 windows. Results by single start
year are reported in Appendix D.*

Whether any strategy beats 1/N depends on the period (Table 13). In the 22 windows whose evaluation starts
in 2017 or 2018, every strategy beats 1/N in a majority of windows, Risk Parity in 91%. This is the only
group in which that happens. In the other 78 windows, no strategy beats 1/N in a majority of windows,
except Max Decorrelation at 55% in 2012–2016. The weakest period for the return-driven strategies is the
most recent one. Among the 15 windows starting in 2022 or 2023, evaluated over 2022 to 2026, Markowitz
beats 1/N in only one. The risk-based strategies win in 20% to 40% of these windows, a range similar to
2012–2016 and 2019–2021.

Windows are grouped by the year in which their evaluation period starts. Because each evaluation period
lasts three years, the groups overlap in calendar time: a window starting in late 2019, for example,
contains both the 2020 crash and the 2022 rise in interest rates. The table therefore
shows that results depend on the period, but it cannot attribute that dependence to a single market event.

A possible reading of this pattern comes from how the assets themselves behaved, measured on the same
price data. By construction, Inverse Volatility, Risk Parity and GMVP give less weight to the most
volatile assets, so they should gain on 1/N when those assets fall hardest and lose when those assets
lead. Across the 25 assets, the more volatile ones (ranked by their volatility over 2015–2016) fell most
in the sell-off of late 2018 and in the 2020 crash, but rose most in 2012–2016, in the rebound from March
2020 and from 2023 onward. The correlation between an asset's volatility and its return is −0.72 and
−0.33 in the two sell-offs, against +0.68, +0.50 and +0.52 in the three rising phases. Evaluation
periods starting in 2017–2018 run to 2020–2021, so most of them span both sell-offs, while those of the
other groups are dominated by the rising phases. After 2022, the defensive assets also lost part of their
protection. Treasuries fell 31% in 2022, and their daily correlation with the 21 shares in the universe,
negative in every year from 2012 to 2021, has been positive since 2022. This reading is descriptive: the
backtest does not record portfolio weights, so it cannot confirm that these episodes drive the results.
### **5.1.4 Asset subset**
*Table 14 – Change in the share of windows beating 1/N on the Sharpe ratio when an asset is held (percentage points)*

| **Asset** | **Windows holding it** | **GMVP** | **Inverse Volatility** | **Risk Parity** | **Most Diversified** | **Max Decorrelation** |
| --- | --- | --- | --- | --- | --- | --- |
| GLD (gold) | 42 | +42 | +36 | +29 | +33 | +24 |
| JPM | 36 | +28 | +19 | +25 | +16 | +3 |
| TLT (Treasuries) | 34 | +9 | +11 | −10 | −10 | −19 |
| VNQ (real estate) | 43 | −21 | −15 | −14 | −1 | +1 |
| ABT | 43 | −8 | −15 | −18 | −26 | −15 |
| PEP | 35 | −23 | −18 | −30 | −34 | −12 |
*Note: share of windows won when the asset is held, minus the share when it is not; quarterly rebalancing,
15 bps. Shown: the two defensive assets (TLT, VNQ) and the assets with the largest effects. All 25 assets
are reported in Appendix D.*

Each asset is held in 33 to 49 of the 100 windows, so no asset dominates the experiment. One asset stands
out (Table 14). When gold is in the subset, all five risk-based strategies beat 1/N noticeably more often:
Risk Parity, for example, wins in 62% of windows that hold gold and in 33% of those that do not. Holding
JPM also helps GMVP, Inverse Volatility and Risk Parity. Treasuries, by contrast, do not help: with TLT in
the subset, Risk Parity, Most Diversified and Max Decorrelation beat 1/N less often. The pattern for gold,
JPM and Treasuries is similar under buy-and-hold.

These effects should be read with care. Each comparison rests on 33 to 49 windows, and with 25 assets and
five strategies some large differences will arise by chance. Gold's effect is both the largest and the most
consistent: it is the largest positive difference for four of the five strategies, and it is positive for
all five under both rebalancing policies. The comparison is an association, not a controlled test: an
asset may simply be held more often in favourable periods. The result for gold is consistent with the
correlation structure in the appendix, where gold is essentially uncorrelated with the rest of the
universe. The result for Treasuries is not what that structure suggests. The backtest does not record
portfolio weights, so it cannot show why; the change in the behaviour of Treasuries after 2022
(Section 5.1.3) is one possible reason.
### **5.1.5 Reference benchmark**
The conclusions do not rest on 1/N as the only reference. Against the Quintile portfolio, every risk-based
strategy wins on the Sharpe ratio in 54% to 66% of windows, and 1/N in 68%. Against the S&P 500, 1/N,
Inverse Volatility, Risk Parity, Most Diversified and Max Decorrelation win in 65% to 76% of windows.
This last comparison overstates their advantage, because the S&P 500 series used is the price index,
which excludes dividends, while the strategies' returns include them (Section 5.2).
### **5.1.6 Summary**
Three conclusions hold under every check for which the results are available. No strategy beats 1/N on
the Sharpe ratio in more than 56% of windows under either rebalancing policy. Inverse Volatility and Risk
Parity deliver lower volatility than 1/N in every window under both policies. The return-driven strategies (Markowitz, Max Sharpe
and Quintile) are the most exposed to costs and lose to 1/N in most periods. Two results depend on the
check. Whether any strategy beats 1/N depends on the sample period, being concentrated in windows starting
in 2017–2018, and on whether gold is in the subset. The effect of rebalancing differs by strategy: it
helps 1/N, Inverse Volatility and Max Decorrelation slightly, and hurts the strategies that rely on
expected returns.
## **5.2 Limitations and residual risks**
The results should be interpreted with the following limitations in mind. Where possible, we state the
direction in which each one is likely to bias the comparison.

- **Historical evidence:** backtests describe past conditions. Our analysis of returns (Section 4.1)
  shows that volatility and correlations change over time, so estimated inputs may not reflect future
  conditions. The evaluation windows start in 2012, so the 2008 financial crisis lies outside the sample.

- **Overlapping experiments:** the 100 windows are five-year blocks drawn from a 16.7-year history, each
  with a three-year evaluation period, so neighbouring windows share much of their evaluation data. They
  are not 100 independent observations, and the shares reported in Sections 4 and 5.1 are descriptive
  rather than formal tests.

- **Design choices relative to the brief:** each window uses two years for estimation and three for
  evaluation, rather than the suggested three-year window with a one-year evaluation. The longer
  evaluation combines crash and recovery in one window, which makes period effects harder to isolate
  (Section 5.1.3) and increases the overlap between windows.

- **Survivorship and hindsight bias:** the universe was selected in 2026 from companies that are
  successful today. This flatters the returns of all strategies, and possibly most those that concentrate
  in past winners. We have not measured how the bias differs between strategies.

- **Universe composition:** 84% of assets are shares and there is only one bond ETF. Because the 10
  assets of each window are drawn at random from all 25, without regard to group, the mix of equity
  sectors and defensive assets varies between windows, and a window can hold no defensive asset at all.
  Differences between strategies therefore partly reflect the composition of each subset. Results may not generalise to a more balanced or international
  universe.

- **Simplified costs:** costs are modelled as a fixed rate per unit of turnover. Market impact, bid–ask
  spreads in stressed markets, taxes and management fees are not included. This understates the cost of
  the high-turnover strategies most, although Section 5.1.1 shows that even 50 bps leaves the return
  ranking unchanged.

- **Risk-free rate:** the risk-free rate is set to zero. This raises every Sharpe and Sortino ratio, by
  more for lower-volatility strategies, and turns the Max Sharpe portfolio into a return-to-volatility
  portfolio. Because a positive rate lowers the Sharpe ratio by more for lower-volatility strategies, it
  could change the order within the leading group, whose median Sharpe ratios lie within 0.03 of each
  other. That order should not be read as meaningful.

- **Estimation choices:** results depend on the 2-year estimation window, the quarterly rebalancing
  frequency and the risk-aversion parameter (φ = 1). These were fixed in advance rather than optimised,
  and were not varied. Sample estimates were used without shrinkage, which may disadvantage the
  optimisation-based strategies.

- **Benchmark comparability:** the S&P 500 series is the price index, which excludes dividends and cannot
  be held directly. It understates the return of an investable S&P 500 fund by the dividend yield, less
  that fund's fees, so comparisons with it favour the strategies, whose returns include dividends.

- **Multiple comparisons:** nine strategies are compared on eight metrics, against three references and
  under two rebalancing policies, and the results are further split by period and asset. No correction for
  multiple comparisons is applied, so isolated large differences, particularly in the period and asset
  splits, should be read with caution.

- **Optimisation failures:** the numerical optimisers (GMVP, Markowitz, Max Sharpe, Most Diversified and
  Max Decorrelation) stop the backtest if they fail to converge, and every portfolio is checked to be
  fully invested. All windows were completed, so no optimisation failed and no window was removed. Risk
  Parity relies on a specialised package whose convergence is not checked separately. A failure would
  have stopped the run rather than been logged and handled within it.

- **Long-only constraint:** excluding short-selling and leverage makes the strategies implementable, but
  it also limits how far the optimisations can depart from simple allocations.

- **Capacity and liquidity:** all assets are large, actively traded US listings, so neither capacity nor
  liquidity is likely to bind at the portfolio sizes an investment committee would consider.

---

## Review comments for the group

Points to raise as comments in the shared document. Each one affects text outside §5, or a number §5
depends on.

1. **§1.3 recommendation vs §5 (decision needed).** §1.3 recommends Markowitz. §5 shows it beats 1/N on
   Sharpe in 29% of windows, in only 1 of 15 windows from 2022, with the highest cost burden, and that it
   does better without rebalancing. The recommendation and §5 cannot both stand.
2. **§4.3 uses the first version of the colleague's results.** Its table, the 56% (Max Decorrelation) and
   17% (Max Sharpe) win rates and the rebalancing bullet predate the final notebook. §5 uses the final
   version (best win rate 48%, Max Sharpe 27%). §4.3 needs updating so the two sections quote the same run.
3. **Means vs medians.** §4.3 reports means; §5 reports medians, as the brief asks. The rebalancing
   conclusion changes with the statistic (on medians, rebalancing slightly lowers the Sharpe ratio of Risk
   Parity and Most Diversified). We should agree on one convention for §4 and §5.
4. **Benchmark is the S&P 500 price index, not an ETF.** The code downloads `^GSPC`, which has no
   dividends. The report calls it an "S&P 500 ETF" throughout. Either rename it, or ask for a re-run on a
   total-return series. §5 currently states the caveat.
5. **§3.4 describes tests the code does not run.** The cluster bootstrap, the Wilcoxon test and the
   "multiplicity adjustments" do not exist in the notebook. §5 is written as descriptive. §3.4 should match,
   or the tests should be added.
6. **Backtest design is described inconsistently.** §3.3 ("final year"), §3.4 ("3-year blocks from 15
   years") and §4.3 ("1 year of out-of-sample trading") disagree with the code: 5-year windows, 2 years of
   estimation and 3 of evaluation, over a 16.7-year history. §5.2 states the actual design.
7. **Monthly rebalancing.** §1.3 assumes an investor who "rebalances monthly". No monthly run exists, and
   §5 tests only buy-and-hold vs quarterly.
8. **Cost check covers returns only.** The fee loop computes Sharpe at every fee level but only exports
   returns. If the colleague can export Sharpe by fee, §5.1.1's last sentence can become a firm statement.
9. **Risk-free rate at zero.** The leading strategies lie within 0.03 of median Sharpe (Risk Parity 0.91,
   1/N 0.89), and a positive rate lowers Sharpe more for lower-volatility strategies. §5 treats the leading
   group as a tie; §4.3 and §1 should not rank within it. A re-run with a T-bill rate would settle it.
10. **Treasuries result vs the correlation appendix.** The appendix expects TLT to make the risk-based
    strategies stand out; §5.1.4 finds the opposite for three of them and leaves the reason open, since the
    backtest does not record weights. The appendix wording may need softening.
11. **Unsourced numbers in the old §5.1 skeleton.** The stock–bond correlation figures ([−0.24] to [+0.30])
    and the "[25] bp" cost level have no source in the code. They were dropped from this draft.
12. **Table numbering.** The report has two "Table 2"s (§3.1.3 and the §4.3 "Tabelle 2"). §5 uses 10–14
    provisionally. Appendix D will need the full per-year and per-asset tables.
13. **Cross-references.** §1.2 points to "Section 6" for limitations (they are §5.2), and §6.1 says "eight"
    strategies (nine with Quintile).
14. **Risk Parity has no convergence check.** The other optimisers stop the run on failure; the Risk Parity
    package's result is used as returned, checked only for full investment. Worth a one-line check by the
    colleague, since §5.2 now states it.
15. **"Fixed in advance" in §5.2.** The existing limitation says the estimation window, rebalancing
    frequency and φ were fixed in advance rather than optimised. The code cannot show this; the group
    should confirm it is true before it stays.
16. **Fee table lacks Sharpe.** Repeats item 8 for the summary: §5.1.6 now claims robustness only "for
    which the results are available", because the win rates exist at 15 bps only.

17. **New figures in §5.1.3's last paragraph come from the colleague's data, not their notebook output.**
    The volatility-return correlations by episode, the 31% Treasuries loss in 2022 and the Treasuries-shares
    correlation by year were computed by us from `Data_Utilized.xlsx` (the colleague's price snapshot). The
    episode dates (19 Feb–23 Mar 2020, end-Sep–24 Dec 2018) are our choice. If the group prefers §5 to quote
    only notebook outputs, the paragraph can stay without the numbers.
