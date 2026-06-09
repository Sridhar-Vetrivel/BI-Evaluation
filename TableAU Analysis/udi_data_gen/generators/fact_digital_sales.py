"""Digital Sales — 1P / 3P / Other-party digital orders."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import attach_brand_personality, build_grid, iter_year_chunks
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer

COMP_VALUES = np.array(["Comp", "Non-Comp"], dtype=object)


def generate() -> int:
    rng = rng_for("DigitalSales")
    total = 0
    with stream_writer("Digital Sales") as w, Timer("Digital Sales"):
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            grid = attach_brand_personality(grid)
            n = len(grid)
            if n == 0:
                continue

            base = grid["baseline_daily_sales"].to_numpy()
            digital_share = grid["digital_share"].to_numpy()
            unit_mult = 0.6 + ((grid["SBRSequence"].to_numpy() % 1000) / 1000.0) * 0.9
            digital_total = base * digital_share * unit_mult * rng.normal(1.0, 0.2, n).clip(0.4, 2.0)

            # Split: 50% first party (own app), 35% third party (DoorDash/UberEats), 15% other (catering aggregators)
            split = rng.dirichlet([5, 3.5, 1.5], n)
            first_net = (digital_total * split[:, 0]).round(2)
            third_net = (digital_total * split[:, 1]).round(2)
            other_net = (digital_total * split[:, 2]).round(2)

            avg_check = grid["avg_check"].to_numpy() * 1.2  # digital checks slightly higher
            first_traffic = np.maximum(0, (first_net / np.maximum(avg_check, 1)).round()).astype("int32")
            third_traffic = np.maximum(0, (third_net / np.maximum(avg_check, 1)).round()).astype("int32")
            other_traffic = np.maximum(0, (other_net / np.maximum(avg_check, 1)).round()).astype("int32")

            # Items per order ~ 2-4
            ipo = rng.uniform(2.0, 4.0, n)
            first_items = (first_traffic * ipo).astype("int32")
            third_items = (third_traffic * ipo).astype("int32")
            other_items = (other_traffic * ipo).astype("int32")

            comp = COMP_VALUES[(rng.random(n) < 0.85).astype(int) ^ 1]

            df = pd.DataFrame({
                "BrandSequence": grid["BrandSequence"].astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "CalendarDate": grid["CalendarDate"],
                "ThirdPartyNetSales": third_net.astype("float32"),
                "ThirdPartyTraffic": third_traffic,
                "ThirdPartyItems": third_items,
                "FirstPartyNetSales": first_net.astype("float32"),
                "FirstPartyTraffic": first_traffic,
                "FirstPartyItems": first_items,
                "OtherPartyNetSales": other_net.astype("float32"),
                "OtherPartyTraffic": other_traffic,
                "OtherPartyItems": other_items,
                "Comp": comp,
            })
            w.write(df)
            total += len(df)
    return total
