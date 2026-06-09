# UDI Synthetic Data Generator

Generates an enterprise-scale, realistic synthetic dataset for the **UDI dimensional model** (15 tables — 4 dims + 11 facts) defined in `UDI Model Tables.xlsx`. Output is Parquet, ready for AtScale, Power BI, and Tableau.

---

## Quickstart

```powershell
# from the repo root
pip install -r udi_data_gen/requirements.txt

# 1) Smoke test (~10 brands, 50 units, 1 year — finishes in seconds)
$env:UDI_SMOKE = "1"; python -m udi_data_gen.orchestrator

# 2) Full Mid-scale run (~15M rows per daily fact)
Remove-Item Env:UDI_SMOKE
python -m udi_data_gen.orchestrator
```

Output lands in `udi_data_gen/output/parquet/` (one file per table) and a summary in `udi_data_gen/output/_summary.json`.

---

## What you get

| Table | Role | Grain | Approx rows (Mid scale) |
|---|---|---|---|
| `dimdate` | dim | day | 3,653 |
| `brand` | dim | brand | 50 |
| `unit` | dim | store | 4,000 |
| `unit_ranking_base` | derived dim | unit × brand × month | ~480K |
| `brand_targets` | fact | brand × month | 6K |
| `availability` | fact | brand × unit × day | ~14.6M |
| `catering` | fact | brand × unit × day | ~14.6M |
| `digital_sales` | fact | brand × unit × day | ~14.6M |
| `field_audits` | fact | brand × unit × day | ~14.6M |
| `food_safety` | fact | brand × unit × day | ~14.6M |
| `gift_cards` | fact | (3×brand) × unit × day | ~14.6M |
| `guest_satisfaction` | fact | brand × unit × day | ~14.6M |
| `loyalty` | fact | brand × unit × day | ~14.6M |
| `remodels` | fact | brand × unit × day | ~14.6M |
| `reported_sales` | fact | brand × unit × day | ~14.6M |

Total ≈ **150M rows**, all referentially consistent.

---

## Architecture

```
udi_data_gen/
├── metadata.json                # parsed schema (source of truth)
├── core/
│   ├── parse_schema.py          # Excel -> metadata.json
│   ├── settings.py              # scale, seed, paths
│   ├── rng.py                   # per-table deterministic Generator
│   ├── registry.py              # in-memory dim keys + brand "personality"
│   ├── fact_base.py             # year-chunked (Unit x Date) grid builder
│   ├── writers.py               # streaming Parquet writer
│   └── validators.py            # DuckDB PK/FK checks
├── generators/
│   ├── dim_date.py
│   ├── dim_brand.py             # also emits brand-personality registry
│   ├── dim_unit.py              # also emits unit->brand map + open/close dates
│   ├── dim_unit_ranking_base.py # monthly snapshot, derived from Brand + Unit
│   ├── fact_availability.py
│   ├── fact_brand_targets.py    # monthly grain
│   ├── fact_catering.py
│   ├── fact_digital_sales.py
│   ├── fact_field_audits.py
│   ├── fact_food_safety.py
│   ├── fact_gift_cards.py       # triple-Brand FK
│   ├── fact_guest_satisfaction.py
│   ├── fact_loyalty.py
│   ├── fact_remodels.py
│   └── fact_reported_sales.py
├── orchestrator.py              # entry point
├── requirements.txt
└── README.md
```

### Design choices

- **Deterministic.** Each table seeds its own numpy `Generator` from `SEED ^ hash(table_name)`. Reruns produce byte-identical output.
- **Vectorized.** No row-by-row Python loops in fact generation; chunked one calendar year at a time.
- **Brand personality.** Each brand has hidden attributes (`baseline_daily_sales`, `food_safety_quality`, `loyalty_adoption`, `digital_share`, `catering_share`, `avg_check`, `gs_top_rate`). All facts use these so the data tells a coherent brand-by-brand story across tables.
- **Active-store filter.** Facts only generate rows for `OpenDate <= day <= CloseDate`, mimicking a realistic store rollout / closure pattern.
- **Streaming Parquet.** Each fact writes year-sized row groups (250K rows/group) — no memory blowup, fast scans for BI tools.
- **DuckDB validation.** Post-run checks PK uniqueness on dims and FK integrity on every fact (zero-copy over Parquet).

---

## Scale knobs

Environment variables override defaults in `core/settings.py`:

| Env var | Default | Effect |
|---|---|---|
| `UDI_SCALE` | `1.0` | Multiplies `BRAND_COUNT` (50) and `UNIT_COUNT` (4000). Try `0.25` for ~4M/fact. |
| `UDI_SEED` | `42` | Master seed for determinism. |
| `UDI_SMOKE` | unset | If `1`: 10 brands, 50 units, 1 year — generates in seconds. Use first. |

Date range is set in `settings.py` (`DATE_START`, `DATE_END`).

---

## BI-tool consumption

- **Power BI / Tableau:** Open the `output/parquet/` folder, connect to each `.parquet` file as a table, build relationships using the dim keys (`BrandSequence`, `SBRSequence`, `CalendarDate`).
- **AtScale:** Point a connection at the folder (or load to your warehouse) and model each fact at its declared grain; the FKs are all clean integers/dates.
- **DuckDB / Polars / Spark:** Read with `read_parquet('output/parquet/*.parquet')`.

---

## Validation

After every run, `output/_summary.json` contains:

- `row_counts` — rows + file size per table
- `pk_checks` — duplicate-PK count per dimension (must be 0)
- `fk_checks` — orphan-row count per fact-FK (must be 0)
- `generation` — per-table wall-clock and throughput
- `totals` — combined rows / MB / seconds

Re-run validations alone (without regenerating data):

```powershell
python -m udi_data_gen.core.validators
```
