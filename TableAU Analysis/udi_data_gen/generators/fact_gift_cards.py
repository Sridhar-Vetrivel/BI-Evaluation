"""Gift Cards — three brand-role keys (Card/Store/Merged) all reference Brand."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import attach_brand_personality, build_grid, iter_year_chunks
from ..core.registry import REGISTRY
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer

COMP_VALUES = np.array(["Comp", "Non-Comp"], dtype=object)


def generate() -> int:
    rng = rng_for("GiftCards")
    total = 0
    with stream_writer("Gift Cards") as w, Timer("Gift Cards"):
        brand_pool = REGISTRY.brand_keys
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            grid = attach_brand_personality(grid)
            n = len(grid)
            if n == 0:
                continue

            base = grid["baseline_daily_sales"].to_numpy()
            unit_mult = 0.6 + ((grid["SBRSequence"].to_numpy() % 1000) / 1000.0) * 0.9
            # ~3% of revenue is gift cards
            gc_total = base * 0.03 * unit_mult * rng.uniform(0.0, 2.0, n)

            activations = np.maximum(0, (gc_total / 30.0).round()).astype("int32")
            first_share = rng.uniform(0.55, 0.85, n)
            first_act = (activations * first_share).astype("int32")
            third_act = activations - first_act

            first_sales = (gc_total * first_share).round(2)
            third_sales = (gc_total - first_sales).round(2)

            comp = COMP_VALUES[(rng.random(n) < 0.85).astype(int) ^ 1]

            # Card/Store/Merged brand: 70% of the time all equal to unit's brand
            store_brand = grid["BrandSequence"].to_numpy().astype("int64")
            card_brand = np.where(
                rng.random(n) < 0.70,
                store_brand,
                rng.choice(brand_pool, n),
            )
            merged_brand = np.where(
                rng.random(n) < 0.85,
                store_brand,
                rng.choice(brand_pool, n),
            )

            df = pd.DataFrame({
                "CardBrandSequence": card_brand.astype("int64"),
                "StoreBrandSequence": store_brand,
                "MergedBrandSequence": merged_brand.astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "CalendarDate": grid["CalendarDate"],
                "TotalActivations": activations,
                "TotalSales": gc_total.astype("float32").round(2),
                "FirstPartySales": first_sales.astype("float32"),
                "FirstPartyActivations": first_act,
                "ThirdPartySales": third_sales.astype("float32"),
                "ThirdPartyActivations": third_act,
                "Comp": comp,
            })
            w.write(df)
            total += len(df)
    return total
