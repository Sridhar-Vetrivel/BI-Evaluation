"""Remodels — sparse: most days zero, occasional completions / due."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import build_grid, iter_year_chunks
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer


def generate() -> int:
    rng = rng_for("Remodels")
    total = 0
    with stream_writer("Remodels") as w, Timer("Remodels"):
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            n = len(grid)
            if n == 0:
                continue

            # Completed: ~1 in 2000 unit-days
            completed = (rng.random(n) < (1 / 2000)).astype("int32")
            # Due: 1 if remodel is overdue (~3% of unit-days)
            due = (rng.random(n) < 0.03).astype("int32")

            df = pd.DataFrame({
                "BrandSequence": grid["BrandSequence"].astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "CalendarDate": grid["CalendarDate"],
                "RemodelsCompleted": completed,
                "RemodelsDue": due,
            })
            w.write(df)
            total += len(df)
    return total
