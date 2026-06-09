"""Central configuration for the UDI synthetic data generator."""

from __future__ import annotations

import os
from pathlib import Path

# ---------- Paths ----------
ROOT = Path(__file__).resolve().parents[2]
PKG_ROOT = ROOT / "udi_data_gen"
METADATA_PATH = PKG_ROOT / "metadata.json"
OUTPUT_DIR = PKG_ROOT / "output"
PARQUET_DIR = OUTPUT_DIR / "parquet"
SUMMARY_PATH = OUTPUT_DIR / "_summary.json"

for d in (PARQUET_DIR,):
    d.mkdir(parents=True, exist_ok=True)

# ---------- Determinism ----------
SEED = int(os.environ.get("UDI_SEED", "42"))

# ---------- Scale (Mid: ~15M rows per daily fact) ----------
ROW_SCALE_FACTOR = float(os.environ.get("UDI_SCALE", "1.0"))

# Date dimension
DATE_START = "2016-01-01"
DATE_END = "2025-12-31"  # 10 years inclusive

# Dimensions
BRAND_COUNT = int(50 * ROW_SCALE_FACTOR)
UNIT_COUNT = int(4_000 * ROW_SCALE_FACTOR)

# Fact-row write chunking (one year per chunk keeps memory bounded)
FACT_CHUNK_DAYS = 365

# Parquet row-group size (rows per group, balances scan speed vs file size)
PARQUET_ROW_GROUP_SIZE = 250_000

# Smoke mode: tiny scale for quick sanity-checks (UDI_SMOKE=1)
if os.environ.get("UDI_SMOKE") == "1":
    BRAND_COUNT = 10
    UNIT_COUNT = 50
    DATE_START = "2024-01-01"
    DATE_END = "2024-12-31"
