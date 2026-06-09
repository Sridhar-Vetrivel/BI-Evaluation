"""Post-generation integrity checks using DuckDB (zero-copy on Parquet files)."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from .settings import PARQUET_DIR, SUMMARY_PATH
from .writers import parquet_path


def _exists(table: str) -> bool:
    return parquet_path(table).exists()


def run_validations() -> dict:
    con = duckdb.connect()
    results: dict[str, dict] = {}

    # Register parquet files as views
    for p in PARQUET_DIR.glob("*.parquet"):
        view = p.stem
        con.execute(f"CREATE OR REPLACE VIEW {view} AS SELECT * FROM read_parquet('{p.as_posix()}')")

    # 1. Row counts
    counts = {}
    for p in PARQUET_DIR.glob("*.parquet"):
        view = p.stem
        n = con.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
        size_mb = p.stat().st_size / (1024 * 1024)
        counts[view] = {"rows": int(n), "size_mb": round(size_mb, 2)}
    results["row_counts"] = counts

    # 2. PK uniqueness on dimensions
    pk_checks = {}
    pk_map = {
        "brand": ["BrandSequence"],
        "unit": ["SBRSequence"],
        "dimdate": ["CalendarDate"],
    }
    for view, keys in pk_map.items():
        if not (PARQUET_DIR / f"{view}.parquet").exists():
            continue
        cols = ", ".join(keys)
        q = f"SELECT COUNT(*) - COUNT(DISTINCT ({cols})) FROM {view}"
        dups = con.execute(q).fetchone()[0]
        pk_checks[view] = {"pk": keys, "duplicates": int(dups)}
    results["pk_checks"] = pk_checks

    # 3. FK integrity for facts
    fk_checks = {}
    fact_fks = {
        # fact_view: [(col, dim_view, dim_col), ...]
        "availability": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "brand_targets": [("BrandSequence", "brand", "BrandSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "catering": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "digital_sales": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "field_audits": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "food_safety": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "gift_cards": [("CardBrandSequence", "brand", "BrandSequence"), ("StoreBrandSequence", "brand", "BrandSequence"), ("MergedBrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "guest_satisfaction": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "loyalty": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "remodels": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "reported_sales": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
        "unit_ranking_base": [("BrandSequence", "brand", "BrandSequence"), ("SBRSequence", "unit", "SBRSequence"), ("CalendarDate", "dimdate", "CalendarDate")],
    }
    for fact, fks in fact_fks.items():
        if not (PARQUET_DIR / f"{fact}.parquet").exists():
            continue
        per_fact = {}
        for col, dim, dim_col in fks:
            if not (PARQUET_DIR / f"{dim}.parquet").exists():
                continue
            q = f"SELECT COUNT(*) FROM {fact} f WHERE f.{col} NOT IN (SELECT {dim_col} FROM {dim})"
            orphans = con.execute(q).fetchone()[0]
            per_fact[f"{col} -> {dim}.{dim_col}"] = int(orphans)
        fk_checks[fact] = per_fact
    results["fk_checks"] = fk_checks

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(results, indent=2, default=str))
    return results


if __name__ == "__main__":
    r = run_validations()
    print(json.dumps(r, indent=2, default=str))
