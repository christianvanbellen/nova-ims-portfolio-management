# Independent replication

A group colleague built the portfolio backtest separately from this repository. This folder holds their
files exactly as delivered (2026-10-16) and our write-up comparing the two implementations.

**In short:** the designs differ (5-year datasets, data ending 2024, futures for gold and silver, zero
risk-free rate, results summarised by means). The paired results still agree with ours: no strategy beats
equal weight on Sharpe in a clear majority of runs, and the risk-based strategies have lower volatility
than EW in nearly every run. The report can cite this as an independent robustness check. The full
reasoning is in [`comparison.md`](comparison.md) §1 and §11.

## Contents

| Path | What it is |
| --- | --- |
| [`comparison.md`](comparison.md) | **Start here.** Where the two implementations converge and diverge: design, results, defects found in the colleague's notebook, and decisions for the group |
| [`inventory.md`](inventory.md) | File by file: what each delivered file contains, the notebook cell by cell, and how both bodies of work map onto the brief |
| [`delivered/Backtesting_Implementation.ipynb`](delivered/Backtesting_Implementation.ipynb) | The colleague's notebook. It produced every other delivered file |
| [`delivered/tables/`](delivered/tables/) | Four Excel workbooks: summary metrics, fee sensitivity, turnover, paired win rates |
| [`delivered/figures/`](delivered/figures/) | Four PNG charts exported from the notebook |

## Ground rules

- **Read-only.** Files in `delivered/` are kept as received (original filenames, saved outputs). Nothing
  was re-run. To change something, ask the colleague for a new version and replace the files.
- **Not part of the pipeline.** Nothing in `src/` or `notebooks/` reads from this folder. The notebook
  also needs packages that are not in `pyproject.toml` (`quantstats`, `riskparityportfolio`, `tqdm`,
  `openpyxl`) and downloads live data, so it will not reproduce as-is (inventory §1.4).
- **Adoptions go through the definitions.** Any idea taken from here (buy-and-hold scenario, wider cost
  grid, Quintile benchmark) goes into [`docs/project-definitions.md`](../docs/project-definitions.md) §8
  first, then into the notebooks.
