"""Deterministic RNG factory — every table gets an independent numpy Generator
seeded from the global SEED + a table-name hash, so order/parallelism is
reproducible without coupling tables together.
"""

from __future__ import annotations

import hashlib

import numpy as np

from .settings import SEED


def rng_for(label: str) -> np.random.Generator:
    h = hashlib.md5(label.encode()).digest()
    sub_seed = int.from_bytes(h[:8], "little") ^ SEED
    return np.random.default_rng(sub_seed)
