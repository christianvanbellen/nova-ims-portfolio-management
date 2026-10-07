# 2. Data

*Draft of report section 2. Target ~1.5 pages alongside Tables 1.1–1.3 and Figures 1.1–1.2, with
Tables A1.1–A1.2 in the appendix. Every number is produced by
[`notebooks/01_investment_universe.ipynb`](../../notebooks/01_investment_universe.ipynb).*

---

## 2.1 Source and adjustment

All prices come from **Yahoo Finance** via the `yfinance` package, retrieved on **7 October 2026**.
Nothing is cached: each notebook re-downloads what it needs. The extraction date, quoted once here and
applying throughout, therefore fully determines every number in this report.

Prices are **adjusted closes**, restated for subsequent splits, spin-offs and cash distributions. This
is equivalent to reinvesting each dividend on its ex-date, so every series is a total-return series.
That one switch is the whole of our dividend treatment. Table 1.3 measures what it is worth by setting
each adjusted series against its price-only counterpart on the same dates.

Distributions are material almost everywhere. Every stock except `AMZN` pays a regular dividend, worth
**1.5 to 4.4 points a year**. For the defensive assets, dividends are much of the return: about half of
`VNQ`'s 8.4% a year, over 40% of `XOM`'s and about a third of the consumer-staples names'. **`TLT`'s
entire return is income and more.** The long Treasury fund lost 3.1% a year on price alone, and
distributions bring it back only to −0.3%. A strategy scored on unadjusted prices would be penalised
for holding exactly the income assets. `GLD`, `SLV` and `AMZN` pay nothing, and adjustment leaves them
unchanged.

**Corporate actions.** The panel contains nine split-type adjustments (Table A1.2). Six are ordinary
splits: `AAPL` (twice), `AMZN`, `WMT`, `KO` and `CL`. Three are **spin-offs**: Abbott's of AbbVie
(2013), Pfizer's Upjohn business into Viatris (2020), and Merck's of Organon (2021). Yahoo records
each spin-off as a fractional split ratio. The adjusted series continues as if the spun-off shares were
sold on the ex-date and the proceeds reinvested in the parent. This is the standard total-return
convention, and the only way to keep a single-ticker history continuous. We checked that it worked: on
every event date the adjusted return is an ordinary move of about 2%, not the double-digit drop a
missed adjustment would leave.

As a further screen, we listed every daily move beyond ±15% (Table A1.1). There are 32 such
asset-sessions. Fifteen fall on three days of the March 2020 crash, when up to seven assets crossed
the threshold at once. The rest are single-name news: earnings and guidance shocks at `INTC` and
`UNH`, `ORCL`'s jump in September 2025, and a 34% one-day fall in `SLV` in January 2026 at the top of
a rally. None falls on a corporate-action date, so none is an adjustment artefact. All stay in the
data.

One gap remains: Yahoo reinvests the **gross** dividend, with no allowance for tax. This applies
equally to every asset and to the `SPY` benchmark, so it shifts levels but not comparisons. We use one
vendor and one adjustment method, with no second source to cross-check against (section 6).

## 2.2 Universe, currencies and proxies

The universe has **25 assets in five sector groups of five** (Table 1.1). Four groups are equities:
technology, healthcare, financials and consumer staples. The fifth, *real assets and defensive*, holds
gold (`GLD`), silver (`SLV`), long-duration US Treasuries (`TLT`), US real estate (`VNQ`) and an energy
major (`XOM`). The groups are our own, not a GICS classification: `AMZN` sits in technology, and `XOM`
is a common stock grouped with the four funds. Strategies allocate only to these 25.

All 25 are **US-listed and quoted in USD**, so the pipeline performs no currency conversion and no
return carries a foreign-exchange layer. Foreign-currency exposure enters only indirectly, through the
companies' overseas earnings, and is part of what an investor in them owns.

**No asset is a proxy.** Every series is a security an investor could have bought and held throughout
the sample. In particular, `GLD` and `SLV` are physically backed trusts: they hold the metal, so their
returns carry the fund's fee but no futures roll.

The **S&P 500** sits outside the universe, and no strategy may allocate to it. It also illustrates the
index/tracker distinction the brief asks for. **`^GSPC` is the index itself: a price index, not
investable, and paying nothing**, so its adjusted and unadjusted returns are identical. **`SPY` is an
ETF that tracks it**: investable, and through the adjustment a total-return series. Over the panel the
gap is **2.0 points a year** (15.9% against 14.0%, Table 1.3), which is the index's dividend yield less
SPY's expense ratio. Using `^GSPC` as the benchmark would understate it by that much. `^GSPC` is
therefore quoted only when describing "the market". `SPY` is used in every performance comparison and
also defines our trading calendar.

The brief's own benchmark for the hundred experiments is the **equally weighted portfolio** of each
experiment's assets. We report both benchmarks because they answer different questions: whether an
optimiser beats naive diversification, and whether the exercise beats simply owning the index.

## 2.3 Calendar, alignment and the 15-year requirement

The panel runs **3 October 2011 to 6 October 2026**: **3,774 NYSE sessions**, a span of **15.0 years**,
satisfying the brief's minimum.

**Every asset is present for the whole panel.** The latest-listed, `SLV`, has data from April 2006,
and most of the stocks reach back to the 1970s or earlier. The 15-year requirement therefore binds on
the panel, not on any asset, and the intersection in which all 25 have data is the full 15.0 years.
The universe would have allowed a start in May 2006, bringing the 2008 crisis into the sample. We kept
the 15-year panel. As a result, the sample's stress periods are the March 2020 crash and the 2022
rate shock, and not a banking crisis. This matters for a universe with five banks and financials in
it (section 6).

We define the calendar as the dates `SPY` trades and reindex every series onto it. Every asset here
trades on NYSE or Nasdaq sessions, so no observation fell off the calendar. Interior gaps would be
forward-filled up to three sessions, with longer gaps reported rather than patched. In practice there
were **no missing sessions in any series** (Table 1.2).

## 2.4 Data quality

Coverage is complete (Table 1.2). The informative column is the share of **zero-return days**, which
tests whether a price is *fresh* rather than whether it exists. An unchanged close is either a
genuinely flat session or a quote that was not updated, and thin trading produces the second kind.
Stale prices bias measured volatility down and correlations toward zero. An optimiser then sees such
an asset as safer and more diversifying than it is.

**No asset shows the problem.** Zero-return days range from **0.08% (`GS`) to 1.91% (`SLV`)**, the level
of liquid instruments that occasionally close unchanged. Liquidity is deep throughout. The thinnest
asset, `CL`, trades a median **$220 million a day** over the panel, and `AAPL` trades $7.9 billion
(Table 1.1). Every asset could absorb a fund's rebalancing without moving its price.

## 2.5 What the data shows before any strategy

Figure 1.1 gives daily log-return correlations over the panel, with assets grouped by sector. The mean
pairwise correlation is **0.28**, but the average hides **strong sector structure**. Within a sector,
names move together: the **financials correlate at 0.75** among themselves (`JPM`–`BAC` 0.85, the
highest pair), consumer staples at 0.55, and technology and healthcare around 0.4. Across sectors the
mean falls to 0.25. A single market factor explains about a third of total variance.

**The diversification sits in one block.** `TLT` is negatively correlated with 22 of the other 24
assets. Its correlation is most negative with the banks (about −0.35) and is −0.23 with the S&P 500.
`GLD` is close to zero against everything except `SLV` (0.80). `VNQ` and `XOM`, by contrast, behave
like equities. Their correlations with the S&P 500 are 0.71 and 0.52. This structure is what the
correlation-aware strategies (GMV, ERC, MDP, MDC) can exploit and the correlation-blind ones (EW, IV)
cannot. How much it matters depends on the drawn subset. Four stocks from four sectors leave little to
exploit. Two banks plus `TLT` leave a great deal, and also hand the optimiser a near-collinear pair
whose weights it estimates poorly.

Figure 1.2 shows growth of $1 for each asset, as small multiples on a shared log scale, with the S&P 500
in every panel for reference. Terminal wealth ranges from **0.95× (`TLT`) to 29.8× (`AAPL`)**, against
**9.2×** for `SPY`. Seven assets beat the index: `AAPL`, `MSFT`, `AMZN`, `JPM`, `GS`, `BAC` and `UNH`.
Unlike in a universe with one runaway asset, no single holding decides the outcome: the best asset
ends at about five times the median one.

Two features of the figure carry into the limitations. **First, the list is chosen with hindsight.**
Twenty of the 25 are today's best-known US large caps, and the three best performers are among the
largest companies in the world now. A universe chosen this way is tilted toward winners before any
strategy runs. That flatters every strategy that holds them, and EW and the benchmark alike, so it
biases absolute returns up more than it distorts the ranking. `INTC`, below the index for most of the
decade, shows the tilt is not complete. **Second, the safest-looking asset lost money.** `TLT` fell 48%
from its August 2020 peak to October 2023 as rates rose. Low volatility and negative correlation make
it the asset that risk-based strategies favour most, and evaluation windows covering 2022 will show
what that cost.
