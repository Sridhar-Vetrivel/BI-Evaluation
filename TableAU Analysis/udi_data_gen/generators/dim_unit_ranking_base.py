"""Unit Ranking Base — monthly snapshot of comp-store ranking per (Unit, Brand, Month).

Treated as a derived dimension. Built from the Unit dim and a synthesized
monthly comp-sales/traffic series, so it lines up with Reported Sales aggregates
at the brand-month level.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.registry import REGISTRY
from ..core.rng import rng_for
from ..core.settings import DATE_END, DATE_START
from ..core.writers import Timer, stream_writer


def generate() -> int:
    rng = rng_for("UnitRankingBase")
    months = pd.date_range(DATE_START, DATE_END, freq="MS")  # month-start
    pers = REGISTRY.brand_personality

    units = pd.DataFrame({
        "SBRSequence": REGISTRY.unit_keys,
        "BrandSequence": [REGISTRY.unit_brand[int(s)] for s in REGISTRY.unit_keys],
        "OpenDate": pd.to_datetime([REGISTRY.unit_open_date[int(s)] for s in REGISTRY.unit_keys]),
        "CloseDate": pd.to_datetime([REGISTRY.unit_close_date[int(s)] for s in REGISTRY.unit_keys]),
    })

    total = 0
    with stream_writer("Unit Ranking Base") as w, Timer("Unit Ranking Base"):
        for m in months:
            # Active units in this month
            active = units[
                (units["OpenDate"] <= m)
                & (units["CloseDate"].isna() | (units["CloseDate"] >= m))
            ].copy()
            n = len(active)
            if n == 0:
                continue

            sbr = active["SBRSequence"].to_numpy()
            brand_seq = active["BrandSequence"].to_numpy()
            baseline = pers.loc[brand_seq, "baseline_daily_sales"].to_numpy()
            unit_mult = 0.6 + ((sbr % 1000) / 1000.0) * 0.9
            month_sales_cy = (baseline * unit_mult * 30 * rng.normal(1.0, 0.08, n).clip(0.5, 1.6)).round(2)
            month_sales_py = (month_sales_cy * rng.normal(0.96, 0.08, n).clip(0.6, 1.3)).round(2)
            avg_check = pers.loc[brand_seq, "avg_check"].to_numpy()
            traffic_cy = np.maximum(1, (month_sales_cy / np.maximum(avg_check, 1)).round())
            traffic_py = np.maximum(1, (month_sales_py / np.maximum(avg_check, 1)).round())

            ranked = rng.choice(["Y", "N"], n, p=[0.92, 0.08])
            comped = np.where(ranked == "Y", rng.choice(["Y", "N"], n, p=[0.95, 0.05]), "N")

            df = pd.DataFrame({
                "SBRBrand": [f"B{b}-U{s}" for b, s in zip(brand_seq, sbr)],
                "FBC": rng.choice([f"FBC-{i:04d}" for i in range(1, 250)], n),
                "FranchiseeEntity": rng.choice([f"FE-{i:05d}" for i in range(1, 800)], n),
                "Franchisee": rng.choice([f"Franchisee-{i:04d}" for i in range(1, 500)], n),
                "SBRNumber": [f"U{s % 1_000_000:06d}" for s in sbr],
                "SBRSequence": sbr.astype("int64"),
                "CalendarDate": [m.date()] * n,
                "Ranked": ranked,
                "Comped": comped,
                "CompSalesCY": month_sales_cy.astype("float32"),
                "CompSalesPY": month_sales_py.astype("float32"),
                "CompTrafficCY": traffic_cy.astype("float32"),
                "CompTrafficPY": traffic_py.astype("float32"),
                "BrandSequence": brand_seq.astype("int64"),
            })
            w.write(df)
            total += len(df)
    return total
