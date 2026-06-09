"""Brand Targets — monthly grain at (BrandSequence, CalendarDate).

CalendarDate is the first-of-month for each target month.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.registry import REGISTRY
from ..core.rng import rng_for
from ..core.settings import DATE_END, DATE_START
from ..core.writers import Timer, write_full


def generate() -> int:
    rng = rng_for("BrandTargets")
    months = pd.date_range(DATE_START, DATE_END, freq="MS").date  # month-start
    brand_keys = REGISTRY.brand_keys
    pers = REGISTRY.brand_personality

    with Timer("Brand Targets"):
        n_brands = len(brand_keys)
        n_months = len(months)
        n = n_brands * n_months

        brand_col = np.repeat(brand_keys, n_months)
        date_col = np.tile(months, n_brands)

        # Look up personality per row
        baseline = pers.loc[brand_col, "baseline_daily_sales"].to_numpy()
        digital = pers.loc[brand_col, "digital_share"].to_numpy()
        loyalty_adoption = pers.loc[brand_col, "loyalty_adoption"].to_numpy()
        gs = pers.loc[brand_col, "gs_top_rate"].to_numpy()
        avg_check = pers.loc[brand_col, "avg_check"].to_numpy()

        # Monthly target sales = baseline * 30 days * #units-per-brand-proxy (use 80)
        rep_target = (baseline * 30 * 80 * rng.uniform(0.95, 1.10, n)).round(2)
        gc_target = (rep_target * 0.03 * rng.uniform(0.9, 1.1, n)).round(2)
        offprem_target = (rep_target * digital * rng.uniform(0.9, 1.1, n)).round(2)
        loyalty_enroll_target = (rep_target / np.maximum(avg_check, 1) * loyalty_adoption * 0.02).round(0)
        gs_top_target = (gs * 100 * rng.uniform(0.95, 1.05, n)).round(1)
        gs_survey_target = (rng.uniform(400, 1500, n)).round(0).astype("int64")

        df = pd.DataFrame({
            "BrandSequence": brand_col.astype("int64"),
            "CalendarDate": date_col,
            "GiftCardSalesTarget": gc_target.astype("float32"),
            "LoyaltyEnrollmentTarget": loyalty_enroll_target.astype("float32"),
            "ReportedSalesTarget": rep_target.astype("float32"),
            "GuestFocusTopScoreTarget": gs_top_target.astype("float32"),
            "GuestFocusSurveyTarget": gs_survey_target,
            "OffPremiseTarget": offprem_target.astype("float32"),
        })

    return write_full("Brand Targets", df)
