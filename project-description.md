# Group & Individual Project Brief

**Executive Education | Post Graduation — Data Science for Finance**
© Jorge Miguel Bravo, 2026

**Purpose:** Investigate the empirical properties of financial market returns and evaluate alternative portfolio investment strategies. Your analysis should explain what the evidence means for an investment decision, taking account of risk, implementation costs and the limitations of historical backtesting.

---

## A. Group Project

**Assessment weight: 14 out of 20 marks.**

### Minimum tasks

#### 1. Select the investment universe and analyse returns

Select a diversified universe of listed securities, such as shares and exchange-traded funds (ETFs). Stock indices and cryptoassets may also be considered where appropriate. Download market data for a minimum of 15 years including the latest available data and state the data source and extraction date. Explain your selection and document any shorter histories or missing observations.

For each asset, calculate daily, weekly and monthly log returns using adjusted closing prices where available. Derive weekly and monthly returns from period-end prices or by summing daily log returns. Explain how dividends, corporate actions, currencies and trading calendars are treated. Distinguish non-investable indices from investable products that track them.

Select one share and investigate the following stylised facts at daily, weekly and monthly frequencies. Use suitable charts, descriptive statistics and, where appropriate, statistical tests. Assess whether the evidence supports each feature; do not assume that every feature must hold.

- Little or no serial correlation in raw returns.
- Non-normal unconditional return distributions and fat tails, particularly at daily frequency.
- Asymmetry in the return distribution, including possible negative skewness.
- Volatility clustering, assessed through absolute or squared returns.
- Leverage effects or asymmetric volatility responses to positive and negative returns.
- Conditional non-normality, assessed using standardised residuals from a suitable volatility model.

#### 2. Compare the core portfolio strategies

Use daily historical data and a rolling-window, walk-forward backtest to compare the following strategies:

a) Equally weighted portfolio;
b) Markowitz mean–variance portfolio;
c) Global minimum-variance portfolio;
d) Maximum Sharpe ratio portfolio;
e) Inverse-volatility portfolio; risk parity portfolio with equal risk contributions;
f) Most diversified portfolio; maximum decorrelation portfolio.

Specify each strategy's objective and constraints. For the Markowitz portfolio, state the target return or risk-aversion parameter so that it is distinct from the minimum-variance and maximum Sharpe ratio portfolios. Distinguish inverse-volatility weighting from equal risk contributions when assets are correlated.

---

## B. Individual Project

**Assessment weight: 6 out of 20 marks.**

### Minimum tasks

Use the dataset developed for the group project to investigate a selection of alternative portfolio management strategies. Compare them with relevant group-project benchmarks using a consistent backtesting framework. Clearly identify your individual contribution and explain any changes to the investment universe or assumptions. Possible strategies include:

a) Mean–semivariance portfolio.
b) Hierarchical risk parity portfolio.
c) Mean–conditional value-at-risk portfolio, also described as mean–expected shortfall.
d) Minimum conditional drawdown-at-risk portfolio.
e) Mean absolute deviation portfolio.
f) Maximum Omega ratio portfolio.
g) Tactical dual momentum strategy.
h) Adaptive asset allocation strategy.
i) Classic 60/40 equity–bond portfolio.
j) Another clearly specified and justified strategy.

Define each strategy's allocation rule, parameters and rebalancing schedule. For a 60/40 strategy, use appropriate equity and bond exposures; if these are absent from the group dataset, explain any extension and ensure that benchmark comparisons remain meaningful.

Critically evaluate the results using the same performance conventions as the group project. Focus on whether the alternative improves an investment decision after costs, and whether the benefit justifies additional complexity. The optional extensions below provide further ideas.

---

## Group size, milestones and reports

The standard and recommended group size is four participants. You are responsible for organising your own group.

Submit one consolidated digital report for the group project and a separate report for the individual project, setting out the objectives, methods, results and conclusions. Reports may be prepared in Word or LaTeX and submitted in PDF or Word format. An HTML notebook is also acceptable. Include all supporting files needed to reproduce the results, such as source documents, Excel workbooks, R scripts, Python code and data or data-retrieval instructions.

Submit the group and individual reports, together with the supporting files, through Moodle **no later than 30 October 2026**. Name the individual PDF report `FirstName_Surname_StudentNumber.pdf`; use the corresponding extension if submitting a Word report.

### Suggested report structure

Executive summary and recommendation; data; methods and assumptions; results; robustness checks and limitations; conclusions; references and reproducibility appendix. Place detailed technical output in the appendix and write the main report for an investment committee.

---

## Optional strategies and extensions to test

These suggestions extend the original brief and are not additional minimum requirements. A focused comparison of one or two extensions with clear benchmarks is preferable to testing many poorly explained variants.

### A. Shrinkage covariance portfolio

Re-estimate the global minimum-variance portfolio using a shrinkage covariance estimator, retaining the same constraints and rebalancing dates. Test whether the resulting weights, turnover and out-of-sample risk are more stable than under the sample covariance estimator. This isolates the value of improving risk estimation.

*Suggested reading:* Ledoit, Olivier and Wolf, Michael, *Honey, I Shrunk the Sample Covariance Matrix* (June 2003). UPF Economics and Business Working Paper No. 691. Available at SSRN: <https://ssrn.com/abstract=433840> or <http://dx.doi.org/10.2139/ssrn.433840>

### B. Constrained and turnover-aware optimisation

Compare the baseline optimiser with a maximum asset-weight constraint and, separately, a turnover limit or transaction-cost penalty. Choose a small set of settings before evaluation. Test whether modest constraints improve net performance and reduce concentration without materially weakening diversification. This makes the trade-off between an optimised allocation and an implementable mandate explicit.

### C. Volatility-targeted allocation

Scale a baseline portfolio's exposure using trailing volatility and allocate the remainder to cash. For a simple unlevered variant, cap risky exposure at 100%. Set the volatility target and estimation window before testing. Compare realised volatility, drawdowns, turnover and net returns with the unscaled portfolio.

*Suggested background:* Moreira and Muir, *Volatility-Managed Portfolios*, <https://www.nber.org/papers/w22208>. The proposed exercise is a simplified variant, not a replication.

### D. Trend filter with a defensive allocation

At each monthly rebalance, retain exposure to an asset only when its price exceeds a pre-specified moving average; otherwise allocate its share to cash or a defined defensive asset. Use lagged signals and specify the cash return. Compare this rule with buy-and-hold and the same portfolio without the filter. Assess downside protection, missed recoveries and the cost of repeated reversals.

### E. Blended portfolio allocation

Combine, for example, equally weighted, minimum-variance and risk parity allocations using fixed blend weights chosen in advance. Test whether the blend delivers more stable rankings across periods and asset subsets than any component alone. Report the blend's own turnover and costs, rather than simply averaging the components' net performance statistics.

### F. Rebalancing policy experiment

Hold the allocation method constant and compare monthly, quarterly and threshold-based rebalancing. Define the deviation threshold before testing. Evaluate whether lower turnover compensates for departures from target weights and changes in risk. This is a manageable extension with a direct governance and implementation interpretation.

---

## Group project methodology and evaluation

### Backtesting design

Generate 100 three-year datasets by randomly selecting contiguous historical periods and subsets of the investment universe. Keep observations in chronological order within each dataset. Use the same sampled periods and asset subsets for every strategy and record the random seed so that the experiment can be reproduced.

Specify how each three-year dataset is divided between initial estimation and out-of-sample evaluation. A suggested design is to use the first two years for estimation and the third year for evaluation, updating estimates with a trailing one-year window and rebalancing quarterly. Treat this as a proposed common convention, to be agreed before comparing results.

- Use only information available at each portfolio formation date. Execute trades after the information used to set the weights becomes available; do not use future observations to choose assets or tune parameters.
- Apply consistent assumptions across strategies for investment constraints, weight limits, short selling, leverage, rebalancing, the risk-free rate and transaction costs. A fully invested, long-only specification is a practical baseline.
- Use simple returns to calculate portfolio returns and compound wealth over time. Use log returns for the stylised-fact analysis. Allow portfolio weights to drift between rebalancing dates.
- Document asset eligibility, sample size, missing-data treatment and optimisation failures. Do not silently remove unsuccessful runs. Discuss survivorship bias and any reliance on today's asset universe.
- Report turnover and performance both before and after transaction costs. State the cost convention and test whether rankings change under less favourable cost assumptions.

### Evaluate performance and explain the decision

Compare annualised returns and volatility, the Sharpe ratio, maximum drawdown and a drawdown-based measure such as the Sterling ratio. You may add the Sortino or Calmar ratio. Define the precise conventions used, including annualisation, the risk-free rate and any drawdown denominator.

Summarise results across the 100 experiments using medians, dispersion and the proportion of experiments in which each strategy outperforms the equally weighted benchmark. Show whether conclusions depend on the sampled period or asset subset. Overlapping historical windows are not independent observations; avoid treating the 100 experiments as 100 independent tests.

Discuss the trade-offs between return, downside risk, concentration, turnover and complexity. Identify the strategy you would recommend for a stated investor objective, explain the evidence supporting that choice, and describe the conditions under which you would reconsider it. A strategy that performs poorly can still support a strong project if the analysis explains why.
