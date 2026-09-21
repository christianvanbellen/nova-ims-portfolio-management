# NOVA IMS — Asset Pricing and Portfolio Management

Coursework repository for the **Asset Pricing and Portfolio Management** group and individual project
(Post-Graduation in Data Science for Finance, NOVA IMS).

## What this project is about

The project investigates the **empirical properties of financial market returns** and evaluates
**alternative portfolio investment strategies**, so that the evidence can support a real investment
decision — one that accounts for risk, implementation costs, and the limits of historical backtesting.

Two strands of work:

1. **Stylised facts of asset returns.** Build a 15+ year dataset of listed securities (shares, ETFs,
   indices), compute daily/weekly/monthly log returns, and test the classic features: little serial
   correlation in raw returns, fat tails, negative skewness, volatility clustering, leverage effects,
   and conditional non-normality from a GARCH-type model.
2. **Portfolio strategy comparison.** Using a rolling-window, walk-forward backtest over 100 randomly
   sampled three-year windows, compare equally weighted, mean–variance, global minimum-variance,
   maximum Sharpe, inverse-volatility, risk parity, most-diversified, and maximum-decorrelation
   portfolios — before and after transaction costs — then recommend one for a stated investor objective.

The full brief is in [`project-description.md`](project-description.md) (converted from the original
PDF in `classes/`).

### Repository layout

| Path | Contents |
| --- | --- |
| `project-description.md` | The assignment brief: tasks, methodology, deliverables, deadline |
| `classes/` | Lecture material — lab notebooks and scripts (Python and R), reference PDF |
| `docs/` | Write-ups and report drafts |
| `pyproject.toml` | Project dependencies |
| `uv.lock` | Exact package versions, so everyone gets an identical environment |

---

## Setting up (step by step)

**New to Python environments?** Read this first. A *virtual environment* is a private folder of Python
packages that belongs to this project alone. It keeps this project's libraries from clashing with any
other Python work on your machine, and it lets everyone on the team run exactly the same versions.
Here the environment lives in a hidden folder called `.venv/`, and it is **not** committed to git —
you create it locally in one command.

We use **[uv](https://docs.astral.sh/uv/)** to manage it. uv installs Python itself, creates the
environment, and installs packages — so it is the only tool you need to install by hand.

### Step 1 — Install uv

**macOS** (in Terminal):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** (in PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Close and reopen your terminal afterwards**, then check it worked:

```bash
uv --version
```

If you get "command not found", the terminal is still the old one — open a fresh window and try again.

### Step 2 — Get the code

```bash
git clone https://github.com/christianvanbellen/nova-ims-portfolio-management.git
cd nova-ims-portfolio-management
```

Every command from here on assumes you are **inside that folder**.

### Step 3 — Create the environment

```bash
uv sync
```

That single command downloads the right Python version (3.12), creates `.venv/`, and installs every
package listed in `uv.lock`. It takes a minute the first time and is near-instant afterwards.

Run `uv sync` again any time someone adds a new dependency — it brings you back in line.

---

## Running the project

### The easy way: `uv run`

Prefix any command with `uv run` and it executes inside the project environment automatically.
**You do not need to activate anything.**

```bash
uv run jupyter lab              # open the notebooks in your browser
uv run python my_script.py      # run a script
uv run python                   # an interactive Python prompt
```

### The traditional way: activating

If you prefer the classic workflow where your terminal prompt shows the environment name:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**

```cmd
.venv\Scripts\activate.bat
```

Your prompt now starts with `(portfolio-management)`. Plain `python` and `jupyter lab` now use the
project environment. Type `deactivate` to leave.

### Using the notebooks in VS Code

Open a notebook, click the kernel selector in the top right, choose **Python Environments**, and pick
the interpreter inside `.venv` (it is usually listed first, marked *Recommended*).

---

## Adding a package

Never use `pip install` here — it would install into the environment without recording it, and your
teammates would not get the package. Use:

```bash
uv add scikit-learn
```

This installs it, adds it to `pyproject.toml`, and updates `uv.lock`. Commit both files so everyone
else picks it up with `uv sync`. To remove one: `uv remove scikit-learn`.

### What is already installed

`numpy`, `pandas`, `matplotlib` (data handling and charts) · `yfinance` (market data downloads) ·
`scipy`, `statsmodels` (statistical tests and time-series models) · `arch` (GARCH volatility models) ·
`jupyter`, `ipykernel` (notebooks).

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `uv: command not found` | Close the terminal and open a new one. If it persists, re-run the Step 1 installer. |
| Windows: *"running scripts is disabled on this system"* | Use `uv run …` instead of activating, or run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` in PowerShell once. |
| `No such file or directory: .venv/bin/activate` | Either you are not in the project folder (`cd` into it), or you have not run `uv sync` yet. Note the leading dot: `.venv`, not `venv`. |
| `ModuleNotFoundError` for a package you know is installed | You are running system Python instead of the project's. Use `uv run python …`, or activate the environment first. |
| Jupyter shows the wrong packages | Wrong kernel selected — pick the `.venv` interpreter (see above). |
| Something is badly broken | Delete the `.venv` folder and run `uv sync` again. Nothing valuable lives in it. |

### A note on the R files

`classes/` also contains R material (`.r`, `.Rmd`). Those are not part of the Python environment and
need [R](https://cran.r-project.org/) and [RStudio](https://posit.co/download/rstudio-desktop/) to run.
The Python notebooks mirror them, so R is optional.
