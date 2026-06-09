"""Master orchestrator: generates every table in dependency order, then runs
validations and prints a summary.

Run:
    python -m udi_data_gen.orchestrator           # full Mid-scale
    UDI_SMOKE=1 python -m udi_data_gen.orchestrator   # tiny smoke test
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable

from .core.settings import BRAND_COUNT, DATE_END, DATE_START, SUMMARY_PATH, UNIT_COUNT
from .core.validators import run_validations
from .core.writers import file_size_mb
from .generators import (
    dim_brand,
    dim_date,
    dim_unit,
    dim_unit_ranking_base,
    fact_availability,
    fact_brand_targets,
    fact_catering,
    fact_digital_sales,
    fact_field_audits,
    fact_food_safety,
    fact_gift_cards,
    fact_guest_satisfaction,
    fact_loyalty,
    fact_remodels,
    fact_reported_sales,
)

# Order matters: dims first (Brand before Unit so unit-brand assignment works),
# DimDate before anything that uses date chunks. Unit Ranking Base after Unit.
PIPELINE: list[tuple[str, Callable[[], int]]] = [
    ("DimDate", dim_date.generate),
    ("Brand", dim_brand.generate),
    ("Unit", dim_unit.generate),
    ("Unit Ranking Base", dim_unit_ranking_base.generate),
    ("Brand Targets", fact_brand_targets.generate),
    ("Availability", fact_availability.generate),
    ("Catering", fact_catering.generate),
    ("Digital Sales", fact_digital_sales.generate),
    ("Field Audits", fact_field_audits.generate),
    ("Food Safety", fact_food_safety.generate),
    ("Gift Cards", fact_gift_cards.generate),
    ("Guest Satisfaction", fact_guest_satisfaction.generate),
    ("Loyalty", fact_loyalty.generate),
    ("Remodels", fact_remodels.generate),
    ("Reported Sales", fact_reported_sales.generate),
]


def main() -> None:
    t_start = time.perf_counter()
    print("=" * 78)
    print(f"UDI Synthetic Data Generator | brands={BRAND_COUNT}  units={UNIT_COUNT}  dates={DATE_START} -> {DATE_END}")
    print("=" * 78)

    results: list[dict] = []
    for name, fn in PIPELINE:
        t0 = time.perf_counter()
        rows = fn()
        elapsed = time.perf_counter() - t0
        size = file_size_mb(name)
        rate = rows / elapsed if elapsed > 0 else 0
        print(f"  {name:22s}  rows={rows:>12,}  {size:>8.2f} MB  {elapsed:>7.2f}s  ({rate:>10,.0f} rows/s)")
        results.append({"table": name, "rows": rows, "size_mb": round(size, 2), "seconds": round(elapsed, 2)})

    print("-" * 78)
    print("Running validations (DuckDB)...")
    v = run_validations()
    bad_pks = sum(c["duplicates"] for c in v["pk_checks"].values())
    bad_fks = sum(
        orphans for table in v["fk_checks"].values() for orphans in table.values()
    )
    print(f"  PK duplicates : {bad_pks}")
    print(f"  FK orphans    : {bad_fks}")

    total_time = time.perf_counter() - t_start
    total_rows = sum(r["rows"] for r in results)
    total_mb = sum(r["size_mb"] for r in results)
    print("-" * 78)
    print(f"TOTAL  rows={total_rows:,}  size={total_mb:.1f} MB  elapsed={total_time:.1f}s")
    print(f"Validation summary written to: {SUMMARY_PATH}")

    # Augment summary with per-table generation timings
    full_summary = json.loads(SUMMARY_PATH.read_text())
    full_summary["generation"] = results
    full_summary["totals"] = {
        "rows": total_rows,
        "size_mb": round(total_mb, 2),
        "seconds": round(total_time, 2),
    }
    SUMMARY_PATH.write_text(json.dumps(full_summary, indent=2, default=str))


if __name__ == "__main__":
    main()
