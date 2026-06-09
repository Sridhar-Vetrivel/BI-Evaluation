# Tableau Build Guide — GoTo Foods Catering Analytics Transformation

End-to-end instructions to build the **5-page Catering Analytics Transformation** (per `catering_analytics_transformation.md`) in Tableau Desktop against the synthesized UDI dataset. Companion to `POWERBI_BUILD_GUIDE.md` — same data, same KPIs, same pages, side-by-side parity in mind.

Source dataset:
```
c:\Users\sridhar.vetrivel\OneDrive - psiog.com\Accounts\GTF\TableAU Analysis\udi_data_gen\output\parquet\
```

> **Important — Tableau Desktop has no first-class local Parquet connector.** Three real options:
>
> | Path | When to use | Setup | Live vs Extract |
> |---|---|---|---|
> | **A. Convert Parquet → Hyper** (recommended) | Default. Best perf, simplest auth. | 5 min, automated | Acts like an extract |
> | **B. DuckDB via JDBC** | When evaluating Tableau Live mode | 15 min | Live |
> | **C. Parquet → CSV** | Last resort. Slow, large, weak types. | 5 min | Extract |
>
> This guide treats **Path A as the default**. Path B documented at the end.

## The 5 dashboards we're building

| Dashboard | Audience | Decision it enables |
|---|---|---|
| **1. Catering Health Scorecard** | Brand Leaders, RVPs | Is catering healthy across the system this period? |
| **2. Channel Intelligence** | Brand Managers, FBCs | Is the 1P/3P mix protecting margin or eroding it? |
| **3. FBC Action Board** | Franchise Business Consultants | Which franchisees need my attention today, and why? |
| **4. Catering Trends (Rebuilt)** | Brand Managers, FBCs | Is the trend real, seasonal, or discount-propped? |
| **5. Marketing ROI View** | Brand Marketing Teams | Are catering incentives generating return or just discounting? |

> **Data-availability note for Dashboard 5.** The transformation doc references a `Catering Marketing Spend` table with `PPP`, `DeliveryFee`, `EZRewards`, `Subtotal`. **The synthetic UDI dataset does not include those fields.** Dashboard 5 uses `ReportedSales.DiscountsCY` as an aggregate spend proxy. Replace the proxy when the real Mktg Spend table is connected.

---

## Prerequisites

1. **Tableau Desktop 2023.3 or later** ([download](https://www.tableau.com/products/desktop/download)). 14-day trial works.
2. **Python 3.10+** (already installed — used to generate the dataset).
3. **`pantab` Python package**:
   ```powershell
   pip install pantab tableauhyperapi
   ```
4. **Tableau Cloud or Tableau Server access** (optional, for the publish phase).

---

## Phase 1 — Convert Parquet to Hyper (Path A)

Tableau's native columnar engine is **Hyper**. One Hyper file per table loads instantly afterward.

### 1.1 Add a converter script to the project

Create `udi_data_gen/core/to_hyper.py`:

```python
"""Convert every Parquet table to a Tableau .hyper file."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pantab

from .settings import PARQUET_DIR

HYPER_DIR = PARQUET_DIR.parent / "hyper"
HYPER_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    files = sorted(PARQUET_DIR.glob("*.parquet"))
    for p in files:
        out = HYPER_DIR / f"{p.stem}.hyper"
        print(f"  {p.name:36s} -> {out.name}")
        df = pd.read_parquet(p)
        pantab.frame_to_hyper(df, out, table=p.stem)
    print(f"\nWrote {len(files)} hyper files to {HYPER_DIR}")


if __name__ == "__main__":
    main()
```

### 1.2 Run it

```powershell
python -m udi_data_gen.core.to_hyper
```

Expected: 15 `.hyper` files in `udi_data_gen/output/hyper/`. For Mid-scale (~118M rows) allow 5–10 minutes.

### 1.3 Verify

```powershell
Get-ChildItem udi_data_gen/output/hyper/ | Sort-Object Length -Descending |
    Select-Object Name, @{n="SizeMB";e={[math]::Round($_.Length/1MB,1)}}
```

---

## Phase 2 — Connect Tableau to the Hyper files

### 2.1 Open the first table

1. Launch Tableau Desktop. Start screen → **Connect → To a File → More…**
2. Select **Tableau Extract (.hyper)**.
3. Browse to `udi_data_gen\output\hyper\catering.hyper` — **start with `catering` because it's the focal fact** for this build.
4. The Data Source pane opens; one table named `catering` appears on the left.

### 2.2 Add all other tables

1. Connections panel → **Add** → choose **Tableau Extract** → browse to `dimdate.hyper` → drag onto canvas.
2. Repeat for all 15 hyper files.

> **Tip:** Add `dimdate`, `brand`, `unit` immediately after `catering` so you can wire relationships as you go. The other facts (`reported_sales`, `digital_sales`, `loyalty`, `guest_satisfaction`, `field_audits`, `food_safety`, `availability`, `brand_targets`, `gift_cards`, `remodels`, `unit_ranking_base`) come last.

### 2.3 Rename tables to CamelCase

Right-click each table on the canvas → **Rename**:

| Hyper table | Rename to |
|---|---|
| `dimdate` | `DimDate` |
| `brand` | `Brand` |
| `unit` | `Unit` |
| `unit_ranking_base` | `UnitRankingBase` |
| `brand_targets` | `BrandTargets` |
| `availability` | `Availability` |
| `catering` | `Catering` |
| `digital_sales` | `DigitalSales` |
| `field_audits` | `FieldAudits` |
| `food_safety` | `FoodSafety` |
| `gift_cards` | `GiftCards` |
| `guest_satisfaction` | `GuestSatisfaction` |
| `loyalty` | `Loyalty` |
| `remodels` | `Remodels` |
| `reported_sales` | `ReportedSales` |

---

## Phase 3 — Build relationships (logical layer)

Drag noodles between tables for star-schema joins. **Catering is the focal fact** for this build.

### 3.1 Standard star — every fact ↔ DimDate / Brand / Unit

| Fact | → DimDate | → Brand | → Unit |
|---|---|---|---|
| Catering | `CalendarDate = CalendarDate` | `BrandSequence = BrandSequence` | `SBRSequence = SBRSequence` |
| ReportedSales | same | same | same |
| Availability | same | same | same |
| DigitalSales | same | same | same |
| FieldAudits | same | same | same |
| FoodSafety | same | same | same |
| GuestSatisfaction | same | same | same |
| Loyalty | same | same | same |
| Remodels | same | same | same |
| UnitRankingBase | same | same | same |
| BrandTargets | `CalendarDate` | `BrandSequence` | *(no Unit)* |
| GiftCards | `CalendarDate` | `StoreBrandSequence = BrandSequence` | `SBRSequence` |

For each noodle, under **Performance Options**:

- **Cardinality:** Many-to-One (fact → dim)
- **Referential Integrity:** *All Records Match* (FK orphans = 0 was verified during generation)

### 3.2 Visual check

Your canvas should look like a star: `DimDate`, `Brand`, `Unit` in the centre, all facts radiating out. `Catering` is the table you'll touch most.

> **Don't double-click and turn relationships into joins.** Double-clicking opens the *physical layer* (SQL-style joins). The build works entirely in the logical layer.

---

## Phase 4 — Field configuration

### 4.1 Hide fields not used by authors

For every fact, right-click → **Hide**:

- `BrandSequence`, `SBRSequence`, `CalendarDate` in all facts
- `GiftCards`: also `CardBrandSequence`, `MergedBrandSequence`
- `Brand`: `BrandSequence`, `BrandSort`
- `DimDate`: `DateKey`

### 4.2 Critical Unit fields to keep visible (for FBC Action Board)

- `Unit.FranchiseBusinessConsultant` — primary filter for Dashboard 3
- `Unit.Franchisee`, `Unit.FranchiseeGroup`, `Unit.FranchisePartner`
- `Unit.VenueTradNonTradByFreq`
- `Unit.NextRemodelDate` — used by the Remodel-Overdue flag

### 4.3 Geographic roles on Unit

| Field | Geographic Role |
|---|---|
| `Unit.Country` | Country/Region |
| `Unit.State` | State/Province |
| `Unit.City` | City |
| `Unit.ZipCode` | ZIP Code/Postcode |
| `Unit.Latitude` | Latitude |
| `Unit.Longitude` | Longitude |

### 4.4 Default formats & aggregations

For each measure: **Default Properties → Number Format** → Currency $ 0 dp for sales, Percentage 1 dp for ratios.

For score fields (`FoodSafetyScore`, `FieldAuditScore`): **Default Aggregation → AVERAGE**. All other fact measures: **SUM**.

---

## Phase 5 — Calculated fields (catering-focused)

Right-click in Data pane → **Create Calculated Field**. Group everything under a `_Measures` folder (right-click any field → **Folders → Create Folder**).

### 5.1 Core catering KPIs

```
// Total Catering Sales
SUM([Catering].[FirstPartyNetSales]) + SUM([Catering].[ThirdPartyNetSales])

// Catering 1P Sales
SUM([Catering].[FirstPartyNetSales])

// Catering 3P Sales
SUM([Catering].[ThirdPartyNetSales])

// Catering 1P Share %
[Catering 1P Sales] / [Total Catering Sales]

// Catering 3P Share %
[Catering 3P Sales] / [Total Catering Sales]

// Catering 1P Traffic
SUM([Catering].[FirstPartyTraffic])

// Catering 3P Traffic
SUM([Catering].[ThirdPartyTraffic])

// Catering Total Traffic
[Catering 1P Traffic] + [Catering 3P Traffic]

// Catering 1P Traffic Share %
[Catering 1P Traffic] / [Catering Total Traffic]

// Catering 1P Avg Check
[Catering 1P Sales] / [Catering 1P Traffic]

// Catering 3P Avg Check
[Catering 3P Sales] / [Catering 3P Traffic]

// Catering Blended Avg Check
[Total Catering Sales] / [Catering Total Traffic]
```

### 5.2 Year-over-year (LOD-driven, no PY columns in Catering fact)

We don't store PY catering values, so YoY uses a fixed-year LOD pattern. Create a parameter first:

- **Year Selector** (Integer, range 2016–2026, default = current year — value to match the system date the data was generated against).

```
// Catering Sales — Current Year
{ FIXED [DimDate].[CalendarDate] :
    SUM(IIF(YEAR([DimDate].[CalendarDate]) = [Year Selector],
            [Catering].[FirstPartyNetSales] + [Catering].[ThirdPartyNetSales], 0))
}

// Catering Sales — Prior Year
{ FIXED [DimDate].[CalendarDate] :
    SUM(IIF(YEAR([DimDate].[CalendarDate]) = [Year Selector] - 1,
            [Catering].[FirstPartyNetSales] + [Catering].[ThirdPartyNetSales], 0))
}

// Catering Sales YoY %
([Catering Sales — Current Year] - [Catering Sales — Prior Year])
    / [Catering Sales — Prior Year]
```

> **Easier alternative:** Use Tableau's built-in **table calc** `% Difference from` against Prior Year as a quick-table-calc on a viz where Year is a dimension. Sufficient for trend charts; use the LOD pattern above when you need YoY as a measure inside a scatter or alert calc.

For the 1P and 3P YoY equivalents, follow the same pattern using `[Catering].[FirstPartyNetSales]` or `[Catering].[ThirdPartyNetSales]` in place of the sum.

```
// Catering 1P YoY %  — concise alternative using SAMEPERIODLASTYEAR-style date filter
// (works on viz with Year on Columns)
(SUM([Catering].[FirstPartyNetSales]) - LOOKUP(SUM([Catering].[FirstPartyNetSales]), -1))
    / LOOKUP(SUM([Catering].[FirstPartyNetSales]), -1)

// Catering Avg Check YoY %
([Catering Blended Avg Check] - LOOKUP([Catering Blended Avg Check], -1))
    / LOOKUP([Catering Blended Avg Check], -1)
```

### 5.3 Comp store catering

```
// Comp Catering Sales (Comp='Comp')
SUM(IIF([Catering].[Comp] = "Comp",
        [Catering].[FirstPartyNetSales] + [Catering].[ThirdPartyNetSales], 0))

// Catering Comp %  — true same-store YoY using ReportedSales CY/PY columns
({ FIXED [Brand].[BrandSequence] :
    SUM(IIF([Catering].[Comp] = "Comp",
            [Catering].[FirstPartyNetSales] + [Catering].[ThirdPartyNetSales], 0)) }
 - LOOKUP({ FIXED [Brand].[BrandSequence] : SUM([ReportedSales].[CateringPY]) }, 0))
 / LOOKUP({ FIXED [Brand].[BrandSequence] : SUM([ReportedSales].[CateringPY]) }, 0)
```

A simpler proxy if the LOD above is slow:

```
// Catering Comp % (simple)
(SUM([ReportedSales].[CateringCY]) - SUM([ReportedSales].[CateringPY]))
    / SUM([ReportedSales].[CateringPY])
```

### 5.4 Cross-table KPIs

```
// Catering Penetration %
[Total Catering Sales] / SUM([ReportedSales].[NetSalesCY])

// Off-Premise Target
SUM([BrandTargets].[OffPremiseTarget])

// Catering Target Attainment %
[Total Catering Sales] / [Off-Premise Target]

// Catering Target Gap $
[Total Catering Sales] - [Off-Premise Target]

// Discounts (Spend Proxy)
SUM([ReportedSales].[DiscountsCY])

// Discount Rate on Catering
[Discounts (Spend Proxy)] / SUM([ReportedSales].[CateringCY])

// Marketing Cost per Catering Order (Proxy)
[Discounts (Spend Proxy)] / [Catering 1P Traffic]

// Loyalty → Catering Conversion
[Total Catering Sales] / SUM([Loyalty].[LoyaltyEarnableSales])

// Digital 1P Sales
SUM([DigitalSales].[FirstPartyNetSales])

// Catering 1P as % of Digital 1P
[Catering 1P Sales] / [Digital 1P Sales]

// Loyalty Enrollments
SUM([Loyalty].[Enrollments])

// Loyalty Sales
SUM([Loyalty].[LoyaltySales])
```

### 5.5 Operational quality (for FBC overlays)

```
// Guest Top Score Rate
SUM([GuestSatisfaction].[TopScores]) / SUM([GuestSatisfaction].[Surveys])

// Speed Top %
SUM([GuestSatisfaction].[SpeedTopScores]) / SUM([GuestSatisfaction].[SpeedResponses])

// Accuracy Top %
SUM([GuestSatisfaction].[AccuracyTopScores]) / SUM([GuestSatisfaction].[AccuracyResponses])

// Field Audit Score Avg
AVG([FieldAudits].[FieldAuditScore])

// Field Audit Failures
SUM([FieldAudits].[FieldAuditFailures])

// Food Safety Criticals
SUM([FoodSafety].[FoodSafetyCriticals])

// Pickup Days Available
SUM([Availability].[PickupAvailable])

// Dispatch Days Available
SUM([Availability].[DispatchAvailable])

// Active Stores
COUNTD([Catering].[SBRSequence])
```

### 5.6 Store-health flags (the heart of Dashboard 3)

Each flag returns a string used for color encoding on cards and matrices. Build them at the granularity Tableau will see on Dashboard 3 (typically `Franchisee` or `UnitNumber`).

```
// F1: 1P Channel Abandonment — 1P down >25% YoY AND 3P up or flat
IF [Catering 1P YoY %] < -0.25 AND [Catering 3P YoY %] >= 0
THEN "1P Abandonment Risk" END

// F2: Platform Over-Dependency — 3P share >75%
IF [Catering 3P Share %] > 0.75
THEN "Platform Over-Dependent" END

// F3: Check Size Erosion — avg check down >15% YoY
IF [Catering Avg Check YoY %] < -0.15
THEN "Check Size Eroding" END

// F4: Catering + Ops Dual Risk — catering comp <-10% AND audit score <75
IF [Catering Comp %] < -0.10 AND [Field Audit Score Avg] < 75
THEN "ESCALATE — Dual Risk" END

// F5: Discount-Propped Growth — catering up but discounts growing faster
IF (SUM([ReportedSales].[CateringCY]) - SUM([ReportedSales].[CateringPY])) > 0
   AND (
        (SUM([ReportedSales].[DiscountsCY]) - SUM([ReportedSales].[DiscountsPY]))
        / SUM([ReportedSales].[DiscountsPY])
       )
   > (
        (SUM([ReportedSales].[CateringCY]) - SUM([ReportedSales].[CateringPY]))
        / SUM([ReportedSales].[CateringPY])
       )
THEN "Hollow Growth" END

// F6: Remodel-Ready Low Performer
IF [Catering Sales YoY %] < 0 AND ATTR([Unit].[NextRemodelDate]) < TODAY()
THEN "Remodel Overdue" END

// F7: Availability Gap
IF [Total Catering Sales] < 5000
   AND (SUM([Availability].[PickupAvailable]) = 0
        OR SUM([Availability].[DispatchAvailable]) = 0)
THEN "Capacity Gap" END

// Alert Count — composite count of fired flags
(IIF(NOT ISNULL([F1: 1P Channel Abandonment]), 1, 0)
+ IIF(NOT ISNULL([F2: Platform Over-Dependency]), 1, 0)
+ IIF(NOT ISNULL([F3: Check Size Erosion]), 1, 0)
+ IIF(NOT ISNULL([F4: Catering + Ops Dual Risk]), 1, 0)
+ IIF(NOT ISNULL([F5: Discount-Propped Growth]), 1, 0)
+ IIF(NOT ISNULL([F6: Remodel-Ready Low Performer]), 1, 0)
+ IIF(NOT ISNULL([F7: Availability Gap]), 1, 0))

// Alert Level (used for row coloring)
IF [Alert Count] >= 3 THEN "RED"
ELSEIF [Alert Count] >= 1 THEN "AMBER"
ELSE "GREEN"
END
```

### 5.7 Apply default formats

For each calc: right-click → **Default Properties → Number Format**. Currency 0 dp for $ values, Percentage 1 dp for ratios, Automatic for flag strings.

---

## Phase 6 — Hierarchies, sets, parameters

### 6.1 Hierarchies

| Hierarchy | Levels (top → bottom) |
|---|---|
| `Brand Hierarchy` (on Brand) | `BrandCategory` → `Concept` → `BrandName` |
| `Geography` (on Unit) | `Country` → `Region` → `State` → `DMA` → `City` |
| `Org` (on Unit) | `RVP` → `DistrictManager` → `FranchiseBusinessConsultant` → `Franchisee` → `UnitNumber` |
| `Date` (on DimDate) | `Year` → `Quarter` → `Month` → `DayOfMonth` |
| `Fiscal` (on DimDate) | `FiscalYear` → `FiscalQuarter` → `Month` |

The **Org hierarchy** must include `FranchiseBusinessConsultant` — Dashboard 3 depends on it.

### 6.2 Useful sets

- **Top 10 Brands by Catering Sales** — right-click `BrandName` → Create → Set, Top tab, by `[Total Catering Sales]`.
- **Flagged Franchisees** — right-click `Franchisee` → Create → Set, Condition tab → "By formula": `[Alert Count] >= 1`.

### 6.3 Parameters

- `Year Selector` (Integer, range 2016–2026, current value matching the period in scope)
- `Top N Stores` (Integer, range 5–50, step 5, default 20)
- `3P Threshold %` (Float, range 0–1, step 0.05, default 0.75) — drives the Platform Dependency flag dynamically if you wire it into the calc

---

## Phase 7 — Worksheets and dashboards

### 7.1 Sheets to build

Build one worksheet per visual element. Numbering matches the dashboards.

**For Dashboard 1 — Catering Health Scorecard**

1. `KPI — Total Catering Sales` — Big text. `Total Catering Sales` on Text.
2. `KPI — 1P Share %` — Text card. Color by `Catering 1P Share %` (green ≥ 60%, red ≤ 40%).
3. `KPI — 3P Share %` — Text card. Color red ≥ 60%.
4. `KPI — Blended Avg Check`
5. `KPI — Catering Comp %` — Color red < 0%, green ≥ 0%.
6. `Mix — 1P vs 3P by Brand (100% Stacked Bar)` — Rows: `BrandName`. Columns: `Catering 1P Sales`, `Catering 3P Sales` (Measure Names on Color, Measure Values on Columns). Mark type: Bar. Quick table calc: Percent of Total → Compute Using → Table (across).
7. `Penetration — Catering as % of Total Sales by Brand` — Rows: `BrandName`. Columns: `Catering Penetration %`. Add reference line at the brand-average.
8. `Target Attainment — Bullet by Brand` — Show Me → Bullet Graph. Measure: `Total Catering Sales`. Reference: `Off-Premise Target`. Color by Target Attainment % (green ≥ 100%, amber 90–99%, red < 90%).
9. `Brand Ranking Table` — Rows: `BrandName`. Columns (Measure Names on Columns): `Total Catering Sales`, `Catering Sales YoY %`, `Catering Comp %`, `Catering 1P Share %`, `Catering Blended Avg Check`, `Catering Target Gap $`. Color-encode each column appropriately.

**For Dashboard 2 — Channel Intelligence**

10. `1P Share Trend` — Continuous date (week) on Columns, `Catering 1P Share %` on Rows. Add prior-year overlay via Quick Table Calc → Year over Year Growth.
11. `Avg Check — 1P vs 3P by Brand` — Rows: `BrandName`. Bars: `Catering 1P Avg Check` and `Catering 3P Avg Check` (Measure Names on Color).
12. **`3P Dependency Risk Matrix (Scatter)`** — the headline.
    - Columns: `Catering 3P Share %`
    - Rows: `Catering Sales YoY %`
    - Detail: `UnitNumber`
    - Size: `Total Catering Sales`
    - Color: `Region`
    - Add **Reference Line X = 0.75** and **Reference Line Y = 0**. Annotate quadrants.
13. `Digital ↔ Catering Overlap` — Continuous date on Columns. Dual axis: Bar = `Catering 1P Sales`, Line = `Digital 1P Sales`. Synchronize axes.

**For Dashboard 3 — FBC Action Board**

14. `Franchisee Alert Matrix` —
    - Rows: `Franchisee` (or `UnitNumber`).
    - Filter: `Flagged Franchisees` set = In.
    - Columns: `Total Catering Sales`, `Catering Sales YoY %`, `Catering 3P Share %`, `Catering Avg Check YoY %`, `Alert Count`.
    - Color: row background by `Alert Level` (RED/AMBER/GREEN via discrete color legend).
    - Sort by `Alert Count` descending.
    - Add the seven flag dimensions as additional columns showing their non-null values as colored tags.
15. `Franchisee Performance Quadrant` —
    - Columns: `Catering 1P YoY %`
    - Rows: `Catering Sales YoY %`
    - Detail: `Franchisee`
    - Size: `Total Catering Sales`
    - Reference lines X=0, Y=0. Quadrant labels: Stars (top-right) / Platform-only Growers (top-left) / Decliners (bottom-left) / 1P-Recovering (bottom-right).
16. `Guest Satisfaction Overlay` — Dual axis combo.
    - Rows: `Franchisee` (filtered to Flagged Franchisees set).
    - Columns: `Total Catering Sales` (bars) and `Speed Top %`, `Accuracy Top %` (line, synchronized).
17. `Dual Risk Table` — Rows: `UnitNumber`, `Franchisee`. Filter where `F4: Catering + Ops Dual Risk` is not null. Columns: `Total Catering Sales`, `Catering Sales YoY %`, `Field Audit Score Avg`, `Field Audit Failures`, `Food Safety Criticals`. All red-coded.

**For Dashboard 4 — Catering Trends (Rebuilt)**

18. `3-Line Trend: Total / 1P / 3P` — Continuous date (week) on Columns. Measures on Rows: `Total Catering Sales` (red), `Catering 1P Sales` (blue), `Catering 3P Sales` (grey dashed).
19. `Target Pace Overlay` — Same chart. Add a 4th measure for paced target. Create calc:
    ```
    // Catering Target Paced
    [Off-Premise Target] *
      (DATEDIFF('day', DATETRUNC('year', [DimDate].[CalendarDate]),
                [DimDate].[CalendarDate]) / 365.0)
    ```
20. `Discount Spike Annotation (Spend Proxy)` — Same date axis. Column = `Discounts (Spend Proxy)`. Marks visible periods of discount activity (proxy for promo events since Mktg Spend table absent).
21. `Seasonality Index` — Columns: `DimDate.Week` (1–52 as continuous integer). Rows: `Total Catering Sales`. Color by `DimDate.FiscalYear`. Multiple year lines + an averaged baseline.

**For Dashboard 5 — Marketing ROI View (with proxy note)**

22. `Incentive Spend vs Sales Lift by Brand` — Rows: `BrandName`. Bars: `Discounts (Spend Proxy)` and `Catering 1P Sales` (Measure Names on Color).
23. `Cost per Catering Order by Brand` — Rows: `BrandName`. Bar: `Marketing Cost per Catering Order (Proxy)`. Color red if > $5.
24. `Loyalty → Catering Scatter` —
    - Columns: `Loyalty Enrollments`
    - Rows: `Total Catering Sales`
    - Detail: `UnitNumber`
    - Add Trend Line (Analytics pane → Trend Line → Linear).
25. `Loyalty vs Catering — Magnitude` — Rows: `BrandName`. Bars (100% stacked): `Loyalty Sales` and `Total Catering Sales`.

### 7.2 Compose five dashboards (1200×800 fixed)

For each: **Dashboard → New Dashboard**, drag the relevant sheets, add the standard header strip.

Standard header strip (every dashboard):
- Page title + audience tag
- Year slicer (parameter `Year Selector` or filter on `DimDate.Year`)
- BrandCategory filter
- Region filter
- Apply to: **Worksheets → All Using This Data Source**

**Dashboard 1 — Catering Health Scorecard**
- Header strip
- Row of 5 KPI cards (sheets 1–5)
- Below: 2×2 grid — Mix Stacked Bar | Penetration | Target Bullet | Brand Ranking Table

**Dashboard 2 — Channel Intelligence**
- Header
- Top-left: 1P Share Trend · Top-right: Avg Check 1P vs 3P
- Bottom-left: **3P Dependency Risk Matrix (largest)**
- Bottom-right: Digital ↔ Catering Overlap

**Dashboard 3 — FBC Action Board**
- Header + **`Unit[FranchiseBusinessConsultant]` filter** (the FBC selects their own name)
- Big top section: Franchisee Alert Matrix
- Bottom-left: Franchisee Performance Quadrant
- Bottom-center: Guest Satisfaction Overlay
- Bottom-right: Dual Risk Table

**Dashboard 4 — Catering Trends (Rebuilt)**
- Header
- Large top chart: 3-Line Trend + Target Pace Overlay on the same axes
- Mid: Discount Spike Annotation
- Bottom: Seasonality Index

**Dashboard 5 — Marketing ROI View**
- **Add a Text object at the top**:
  > **Data substitution note:** This page uses `ReportedSales[DiscountsCY]` as a proxy for total incentive spend, since the synthetic UDI dataset does not contain the `Catering Marketing Spend` table (no `PPP`, `DeliveryFee`, `EZRewards` split). When the real Mktg Spend table is connected, replace the `Discounts (Spend Proxy)` measure with the corresponding spend measure.
- Header
- Top-left: Incentive Spend vs Sales Lift · Top-right: Cost per Catering Order
- Bottom-left: Loyalty → Catering Scatter · Bottom-right: Loyalty vs Catering Magnitude

### 7.3 Cross-dashboard navigation

For each dashboard:
1. Drag a **Navigation** object onto the header.
2. Configure five buttons: 1 — Scorecard, 2 — Channel, 3 — FBC, 4 — Trends, 5 — ROI.
3. Style consistently.

### 7.4 Drill actions (optional Store Detail)

If you build a 6th hidden dashboard with store-level KPIs:

1. Open Dashboard 1.
2. **Dashboard → Actions → Add Action → Go to Sheet…**
3. Source: any sheet that exposes `UnitNumber` (e.g., the scatter on Dashboard 2). Target: Store Detail dashboard. Run on: Menu.
4. Source Field = `UnitNumber`, Target Field = `UnitNumber`.

### 7.5 Filters applied across all sheets

For each filter on each dashboard:
1. Click the filter pill → dropdown → **Apply to Worksheets → All Using This Data Source**.

### 7.6 Visual consistency

- **Format → Workbook** → font: Tableau Bold for titles, Tableau Book for body.
- Set a custom color palette where `Concept` always uses the same colors across all dashboards.
- Use diverging palettes (red-grey-green) on every YoY % metric. Use sequential (single hue) on absolute magnitudes.

---

## Phase 8 — Performance & polish

1. **Help → Settings and Performance → Start Performance Recording.** Heavy visuals: Dashboard 3's Franchisee Alert Matrix (computes 7 flag calcs per row) and Dashboard 2's scatter. Anything > 1.5 s deserves attention.
2. **Replace divide-by-zero risk** with `ZN()` or `IIF([denom]=0, NULL, ...)`.
3. **Use the Set "Flagged Franchisees" as a filter on Dashboard 3** — never let the matrix render all 4,000 stores.
4. **Save as `.twbx`** (packaged) → `udi_data_gen/dashboards/Catering Analytics Transformation.twbx`.

---

## Phase 9 — Publish to Tableau Cloud / Server (optional)

1. **Server → Sign In** (Tableau Cloud URL).
2. **Server → Publish Workbook** → check **Include external files** to embed Hyper extracts.
3. After publish:
   - Set **Subscriptions** per audience (e.g., weekly Monday for FBCs on Dashboard 3).
   - **Data-driven alerts** on Alert Count: open Dashboard 3 → click the Alert Count axis → **Create Alert** → threshold "> 5".

---

## Path B — DuckDB JDBC (live mode evaluation)

Use this only if specifically evaluating Tableau Live (e.g., for case #183 in the discovery matrix).

### B.1 Install DuckDB JDBC

1. Download the DuckDB JDBC jar from <https://duckdb.org/docs/installation/?version=stable&environment=java>.
2. Put `duckdb_jdbc-x.y.z.jar` into `C:\Program Files\Tableau\Drivers\`.
3. Restart Tableau Desktop.

### B.2 Create a DuckDB file with views over the Parquet

```powershell
python -c "
import duckdb, pathlib
con = duckdb.connect('udi_data_gen/output/udi.duckdb')
for p in pathlib.Path('udi_data_gen/output/parquet').glob('*.parquet'):
    con.execute(f\"CREATE OR REPLACE VIEW {p.stem} AS SELECT * FROM read_parquet('{p.as_posix()}')\")
print('Views created')
"
```

### B.3 Connect Tableau

1. **Connect → To a Server → More… → Other Databases (JDBC)**.
2. URL: `jdbc:duckdb:c:/Users/sridhar.vetrivel/OneDrive - psiog.com/Accounts/GTF/TableAU Analysis/udi_data_gen/output/udi.duckdb`
3. Dialect: PostgreSQL.
4. Repeat Phases 3–7. **Connection type = Live**.

---

## Validation checklist

- [ ] 15 hyper files generated and verified.
- [ ] All 15 tables added as connections, renamed to CamelCase.
- [ ] Star schema in logical layer; `Catering` is the focal fact.
- [ ] Cardinality (Many-to-One) + Referential Integrity (All Records Match) set on every relationship.
- [ ] `Unit.FranchiseBusinessConsultant` visible.
- [ ] All 12 core catering KPIs (Section 5.1) created.
- [ ] YoY calcs (Section 5.2) created using LOD or Lookup pattern.
- [ ] All 7 store-health flags + Alert Count + Alert Level (Section 5.6).
- [ ] 5 hierarchies built; Org hierarchy includes FranchiseBusinessConsultant.
- [ ] 25 worksheets built.
- [ ] 5 dashboards composed: Scorecard, Channel, FBC, Trends, ROI.
- [ ] Dashboard 5 has the data-substitution note text object.
- [ ] Cross-dashboard navigation buttons on every dashboard.
- [ ] Performance recording shows < 1.5 s on each dashboard.
- [ ] Saved as `.twbx`.
- [ ] Published to Cloud/Server (if available).

---

## Common gotchas

| Symptom | Fix |
|---|---|
| `pantab` errors on install | `pip install --upgrade pip` then retry. Python 3.10+ required. |
| Hyper conversion runs out of memory on a big fact | Chunk the `pd.read_parquet`, or regen at `UDI_SCALE=0.25`. |
| Tableau shows row counts that don't match the dataset | You're in the *physical layer*. Click back to the logical layer in the Data Source pane. |
| Filter only affects one viz | Apply to Worksheets → "All Using This Data Source". |
| YoY % calculations show NULL | Likely a single-year filter — YoY needs at least two years in scope. Widen the filter. |
| Flag calcs show NULL on Dashboard 1 (Brand level) | Flags use Unit-grained context (`ATTR(Unit.NextRemodelDate)`). They only fire on Dashboards 3 (Franchisee/Unit-level). Don't try to surface them on the Scorecard. |
| Different totals between PBI and Tableau | Check relationship cardinality. Tableau defaults to Many-to-Many; force Many-to-One on the fact side. |
| Map shows nothing | Country / State / City must have geographic roles set. |
| Drill-through opens but shows all stores | Action's Target Filters must pass `UnitNumber` (Source Field = `UnitNumber`, Target Field = `UnitNumber`). |
| 3P Risk Matrix is empty | YoY % calc requires multi-year scope and a per-unit aggregation. Check that the scatter's Detail shelf is `UnitNumber` and Year Selector parameter has data on both sides. |
| Alert matrix has 4,000 rows | Apply the `Flagged Franchisees` set as a filter — Dashboard 3 is meant to show only flagged stores. |
| Hyper file fails to open | The file is open in another Tableau session. Close other workbooks. |

---

## Side-by-side parity with PBI

The Tableau build should produce the same numbers as the Power BI build (data is deterministic). Common divergence causes:

1. **Relationship cardinality differs** — Tableau M-to-M default vs PBI 1-to-many.
2. **Filter scope differs** — Tableau worksheet-only vs PBI page-level.
3. **Measure aggregation differs** — `AVG` vs `SUM` vs `COUNTD`.
4. **PBI's Auto Date/Time still on** — creates extra date tables.
5. **YoY computed against different baselines** — Tableau LOD-based pattern vs PBI `SAMEPERIODLASTYEAR`.

Match the dashboards 1:1 by page and check the headline KPI on each. Differences > 0.1% are bugs to chase.
