"""Brand dimension — small (50 by default) with per-brand 'personality' that
drives the realism of all downstream fact generators.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.registry import REGISTRY
from ..core.rng import rng_for
from ..core.settings import BRAND_COUNT
from ..core.writers import write_full

CONCEPTS = [
    "Quick Serve", "Fast Casual", "Casual Dining", "Family Dining",
    "Coffee & Bakery", "Pizza", "Seafood", "Steakhouse", "Asian", "Mexican",
]
CATEGORIES = ["Restaurant", "Cafe", "Bar & Grill", "Bakery", "Ice Cream"]
SOURCES = ["Internal", "EcoSure", "Steritech", "Rentokil"]
TIMEFRAMES = ["TTM", "YTD", "Last90", "Last30"]


def generate() -> int:
    rng = rng_for("Brand")
    n = BRAND_COUNT
    brand_seq = np.arange(1_000_001, 1_000_001 + n, dtype="int64")

    # Realistic brand naming — repeatable, recognizable
    prefixes = ["Sun", "Blue", "Iron", "Red", "Golden", "Crown", "Maple", "Coastal",
                "Urban", "Prairie", "Summit", "Harbor", "Copper", "Silver", "Heritage"]
    cores = ["Grill", "Kitchen", "Diner", "Cafe", "House", "Roast", "Catch",
             "Table", "Oven", "Bistro", "Tap", "Crust", "Burger", "Bowl", "Bean"]
    suffixes = ["", " Co.", " & Co.", " Bros", " Eatery", " Group", ""]

    # Build unique brand names
    used: set[str] = set()
    names: list[str] = []
    while len(names) < n:
        nm = f"{rng.choice(prefixes)} {rng.choice(cores)}{rng.choice(suffixes)}"
        if nm not in used:
            used.add(nm)
            names.append(nm)

    df = pd.DataFrame({
        "BrandSequence": brand_seq,
        "BrandName": names,
        "BrandType": rng.choice(["Franchise", "Company", "Hybrid"], n, p=[0.7, 0.2, 0.1]),
        "InternationalFlag": rng.choice(["Y", "N"], n, p=[0.25, 0.75]),
        "BrandSort": (np.arange(n) + 1).astype("int32"),
        "Concept": rng.choice(CONCEPTS, n),
        "BrandCategory": rng.choice(CATEGORIES, n),
        "BrandFoodSafetySource": rng.choice(SOURCES, n),
        "BrandScorecardRankingTimeframe": rng.choice(TIMEFRAMES, n),
    })

    # ---------- Brand personality (not persisted; used by fact gens) ----------
    personality = pd.DataFrame({
        "BrandSequence": brand_seq,
        # Average daily net-sales baseline per unit, in $
        "baseline_daily_sales": rng.uniform(1_200, 6_500, n).round(2),
        # Food-safety quality: probability a daily audit passes critical-free
        "food_safety_quality": rng.uniform(0.78, 0.99, n).round(3),
        # Loyalty program adoption (fraction of guests enrolled)
        "loyalty_adoption": rng.uniform(0.05, 0.45, n).round(3),
        # Share of sales that come through digital channels (1P + 3P)
        "digital_share": rng.uniform(0.10, 0.55, n).round(3),
        # Share of sales coming from catering
        "catering_share": rng.uniform(0.02, 0.18, n).round(3),
        # Avg guest check ($)
        "avg_check": rng.uniform(8.0, 32.0, n).round(2),
        # Guest-satisfaction baseline top-score rate
        "gs_top_rate": rng.uniform(0.55, 0.88, n).round(3),
    })
    REGISTRY.brand_keys = brand_seq
    REGISTRY.brand_personality = personality.set_index("BrandSequence")

    return write_full("Brand", df)
