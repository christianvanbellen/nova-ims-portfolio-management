# Independent replication

A group colleague built the portfolio backtest separately from this repository. This folder holds the final
version of their files exactly as delivered (2026-10-20, replacing the first delivery of 2026-10-16) and our
write-up comparing the two implementations.

**In short:** the final version uses the same 25 assets and the same 2010–2026 panel as ours, and reports
medians as well as means. The designs still differ (5-year datasets, zero risk-free rate, uniform subset
draw, a price-only S&P 500 index as benchmark). The paired results agree with ours more closely than
before: no strategy beats equal weight on Sharpe in a majority of runs, and the risk-based strategies have
lower volatility than EW in nearly every run. The report can cite this as an independent robustness check.
What changed between versions is in [`comparison.md`](comparison.md) §2; the full reasoning in §1 and §12.

## Contents

| Path | What it is |
| --- | --- |
| [`comparison.md`](comparison.md) | **Start here.** What changed in the final version, where the two implementations converge and diverge (design, results), defects in the colleague's notebook and their status, and decisions for the group |
| [`inventory.md`](inventory.md) | File by file: what each delivered file contains, the notebook cell by cell, and how both bodies of work map onto the brief |
| [`delivered/Backtesting_Implementation.ipynb`](delivered/Backtesting_Implementation.ipynb) | The colleague's notebook. It produced every other delivered file |
| [`delivered/data/`](delivered/data/) | `Data_Utilized.xlsx`: the price snapshot the notebook runs on, with its download timestamp |
| [`delivered/tables/`](delivered/tables/) | Four Excel workbooks: summary metrics (mean and median), fee sensitivity, paired win rates for two scenarios |
| [`delivered/figures/`](delivered/figures/) | Four PNG charts exported from the notebook |

## Ground rules

- **Read-only.** Files in `delivered/` are kept as received (original filenames, saved outputs). Nothing
  was re-run. To change something, ask the colleague for a new version and replace the files; the previous
  version stays in git history.
- **Not part of the pipeline.** Nothing in `src/` or `notebooks/` reads from this folder. The notebook
  also needs packages that are not in `pyproject.toml` (`quantstats`, `riskparityportfolio`, `tqdm`,
  `openpyxl`) and a hard-coded Windows path, so it will not run as-is (inventory §1.4).
- **Adoptions go through the definitions.** Any idea taken from here (buy-and-hold scenario, wider cost
  grid, Quintile benchmark) goes into [`docs/project-definitions.md`](../docs/project-definitions.md) §8
  first, then into the notebooks.
