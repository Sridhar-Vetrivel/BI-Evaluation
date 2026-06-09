"""Holds dimension PK arrays in memory so fact generators can sample FKs without
re-reading Parquet. Lightweight — only keys are stored.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Registry:
    brand_keys: np.ndarray = field(default_factory=lambda: np.array([], dtype=np.int64))
    unit_keys: np.ndarray = field(default_factory=lambda: np.array([], dtype=np.int64))
    date_index: pd.DatetimeIndex = field(default_factory=lambda: pd.DatetimeIndex([]))

    # Brand-level "personality" attributes, indexed positionally with brand_keys
    brand_personality: pd.DataFrame = field(default_factory=pd.DataFrame)

    # Per-unit attributes needed by some facts (e.g. open date filters)
    unit_open_date: dict[int, pd.Timestamp] = field(default_factory=dict)
    unit_close_date: dict[int, pd.Timestamp] = field(default_factory=dict)
    unit_brand: dict[int, int] = field(default_factory=dict)  # SBRSequence -> BrandSequence


REGISTRY = Registry()
