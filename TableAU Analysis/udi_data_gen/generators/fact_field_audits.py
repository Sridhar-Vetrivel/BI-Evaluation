"""Field Audits — operational compliance audits."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import attach_brand_personality, build_grid, iter_year_chunks
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer


def generate() -> int:
    rng = rng_for("FieldAudits")
    total = 0
    with stream_writer("Field Audits") as w, Timer("Field Audits"):
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            grid = attach_brand_personality(grid)
            n = len(grid)
            if n == 0:
                continue

            quality = grid["food_safety_quality"].to_numpy()  # proxy for ops quality
            # Audit roughly quarterly per unit
            audited = (rng.random(n) < (1 / 90)).astype("int32")
            score = (75 + quality * 22 + rng.normal(0, 5, n)).clip(40, 100).round(1)
            score = np.where(audited > 0, score, np.nan)
            failures = np.where((audited > 0) & (score < 80), 1, 0).astype("int32")
            current = audited
            source = np.array(["Internal", "Third Party", "Self-Audit"])[rng.integers(0, 3, n)]

            df = pd.DataFrame({
                "BrandSequence": grid["BrandSequence"].astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "CalendarDate": grid["CalendarDate"],
                "FieldAuditSource": np.where(audited > 0, source, None),
                "CurrentFieldAudit": current,
                "FieldAuditScore": score.astype("float32"),
                "FieldAuditFailures": failures,
                "FieldAudits": audited,
            })
            w.write(df)
            total += len(df)
    return total
