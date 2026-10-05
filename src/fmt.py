"""Number formatting for report tables (plan SS1, "Numbers").

Percent columns carry the `%` in the *header*, never the cell. Anything not
applicable prints an em dash, never `0` and never blank.
"""

from __future__ import annotations

import math

import pandas as pd

NA = "—"  # em dash


def _blank(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value)) or value is pd.NA


def number(value, dp: int = 2) -> str:
    """Fixed decimal places, minus sign for negatives, em dash when missing."""
    return NA if _blank(value) else f"{value:.{dp}f}"


def percent(value, dp: int = 2) -> str:
    """A percent *value* -- the `%` belongs in the column header."""
    return number(value, dp)


def count(value) -> str:
    """Integer with a thousands separator."""
    return NA if _blank(value) else f"{int(round(value)):,}"


def pvalue(value) -> str:
    """Three decimal places; below that, `<0.001`."""
    if _blank(value):
        return NA
    return "<0.001" if value < 0.001 else f"{value:.3f}"


def style(frame: pd.DataFrame, rules: dict[str, object]) -> pd.DataFrame:
    """Apply a `{column: formatter}` map and return a frame of strings.

    Columns with no rule are passed through unchanged. Use this immediately
    before displaying a table, never on the frame downstream code reads.
    """
    out = frame.copy()
    for column, rule in rules.items():
        if column in out.columns:
            out[column] = out[column].map(rule)
    return out.fillna(NA)
