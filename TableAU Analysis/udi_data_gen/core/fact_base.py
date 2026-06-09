"""Shared helpers for generating daily-grain fact tables in year-sized chunks.

Each chunk yields a DataFrame with the canonical FK triplet:
    (BrandSequence, SBRSequence, CalendarDate)
plus a per-row pull from the brand-personality table for use by measure
formulas. Units are filtered by OpenDate <= day <= CloseDate so closed/not-yet-
opened stores don't appear (preserves a realistic step-function rollout).
"""

from __future__ import annotations

from typing import Iterator

import numpy as np
import pandas as pd

from .registry import REGISTRY


def iter_year_chunks() -> Iterator[pd.DatetimeIndex]:
    idx = REGISTRY.date_index
    if len(idx) == 0:
        raise RuntimeError("DimDate must be generated first")
    years = sorted(set(idx.year))
    for y in years:
        yield idx[idx.year == y]


def build_grid(date_chunk: pd.DatetimeIndex) -> pd.DataFrame:
    """Cartesian (active-Unit x date) grid joined with the unit's BrandSequence.

    Returns columns: BrandSequence, SBRSequence, CalendarDate
    """
    units = pd.DataFrame({
        "SBRSequence": REGISTRY.unit_keys,
        "BrandSequence": [REGISTRY.unit_brand[int(s)] for s in REGISTRY.unit_keys],
        "OpenDate": [REGISTRY.unit_open_date[int(s)] for s in REGISTRY.unit_keys],
        "CloseDate": [REGISTRY.unit_close_date[int(s)] for s in REGISTRY.unit_keys],
    })

    # Cross join via index-broadcasting (vectorized)
    dates = pd.DataFrame({"CalendarDate": date_chunk})
    grid = units.merge(dates, how="cross")

    # Filter to active days for the unit
    cal = pd.to_datetime(grid["CalendarDate"])
    open_ok = cal >= pd.to_datetime(grid["OpenDate"])
    closed = grid["CloseDate"].notna()
    close_ok = ~closed | (cal <= pd.to_datetime(grid["CloseDate"]))
    grid = grid.loc[open_ok & close_ok, ["BrandSequence", "SBRSequence", "CalendarDate"]].reset_index(drop=True)

    # Normalize date to .date() for parquet
    grid["CalendarDate"] = pd.to_datetime(grid["CalendarDate"]).dt.date
    return grid


def attach_brand_personality(grid: pd.DataFrame) -> pd.DataFrame:
    """Left-join brand personality attributes onto every fact row."""
    return grid.merge(
        REGISTRY.brand_personality, left_on="BrandSequence", right_index=True, how="left"
    )
