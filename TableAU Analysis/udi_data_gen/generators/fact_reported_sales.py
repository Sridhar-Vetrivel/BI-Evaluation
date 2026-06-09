"""Reported Sales — daily net sales / traffic with CY & PY pairs."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import attach_brand_personality, build_grid, iter_year_chunks
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer

COMP_VALUES = np.array(["Comp", "Non-Comp"], dtype=object)


def generate() -> int:
    rng = rng_for("ReportedSales")
    total = 0
    with stream_writer("Reported Sales") as w, Timer("Reported Sales") as _t:
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            grid = attach_brand_personality(grid)
            n = len(grid)
            if n == 0:
                continue

            base = grid["baseline_daily_sales"].to_numpy()
            # Per-unit fixed multiplier (deterministic by SBRSequence parity)
            unit_mult = 0.6 + ((grid["SBRSequence"].to_numpy() % 1000) / 1000.0) * 0.9
            # Daily noise
            noise = rng.normal(1.0, 0.15, n).clip(0.4, 2.0)
            net_cy = (base * unit_mult * noise).round(2)
            net_py = (net_cy * rng.normal(0.96, 0.10, n).clip(0.5, 1.3)).round(2)

            avg_check = grid["avg_check"].to_numpy()
            traffic_cy = np.maximum(1, (net_cy / np.maximum(avg_check, 1)).round()).astype("int32")
            traffic_py = np.maximum(1, (net_py / np.maximum(avg_check, 1)).round()).astype("int32")

            discount_rate = rng.uniform(0.02, 0.10, n)
            disc_cy = (net_cy * discount_rate).round(2)
            disc_py = (net_py * discount_rate * rng.uniform(0.8, 1.2, n)).round(2)

            cat_share = grid["catering_share"].to_numpy()
            cater_cy = (net_cy * cat_share).round(2)
            cater_py = (net_py * cat_share * rng.uniform(0.85, 1.15, n)).round(2)
            # Catering check counts ~ catering revenue / (3x avg_check) since catering orders are larger
            cater_chk_cy = np.maximum(0, (cater_cy / np.maximum(avg_check * 3, 1)).round()).astype("int32")
            cater_chk_py = np.maximum(0, (cater_py / np.maximum(avg_check * 3, 1)).round()).astype("int32")

            comp = COMP_VALUES[(rng.random(n) < 0.85).astype(int) ^ 1]  # ~85% Comp
            traffic_comp = COMP_VALUES[(rng.random(n) < 0.85).astype(int) ^ 1]

            df = pd.DataFrame({
                "BrandSequence": grid["BrandSequence"].astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "CalendarDate": grid["CalendarDate"],
                "Comp": comp,
                "TrafficComp": traffic_comp,
                "NetSalesCY": net_cy.astype("float32"),
                "NetSalesPY": net_py.astype("float32"),
                "TrafficCY": traffic_cy.astype("float32"),
                "TrafficPY": traffic_py.astype("float32"),
                "DiscountsCY": disc_cy.astype("float32"),
                "DiscountsPY": disc_py.astype("float32"),
                "CateringCY": cater_cy.astype("float32"),
                "CateringPY": cater_py.astype("float32"),
                "CateringCheckCountCY": cater_chk_cy.astype("float32"),
                "CateringCheckCountPY": cater_chk_py.astype("float32"),
            })
            w.write(df)
            total += len(df)
    return total
