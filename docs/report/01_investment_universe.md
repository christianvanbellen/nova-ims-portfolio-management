# 2. Data

*Draft of report section 2. Target ~1.5 pages alongside Tables 1.1–1.3 and Figures 1.1–1.2. Every
number is produced by [`notebooks/01_investment_universe.ipynb`](../../notebooks/01_investment_universe.ipynb).*

---

## 2.1 Source and adjustment

All prices come from **Yahoo Finance** via the `yfinance` package, retrieved on **7 October 2026**.
Nothing is cached: each notebook re-downloads what it needs, so the extraction date — quoted once here
and applying throughout — fully determines every number in this report.

Prices are **adjusted closes**, restated for subsequent splits and distributions — equivalent to
reinvesting each dividend on its ex-date, so every series is a total-return series. That one switch is
the whole of our dividend treatment, and Table 1.3 measures what it is worth by setting each adjusted
series against its price-only counterpart on the same dates.

It is material for four of the six. **`GOVT`'s entire return is income**: 1.0% a year in total, −0.9%
on price alone, so an unadjusted series would show a Treasury allocation losing money. Distributions
supply **4.2 of `VNQ`'s 8.4 points** a year, and add 3.3 and 2.3 points to `TSM` and `RNMBY`. A
strategy scored on unadjusted prices would therefore be penalised for holding exactly the income
assets. `GC=F` and `BTC-USD` pay nothing, and adjustment leaves them unchanged.

The same factors would absorb splits and ADR ratio changes, but over the panel there are **none**
among the six assets (Table 1.3), so corporate actions other than cash distributions play no part.

The adjustment has two known gaps. Yahoo reinvests the **gross** dividend, whereas a US holder of the
ADRs receives it net of foreign withholding tax — 21% in Taiwan for `TSM`, 26.375% in Germany for
`RNMBY` — and of depositary fees; at the yields above this overstates each by roughly 0.6–0.7 points a
year. And `GC=F` is not adjusted at all (below). We use one vendor and one adjustment method, with no
second source to cross-check against (section 6).

## 2.2 Universe, currencies and proxies

The six assets in Table 1.1 span six distinct return drivers: a commodity, government bonds, a
semiconductor equity, listed real estate, a defence equity and a cryptoasset. Strategies allocate only
to these six.

All are **quoted in USD on US venues**, so the pipeline performs no currency conversion. Currency risk
has not disappeared, however — it sits inside the series. `TSM` is an ADR over a TWD-denominated share
and `RNMBY` over a EUR-denominated one, so their USD returns combine the local equity move with the
exchange-rate move, and we do not separate the two. Part of what a defence allocation buys here is
short EUR/USD.

**Two of the six are proxies, not holdings.** `GC=F` is the COMEX continuous front-month gold future: a
splice of successive contracts with no roll adjustment, so the price jump at each roll is booked as a
return and the collateral yield a futures holder earns is absent. It tracks spot gold closely but is
not a holding anyone can buy and keep. The investable counterparts are `GLD` or `IAU`, whose returns would be marginally lower
after fees. `BTC-USD` is a spot rate; before the US spot ETFs launched in **January 2024** no regulated
US vehicle tracked it closely. For roughly three-quarters of the sample, the bitcoin series is therefore
**not a return a US committee could have earned**, and pre-2024 bitcoin allocations should be read as an
upper bound on what was achievable.

The **S&P 500** sits outside the universe and no strategy may allocate to it, and it shows the
index/tracker distinction the brief asks for. **`^GSPC` is the index itself: a price index, not
investable, and paying nothing** — its adjusted and unadjusted returns are identical. **`SPY` is an ETF
that tracks it**: investable, and through the adjustment a total-return series. Over the panel the gap
is **2.0 points a year** (15.9% against 14.0%, Table 1.3) — the index's dividend yield less SPY's
expense ratio. Using `^GSPC` as the benchmark would understate it by that much, so `^GSPC` is quoted
only when describing "the market"; `SPY` is used in every performance comparison and also defines our
trading calendar. The brief's own benchmark for the
hundred experiments is the **equally weighted portfolio** of the six assets. We report both: they answer
different questions, namely whether an optimiser beats naive diversification, and whether the exercise
beats simply owning the index.

## 2.3 Calendar, alignment and the 15-year question

The panel runs **3 October 2011 to 6 October 2026** — **3,774 NYSE sessions**, a span of **15.0 years**,
satisfying the brief's minimum.

The six assets do not share that history. Only `GC=F`, `TSM` and `VNQ` reach back fifteen years; `GOVT`
begins February 2012, `RNMBY` November 2012, and `BTC-USD` not until **17 September 2014**. **The
intersection in which all six have data is 12.1 years, not 15.** Both figures are stated wherever
either is used: single-asset statistics use that asset's full history, while anything needing the
complete matrix — Figure 1.1, the rebasing in Figure 1.2 — starts in September 2014 and says so.

We did not pad the short series. Assets enter on their own first observation; pre-entry cells stay
missing, never zero- or back-filled. The sampler (section 4) draws each window only from dates where
every asset *in that drawn subset* has data, so short histories cost us candidate windows rather than
forcing an invented price. One consequence needs flagging: windows containing bitcoin can only come
from the back half of the sample, so BTC effects and recent-period effects are partially confounded —
section 6 tests this.

**The calendar.** `BTC-USD` trades 365 days a year, the others roughly 252. We define the calendar as
the dates `SPY` trades and reindex everything onto it, discarding **1,373 bitcoin observations** on
weekends and holidays. The bias runs against caution: bitcoin's weekend moves are large, so dropping
them **understates its measured volatility**, which leads every volatility-sensitive strategy to hold
*more* of it than full information would justify. Aggregating weekends into Monday would avoid this but
inject artificially fat-tailed Mondays into the stylised facts in section 3.

Interior gaps are forward-filled up to three sessions, longer ones reported rather than patched. In
practice this was near-trivial — **three `GC=F` sessions** filled, no gap anywhere exceeding the limit.
Table 1.2 records every fill; there are no silent ones.

## 2.4 Data quality

Coverage is essentially complete (Table 1.2). The informative column is the share of **zero-return
days**, which tests whether a price is *fresh* rather than whether it exists: an unchanged close is
either a genuinely flat session or a quote that was not updated, and thin trading produces the second
kind in volume.

**`RNMBY` is the problem case.** Nearly **20% of its sessions show no price change**, against 0.03–1.0%
for the other five, on a median of **1,500 shares a day** over its full history. The bias has a definite direction: stale
prices suppress measured variance and pull correlations toward zero, so `RNMBY` presents to an optimiser
as a low-risk, well-diversifying asset when it is neither. IV directly, and GMV and ERC through the
covariance matrix, will over-weight it. Section 6 re-runs the comparison without it. Its liquidity has
improved sharply since 2022, so that full-history median overstates how thin it is today and the bias
is concentrated in the early part of the sample.

`GOVT`'s 6.4% is not a data fault — a short-duration Treasury ETF genuinely closes unchanged on quiet
days, consistent with its low volatility rather than evidence against it.

## 2.5 What the data shows before any strategy

Figure 1.1 gives daily log-return correlations over the common period. The six are **genuinely weakly
correlated**: the mean pairwise correlation is about **0.1**, the strongest pair (`TSM`–`VNQ`) only
**0.33**, and `GOVT` is mildly negative against both `TSM` and the S&P 500. This is a precondition for
the comparison that follows — the correlation-aware strategies (GMV, ERC, MDP, MDC) can only separate
from the correlation-blind ones (EW, IV) when the matrix has structure to exploit. Here it does; under
uniformly high correlation all eight would converge.

Figure 1.2 shows growth of $1 on a log scale. Dispersion is extreme: `BTC-USD` returns roughly **187×**
and `TSM` **32×**, against **1.1×** for `GOVT` and **4.8×** for the S&P 500. The log axis is therefore
not cosmetic — linearly, bitcoin compresses the other five onto the x-axis. More importantly, **one
asset dominates the sample so heavily that measured performance is largely a question of how much
bitcoin a strategy happened to hold.** That is exactly why the hundred-window, four-asset-subset design
is the right one: it stops a single lucky allocation over a single period from deciding the
recommendation. Section 6 separates experiments that include bitcoin from those that do not.
