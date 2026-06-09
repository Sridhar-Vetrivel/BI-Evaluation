# Synthetic Data Generation Plan — UDI Model Tables

**Project:** Enterprise-scale synthetic data generation for the UDI dimensional model
**Source Schema:** `UDI Model Tables.xlsx`
**Target Consumers:** AtScale semantic layer, Tableau, Power BI
**Author:** Generated for BI benchmarking & semantic model testing
**Date:** 2026-05-24

---

## 1. Goal

Take the OLAP/dimensional schema described in `UDI Model Tables.xlsx` (schema only — no data) and produce a realistic, enterprise-scale synthetic dataset suitable for:

- AtScale semantic layer testing
- Tableau vs Power BI evaluation
- Performance benchmarking
- Query optimization testing
- Dashboard and visualization analysis

The output dataset must look and behave like a real enterprise data warehouse: realistic distributions, valid hierarchies, intact referential integrity, time-series seasonality, and BI-friendly cardinalities.

---

## 2. Step-by-Step Approach

### Step 1 — Analyze the Excel File

- Read `UDI Model Tables.xlsx` using `pandas` + `openpyxl`.
- Detect all sheets.
- For each sheet, extract:
  - Table names
  - Column names
  - Datatypes
  - Primary keys
  - Foreign keys
  - Relationships (declared)
  - Nullable columns
  - Measures vs attributes
  - Fact vs dimension classification
- Build a **metadata dictionary** capturing every table, column, and relationship.
- **Infer missing relationships** by naming convention, e.g.:
  - `CustomerID` → `DimCustomer.CustomerID`
  - `ProductKey` → `DimProduct.ProductKey`
  - `*Key` / `*ID` columns appearing in fact tables → matching dim PK.

### Step 2 — Build a Data Generation Strategy

**Dimension tables**
- Realistic, unique values.
- Hierarchies preserved (e.g., Country → Region → City; Category → Subcategory → Product).
- Use `Faker` for: names, addresses, cities, countries, emails, phone numbers, company names.
- Consistent business semantics across dims (e.g., currencies match country).

**Fact tables**
- Millions of rows.
- Weighted distributions (Pareto / log-normal for revenue, normal for quantities).
- Realistic business behavior: most customers small, a few large; most products low-velocity, a few hits.
- Time-series patterns: yearly growth, weekly seasonality, monthly cycles, holiday peaks.
- Preserve all dimensional FK references.

**Slowly Changing Dimensions**
- SCD Type 2 support for relevant dims (e.g., Customer address changes, Employee role changes) with `EffectiveDate`, `EndDate`, `IsCurrent`.

### Step 3 — Data Scale Requirements

| Bucket | Volume |
|---|---|
| Small dimensions (Date, Currency, Region, etc.) | 1K – 50K rows |
| Medium dimensions (Customer, Product, Employee) | 100K – 1M rows |
| Large fact tables (Sales, Transactions, Events) | 5M – 50M rows |
| Date dimension | ≥ 10 years of daily grain |

Centralized configuration via:

```python
ROW_SCALE_FACTOR  = 1.0   # global multiplier
FACT_TABLE_SIZE   = 10_000_000
DIM_TABLE_SIZE    = 500_000
DATE_RANGE_YEARS  = 10
```

### Step 4 — Performance Optimization

- Use `numpy` vectorization for bulk numeric/date columns.
- Batch `Faker` generation; cache reusable pools (cities, company suffixes).
- Use `pyarrow` to stream-write Parquet in row-group chunks.
- Use `multiprocessing` for independent fact-row chunks.
- **No Python row-by-row loops** for fact tables.

### Step 5 — Output Format & Project Structure

```
udi_data_gen/
├── config/
│   └── settings.py           # scale factors, paths, seed
├── generators/
│   ├── __init__.py
│   ├── base.py               # BaseGenerator
│   ├── dim_date.py
│   ├── dim_customer.py
│   ├── dim_product.py
│   ├── dim_employee.py
│   ├── dim_geography.py
│   ├── ...                   # one per dim
│   └── fact_sales.py
├── core/
│   ├── schema_loader.py      # parse Excel -> metadata dict
│   ├── relationship_manager.py
│   ├── writers.py            # csv / parquet / sql
│   └── validators.py         # PK/FK / null / range checks
├── output/
│   ├── csv/
│   ├── parquet/
│   └── sql/
├── orchestrator.py           # master entry point
├── requirements.txt
└── README.md
```

Parquet preferred for large fact tables; CSV mirrored for portability; SQL `INSERT` files only for small dims.

### Step 6 — Data Quality Rules

- ✅ No FK violations
- ✅ No duplicate PKs
- ✅ Realistic distributions (skewed, not uniform)
- ✅ Controlled null percentages per column
- ✅ Valid date ranges
- ✅ Logical measure alignment
- ✅ No impossible values

Examples enforced:
- `Revenue > 0`
- `Quantity` within realistic bounds
- `OrderDate ≤ ShipDate`
- `EmployeeAge ∈ [18, 65]`
- `UnitPrice × Quantity = Revenue` (with discount allowance)

### Step 7 — BI Optimization

The dataset will deliberately include features that stress BI engines:

- Skewed distributions (Pareto customers, hit-product effect)
- High-cardinality columns (e.g., transaction IDs, customer emails)
- Large dimensions for join-cost testing
- Deep hierarchies (Geography 4 levels, Product 3 levels, Org chart)
- Many-to-many relationships (Customer ↔ Promotion, Product ↔ Tag)
- Incremental refresh scenarios (partition by month)
- Historical snapshots (SCD2 history rows)

Why: matters for **Power BI VertiPaq compression**, **Tableau Hyper extracts**, and **AtScale aggregate caching**.

### Step 8 — Final Outputs Required

1. Complete Python codebase under `udi_data_gen/`
2. `README.md` with execution steps
3. `requirements.txt`
4. Schema relationship diagram (Mermaid/PNG)
5. Data volume summary (`output/_summary.json`)
6. Sample outputs (first 1K rows per table)
7. Execution instructions

### Step 9 — Execution

- Run `python orchestrator.py`
- Generate all dim + fact files
- Validate row counts and FK integrity
- Print generation summary (rows, MB, duration per table)

---

## 3. Technical Stack

**Mandatory**
- `pandas`
- `numpy`
- `faker`
- `pyarrow`
- `openpyxl`

**Optional (used where it helps)**
- `polars` — fast group-bys for validation
- `duckdb` — in-process SQL validation of FKs/PKs
- `dask` — only if a single fact exceeds RAM
- `tqdm` — progress bars

---

## 4. Quality Bar

The generated data must look realistic enough for:

- Executive dashboards
- KPI reporting
- Drill-through analysis
- Semantic model testing
- Aggregation testing
- BI benchmark comparisons

Production-quality code: typed where useful, deterministic via seed, idempotent reruns, clear logging, no hard-coded paths.

---

## 5. Next Action

➡️ **Analyze `UDI Model Tables.xlsx`** — enumerate sheets, columns, datatypes, PK/FK — and produce the concrete `metadata.json` before writing any generator code.
