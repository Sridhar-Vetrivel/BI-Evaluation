"""Guest Satisfaction — survey responses and top-box scores across 5 attributes."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.fact_base import attach_brand_personality, build_grid, iter_year_chunks
from ..core.rng import rng_for
from ..core.writers import Timer, stream_writer

COMP_VALUES = np.array(["Comp", "Non-Comp"], dtype=object)


def generate() -> int:
    rng = rng_for("GuestSat")
    total = 0
    with stream_writer("Guest Satisfaction") as w, Timer("Guest Satisfaction"):
        for chunk_dates in iter_year_chunks():
            grid = build_grid(chunk_dates)
            grid = attach_brand_personality(grid)
            n = len(grid)
            if n == 0:
                continue

            gs_rate = grid["gs_top_rate"].to_numpy()

            surveys = rng.poisson(15, n).astype("int32")  # ~15 surveys/day/unit

            def attr(responses_factor: float, top_rate_offset: float = 0.0):
                resp = (surveys * rng.uniform(0.7, 1.0, n) * responses_factor).round().astype("int32")
                rate = (gs_rate + rng.normal(0, 0.04, n) + top_rate_offset).clip(0.1, 0.99)
                tops = (resp * rate).round().astype("int32")
                return resp, tops

            friend_resp, friend_top = attr(0.95, 0.02)
            clean_resp, clean_top = attr(0.92, -0.02)
            qual_resp, qual_top = attr(0.97, 0.0)
            speed_resp, speed_top = attr(0.88, -0.05)
            acc_resp, acc_top = attr(0.85, 0.03)

            # Overall TopScores: union heuristic — avg of attribute top counts
            top_scores = ((friend_top + clean_top + qual_top + speed_top + acc_top) / 5).round().astype("int32")

            # Alerts when speed_top rate is very low
            alerts = ((speed_top / np.maximum(speed_resp, 1)) < 0.5).astype("int32")
            escalations = (alerts & (rng.random(n) < 0.25)).astype("int32")

            comp = COMP_VALUES[(rng.random(n) < 0.85).astype(int) ^ 1]

            df = pd.DataFrame({
                "BrandSequence": grid["BrandSequence"].astype("int64"),
                "SBRSequence": grid["SBRSequence"].astype("int64"),
                "CalendarDate": grid["CalendarDate"],
                "Surveys": surveys,
                "TopScores": top_scores,
                "FriendlinessTopScores": friend_top,
                "FriendlinessResponses": friend_resp,
                "CleanlinessTopScores": clean_top,
                "CleanlinessResponses": clean_resp,
                "QualityTopScores": qual_top,
                "QualityResponses": qual_resp,
                "SpeedTopScores": speed_top,
                "SpeedResponses": speed_resp,
                "AccuracyTopScores": acc_top,
                "AccuracyResponses": acc_resp,
                "Alerts": alerts,
                "Escalations": escalations,
                "Comp": comp,
            })
            w.write(df)
            total += len(df)
    return total
