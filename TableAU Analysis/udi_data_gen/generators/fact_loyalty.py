"""Loyalty — enrollments, loyalty sales, earnable sales."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import attach_brand_personality, build_grid, iter_year_chunks
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer

COMP_VALUES = np.array(["Comp", "Non-Comp"], dtype=object)


def generate() -> int:
    rng = rng_for("Loyalty")
    total = 0
    with stream_writer("Loyalty") as w, Timer("Loyalty"):
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            grid = attach_brand_personality(grid)
            n = len(grid)
            if n == 0:
                continue

            base = grid["baseline_daily_sales"].to_numpy()
            unit_mult = 0.6 + ((grid["SBRSequence"].to_numpy() % 1000) / 1000.0) * 0.9
            adoption = grid["loyalty_adoption"].to_numpy()
            avg_check = grid["avg_check"].to_numpy()

            day_sales = base * unit_mult * rng.normal(1.0, 0.15, n).clip(0.4, 1.8)
            loyalty_sales = (day_sales * adoption).round(2)
            # Earnable: sales that qualified for points (slightly less than loyalty_sales)
            earnable = (loyalty_sales * rng.uniform(0.85, 0.98, n)).round(2)
            loyalty_traffic = np.maximum(0, (loyalty_sales / np.maximum(avg_check, 1)).round()).astype("int32")

            # Enrollments: small fraction of new guests
            day_traffic = np.maximum(1, (day_sales / np.maximum(avg_check, 1)).round())
            enrollments = (day_traffic * rng.uniform(0.005, 0.04, n)).round().astype("int32")

            comp = COMP_VALUES[(rng.random(n) < 0.85).astype(int) ^ 1]

            df = pd.DataFrame({
                "CalendarDate": grid["CalendarDate"],
                "BrandSequence": grid["BrandSequence"].astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "Enrollments": enrollments,
                "LoyaltySales": loyalty_sales.astype("float32"),
                "LoyaltyEarnableSales": earnable.astype("float32"),
                "LoyaltyTraffic": loyalty_traffic,
                "Comp": comp,
            })
            w.write(df)
            total += len(df)
    return total
