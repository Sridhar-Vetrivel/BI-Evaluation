"""Food Safety — audit scores, critical findings, ratings."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import attach_brand_personality, build_grid, iter_year_chunks
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer

RATINGS = np.array(["A", "B", "C", "D", "F"], dtype=object)
# Cumulative thresholds: high quality -> A; very low -> F
RATING_SORT = {"A": 1, "B": 2, "C": 3, "D": 4, "F": 5}


def generate() -> int:
    rng = rng_for("FoodSafety")
    total = 0
    with stream_writer("Food Safety") as w, Timer("Food Safety"):
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            grid = attach_brand_personality(grid)
            n = len(grid)
            if n == 0:
                continue

            quality = grid["food_safety_quality"].to_numpy()
            # Score 70-100, biased upward by brand quality
            score = (70 + quality * 30 + rng.normal(0, 4, n)).clip(40, 100).round(1)
            # Audits happen ~once every 60 days -> mostly 0, occasionally 1
            audits = (rng.random(n) < (1 / 60)).astype("int32")
            current_audit = audits.copy()  # 1 if audited today
            # Critical findings: poisson with low lambda inversely related to quality
            criticals = rng.poisson((1 - quality) * 2.5, n).astype("int32")
            criticals = np.where(audits > 0, criticals, 0)
            # Failures: 1 if score < 80
            failures = ((score < 80) & (audits > 0)).astype("int32")

            # Rating bucket
            rating_idx = np.select(
                [score >= 95, score >= 88, score >= 80, score >= 70],
                [0, 1, 2, 3],
                default=4,
            )
            rating = RATINGS[rating_idx]
            rating_sort = np.vectorize(RATING_SORT.get)(rating).astype("int32")

            source = np.array(["EcoSure", "Steritech", "Internal", "Rentokil"])[rng.integers(0, 4, n)]

            df = pd.DataFrame({
                "BrandSequence": grid["BrandSequence"].astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "CalendarDate": grid["CalendarDate"],
                "CurrentFoodSafetyAudit": current_audit,
                "FoodSafetyRating": rating,
                "FoodSafetyRatingSort": rating_sort,
                "FoodSafetyCriticals": criticals,
                "FoodSafetyScore": score.astype("float32"),
                "FoodSafetyAudits": audits,
            })
            # Add audit failures column at end (schema had FieldAuditFailures separately on Field Audits)
            # Wait — Food Safety schema doesn't have failures column; keep df as-is.
            _ = failures  # unused for this table; retained for clarity
            w.write(df)
            total += len(df)
    return total
