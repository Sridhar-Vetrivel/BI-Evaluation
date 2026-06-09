"""Catering — 1P and 3P catering sales / traffic."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import attach_brand_personality, build_grid, iter_year_chunks
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer

COMP_VALUES = np.array(["Comp", "Non-Comp"], dtype=object)


def generate() -> int:
    rng = rng_for("Catering")
    total = 0
    with stream_writer("Catering") as w, Timer("Catering"):
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            grid = attach_brand_personality(grid)
            n = len(grid)
            if n == 0:
                continue

            base = grid["baseline_daily_sales"].to_numpy()
            cat_share = grid["catering_share"].to_numpy()
            unit_mult = 0.6 + ((grid["SBRSequence"].to_numpy() % 1000) / 1000.0) * 0.9
            # 60% of days have zero catering activity
            active = rng.random(n) < 0.4
            cat_total = base * cat_share * unit_mult * rng.normal(1.0, 0.4, n).clip(0.1, 3.0)
            cat_total = np.where(active, cat_total, 0.0)

            third_share = rng.uniform(0.3, 0.7, n)
            third_net = (cat_total * third_share).round(2)
            first_net = (cat_total - third_net).round(2)

            avg_check = grid["avg_check"].to_numpy() * 3.0  # catering checks are bigger
            first_traffic = np.maximum(0, (first_net / np.maximum(avg_check, 1)).round()).astype("int32")
            third_traffic = np.maximum(0, (third_net / np.maximum(avg_check, 1)).round()).astype("int32")
            comp = COMP_VALUES[(rng.random(n) < 0.85).astype(int) ^ 1]

            df = pd.DataFrame({
                "BrandSequence": grid["BrandSequence"].astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "CalendarDate": grid["CalendarDate"],
                "FirstPartyNetSales": first_net.astype("float32"),
                "ThirdPartyNetSales": third_net.astype("float32"),
                "FirstPartyTraffic": first_traffic,
                "ThirdPartyTraffic": third_traffic,
                "Comp": comp,
            })
            w.write(df)
            total += len(df)
    return total
