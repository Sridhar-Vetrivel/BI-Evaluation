"""Availability — operating hours and channel availability flags per day."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import build_grid, iter_year_chunks
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer


def generate() -> int:
    rng = rng_for("Availability")
    total = 0
    with stream_writer("Availability") as w, Timer("Availability"):
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            n = len(grid)
            if n == 0:
                continue

            standard_open = rng.uniform(10.0, 12.0, n).round(2)  # hours of online availability
            standard_op = rng.uniform(11.0, 14.0, n).round(2)
            # Actual usually slightly below standard
            open_hours = (standard_open - rng.uniform(0.0, 1.5, n)).clip(0, 24).round(2)
            op_hours = (standard_op - rng.uniform(0.0, 2.0, n)).clip(0, 24).round(2)

            closed = (rng.random(n) < 0.02).astype("int8")  # 2% closed days

            # Channel availability (0/1) — some brands disable some channels
            pickup_avail = (rng.random(n) < 0.95).astype("float32")
            pickup_dis = (1.0 - pickup_avail).astype("float32")
            dispatch_avail = (rng.random(n) < 0.65).astype("float32")
            dispatch_dis = (1.0 - dispatch_avail).astype("float32")
            curbside_avail = (rng.random(n) < 0.55).astype("float32")
            curbside_dis = (1.0 - curbside_avail).astype("float32")
            combined_avail = np.maximum.reduce([pickup_avail, dispatch_avail, curbside_avail]).astype("float32")
            combined_dis = (1.0 - combined_avail).astype("float32")

            df = pd.DataFrame({
                "BrandSequence": grid["BrandSequence"].astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "CalendarDate": grid["CalendarDate"],
                "OpenHours": open_hours.astype("float32"),
                "OperatingHours": op_hours.astype("float32"),
                "Closed": closed,
                "PickupAvailable": pickup_avail,
                "PickupDisabled": pickup_dis,
                "DispatchAvailable": dispatch_avail,
                "DispatchDisabled": dispatch_dis,
                "CurbsideAvailable": curbside_avail,
                "CurbsideDisabled": curbside_dis,
                "CombinedAvailable": combined_avail,
                "CombinedDisabled": combined_dis,
                "BrandStandardOnlineHours": standard_open.astype("float32"),
                "BrandStandardOperatingHours": standard_op.astype("float32"),
            })
            w.write(df)
            total += len(df)
    return total
