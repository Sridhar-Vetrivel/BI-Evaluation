# Power BI Build Guide — GoTo Foods Catering Analytics Transformation

End-to-end instructions to point Power BI Desktop at the generated Parquet files and build the **5-page Catering Analytics Transformation** described in `catering_analytics_transformation.md`. The goal isn't a generic UDI dashboard — it's a decision-ready Catering report that replaces the current 6-page "data dump" with audience-driven insight pages.

Source dataset:

```
c:\Users\sridhar.vetrivel\OneDrive - psiog.com\Accounts\GTF\TableAU Analysis\udi_data_gen\output\parquet\
```

15 files · ~1 GB on disk · ~118M rows total. In Power BI Import mode VertiPaq will compress this to a smaller in-memory footprint — but expect the initial load to take 3–8 minutes.

> If the load is too heavy for your laptop, regenerate at 25% scale first:
> ```powershell
> $env:UDI_SCALE = "0.25"
> python -m udi_data_gen.orchestrator
> ```
> That yields ~3M rows per fact (~250 MB total) — same shape, much lighter.

## The 5 pages we're building

| Page | Audience | Decision it enables |
|---|---|---|
| **1. Catering Health Scorecard** | Brand Leaders, RVPs | Is catering healthy across the system this period? |
| **2. Channel Intelligence** | Brand Managers, FBCs | Is the 1P/3P mix protecting margin or eroding it? |
| **3. FBC Action Board** | Franchise Business Consultants | Which franchisees need my attention today, and why? |
| **4. Catering Trends (Rebuilt)** | Brand Managers, FBCs | Is the trend real, seasonal, or discount-propped? |
| **5. Marketing ROI View** | Brand Marketing Teams | Are catering incentives generating return or just discounting? |

> **Data-availability note for Page 5.** The original transformation doc references a `Catering Marketing Spend` table with `PPP`, `DeliveryFee`, `EZRewards`, `Subtotal` fields. **The synthetic UDI dataset does not include those fields.** Page 5 in this guide uses `ReportedSales[DiscountsCY]` as an aggregate spend proxy. When the real Catering Marketing Spend table is connected, the page structure stays — only the field source changes.

---

## Prerequisites

1. **Power BI Desktop** — latest stable build (May 2024 or later — earlier versions have a buggy Parquet connector). [Download here](https://powerbi.microsoft.com/desktop/).
2. **DAX Studio** (optional but recommended) — for measure debugging and model size inspection.
3. **Tabular Editor 2** (free, optional) — for bulk measure authoring (the catering build has ~40 measures; Tabular Editor is faster than New Measure × 40).
4. Folder permissions on the parquet path.

---

## Phase 1 — Connect to Parquet files (load 15 tables)

### Option A: Quick — one parquet file at a time (good for first run)

For each of the 15 files:

1. **Home → Get Data → More… → File → Parquet → Connect**
2. Browse to `udi_data_gen\output\parquet\reported_sales.parquet`
3. In the preview dialog, click **Transform Data** (so you can rename + set types) — *not* Load.
4. In Power Query Editor: right-click the query → **Rename** → `ReportedSales` (no spaces — Power BI loves CamelCase).
5. Repeat for every parquet file.

### Option B: Faster — one parameterized Power Query (recommended)

In Power Query Editor (**Home → Transform Data**), create one **parameter** for the base path, then 15 queries that share it. This makes the model portable.

1. **Home → Manage Parameters → New Parameter**
   - Name: `ParquetFolder`
   - Type: Text
   - Suggested Values: Any value
   - Current Value: `C:\Users\sridhar.vetrivel\OneDrive - psiog.com\Accounts\GTF\TableAU Analysis\udi_data_gen\output\parquet`

2. **Home → New Source → Blank Query**, then **Advanced Editor** and paste — one query per table:

```m
// === DimDate ===
let
    Source = Parquet.Document(File.Contents(ParquetFolder & "\dimdate.parquet")),
    Typed  = Table.TransformColumnTypes(Source, {
        {"CalendarDate", type date},
        {"DateKey", Int64.Type}, {"Year", Int64.Type}, {"Quarter", Int64.Type},
        {"Month", Int64.Type}, {"MonthName", type text},
        {"Week", Int64.Type}, {"DayOfMonth", Int64.Type},
        {"DayOfWeek", Int64.Type}, {"DayName", type text},
        {"IsWeekend", Int64.Type}, {"IsHoliday", Int64.Type},
        {"FiscalYear", Int64.Type}, {"FiscalQuarter", Int64.Type}
    })
in
    Typed
```

```m
// === Brand ===
let
    Source = Parquet.Document(File.Contents(ParquetFolder & "\brand.parquet")),
    Typed  = Table.TransformColumnTypes(Source, {
        {"BrandSequence", Int64.Type}, {"BrandName", type text},
        {"BrandType", type text}, {"InternationalFlag", type text},
        {"BrandSort", Int64.Type}, {"Concept", type text},
        {"BrandCategory", type text}, {"BrandFoodSafetySource", type text},
        {"BrandScorecardRankingTimeframe", type text}
    })
in
    Typed
```

```m
// === Unit ===
let
    Source = Parquet.Document(File.Contents(ParquetFolder & "\unit.parquet")),
    Typed  = Table.TransformColumnTypes(Source, {
        {"SBRSequence", Int64.Type}, {"UnitNumber", type text},
        {"OpenDate", type date}, {"CloseDate", type date},
        {"LeaseExpirationDate", type date}, {"NextRemodelDate", type date},
        {"Latitude", type number}, {"Longitude", type number}
    })
in
    Typed
```

```m
// === Catering ===  (the central fact for this report)
let
    Source = Parquet.Document(File.Contents(ParquetFolder & "\catering.parquet")),
    Typed  = Table.TransformColumnTypes(Source, {
        {"BrandSequence", Int64.Type}, {"SBRSequence", Int64.Type},
        {"CalendarDate", type date},
        {"FirstPartyNetSales", type number}, {"ThirdPartyNetSales", type number},
        {"FirstPartyTraffic", Int64.Type}, {"ThirdPartyTraffic", Int64.Type},
        {"Comp", type text}
    })
in
    Typed
```

```m
// === ReportedSales ===  (penetration & discount-as-spend proxy)
let
    Source = Parquet.Document(File.Contents(ParquetFolder & "\reported_sales.parquet")),
    Typed  = Table.TransformColumnTypes(Source, {
        {"BrandSequence", Int64.Type}, {"SBRSequence", Int64.Type},
        {"CalendarDate", type date},
        {"NetSalesCY", type number}, {"NetSalesPY", type number},
        {"TrafficCY", type number}, {"TrafficPY", type number},
        {"DiscountsCY", type number}, {"DiscountsPY", type number},
        {"CateringCY", type number}, {"CateringPY", type number},
        {"CateringCheckCountCY", type number}, {"CateringCheckCountPY", type number},
        {"Comp", type text}, {"TrafficComp", type text}
    })
in
    Typed
```

For the remaining tables the column types are similar — measures are `type number`, integers are `Int64.Type`, dates are `type date`, anything else is `type text`. Final query names:

| File | Query name |
|---|---|
| `dimdate.parquet` | `DimDate` |
| `brand.parquet` | `Brand` |
| `unit.parquet` | `Unit` |
| `unit_ranking_base.parquet` | `UnitRankingBase` |
| `brand_targets.parquet` | `BrandTargets` |
| `availability.parquet` | `Availability` |
| `catering.parquet` | `Catering` |
| `digital_sales.parquet` | `DigitalSales` |
| `field_audits.parquet` | `FieldAudits` |
| `food_safety.parquet` | `FoodSafety` |
| `gift_cards.parquet` | `GiftCards` |
| `guest_satisfaction.parquet` | `GuestSatisfaction` |
| `loyalty.parquet` | `Loyalty` |
| `remodels.parquet` | `Remodels` |
| `reported_sales.parquet` | `ReportedSales` |

3. **Home → Close & Apply.** First load takes a few minutes — VertiPaq compresses as it ingests.

> Sanity check after load: bottom-right status bar should show ~118M rows pulled. If only 100K rows appeared, you accidentally hit "Combine Binaries" — undo and re-import individually.

---

## Phase 2 — Model configuration

Switch to **Model view** (left sidebar, third icon).

### 2.1 Mark DimDate as the Date table

1. Click `DimDate` in the model canvas.
2. Right-click → **Mark as date table** → choose `CalendarDate` → OK.
3. **File → Options → Current File → Data Load → Time intelligence:** **uncheck "Auto date/time"**. Critical — otherwise PBI creates a hidden date table per fact, blowing up model size by 30–50%.

### 2.2 Hide key columns from Report view

In every fact table, key columns shouldn't appear in slicers. In the Data pane (right side, Report view):

- Right-click each of these → **Hide in report view**:
  - All fact tables: `BrandSequence`, `SBRSequence`, `CalendarDate` (still used for relationships, but hidden)
  - `GiftCards`: also `CardBrandSequence`, `StoreBrandSequence`, `MergedBrandSequence`
  - `DimDate`: `DateKey`
  - `Brand`: `BrandSequence`, `BrandSort`
  - `Unit`: `SBRSequence`, `Latitude`/`Longitude` (leave visible if you want a map)

### 2.3 Critical fields to leave visible on Unit

The FBC Action Board (Page 3) filters and slices on:
- `Unit[FranchiseBusinessConsultant]` — the page's primary filter
- `Unit[Franchisee]`, `Unit[FranchiseeGroup]`, `Unit[FranchisePartner]` — the page's row identity
- `Unit[VenueTradNonTradByFreq]` — for venue-type segmentation
- `Unit[NextRemodelDate]` — for the Remodel-Ready Low Performer flag

Make sure these are NOT hidden.

### 2.4 Mark Lat/Long for mapping

- `Unit[Latitude]` → Properties pane → **Data category = Latitude**
- `Unit[Longitude]` → Properties pane → **Data category = Longitude**
- `Unit[City]` → Data category = City; `Unit[State]` → State or Province; `Unit[Country]` → Country/Region; `Unit[ZipCode]` → Postal Code.

### 2.5 Sort orders that matter

- `DimDate[MonthName]` → Column tools → **Sort by column = Month**
- `DimDate[DayName]` → Sort by column = `DayOfWeek`

---

## Phase 3 — Build relationships

Power BI usually auto-detects most of these. Verify them in **Model view** and add the missing ones.

### Active relationships

| From (many) | → To (one) | Active | Cross-filter |
|---|---|---|---|
| `Catering[BrandSequence]` | `Brand[BrandSequence]` | ✅ | Single |
| `Catering[SBRSequence]` | `Unit[SBRSequence]` | ✅ | Single |
| `Catering[CalendarDate]` | `DimDate[CalendarDate]` | ✅ | Single |
| Repeat the Brand / Unit / DimDate triplet for **every** other fact: ReportedSales, Availability, DigitalSales, FieldAudits, FoodSafety, GuestSatisfaction, Loyalty, Remodels, UnitRankingBase | | | |
| `BrandTargets[BrandSequence]` | `Brand[BrandSequence]` | ✅ | Single |
| `BrandTargets[CalendarDate]` | `DimDate[CalendarDate]` | ✅ | Single |
| `GiftCards[StoreBrandSequence]` | `Brand[BrandSequence]` | ✅ | Single |
| `GiftCards[SBRSequence]` | `Unit[SBRSequence]` | ✅ | Single |
| `GiftCards[CalendarDate]` | `DimDate[CalendarDate]` | ✅ | Single |

### Inactive relationships (GiftCards role-playing)

| From | To | Why |
|---|---|---|
| `GiftCards[CardBrandSequence]` | `Brand[BrandSequence]` | Reporting "by card brand" |
| `GiftCards[MergedBrandSequence]` | `Brand[BrandSequence]` | Reporting "by merged brand" |

### Visual check

Layout should look like a star: `Brand`, `Unit`, `DimDate` at the centre, all fact tables radiating outward. **`Catering` is the focal fact** — most measures hit it. No bidirectional relationships unless absolutely needed.

---

## Phase 4 — DAX measures (catering-focused)

Create a dedicated measure table: **Home → Enter Data → name it `_Measures` → Load.** Right-click the dummy column → Hide.

### 4.1 Core catering KPIs (Catering table)

```dax
Total Catering Sales =
    SUM ( Catering[FirstPartyNetSales] ) + SUM ( Catering[ThirdPartyNetSales] )

Catering 1P Sales =
    SUM ( Catering[FirstPartyNetSales] )

Catering 3P Sales =
    SUM ( Catering[ThirdPartyNetSales] )

Catering 1P Share % =
    DIVIDE ( [Catering 1P Sales], [Total Catering Sales] )

Catering 3P Share % =
    DIVIDE ( [Catering 3P Sales], [Total Catering Sales] )

Catering 1P Traffic =
    SUM ( Catering[FirstPartyTraffic] )

Catering 3P Traffic =
    SUM ( Catering[ThirdPartyTraffic] )

Catering Total Traffic =
    [Catering 1P Traffic] + [Catering 3P Traffic]

Catering 1P Traffic Share % =
    DIVIDE ( [Catering 1P Traffic], [Catering Total Traffic] )

Catering 1P Avg Check =
    DIVIDE ( [Catering 1P Sales], [Catering 1P Traffic] )

Catering 3P Avg Check =
    DIVIDE ( [Catering 3P Sales], [Catering 3P Traffic] )

Catering Blended Avg Check =
    DIVIDE ( [Total Catering Sales], [Catering Total Traffic] )
```

### 4.2 Year-over-year catering measures (time intelligence)

Catering's PY values come from time-shifted CY measures (we don't store PY columns in the Catering fact). Requires DimDate as the date table.

```dax
Total Catering Sales PY =
    CALCULATE (
        [Total Catering Sales],
        SAMEPERIODLASTYEAR ( DimDate[CalendarDate] )
    )

Catering Sales YoY % =
    DIVIDE (
        [Total Catering Sales] - [Total Catering Sales PY],
        [Total Catering Sales PY]
    )

Catering 1P Sales PY =
    CALCULATE ( [Catering 1P Sales], SAMEPERIODLASTYEAR ( DimDate[CalendarDate] ) )

Catering 1P YoY % =
    DIVIDE ( [Catering 1P Sales] - [Catering 1P Sales PY], [Catering 1P Sales PY] )

Catering 3P Sales PY =
    CALCULATE ( [Catering 3P Sales], SAMEPERIODLASTYEAR ( DimDate[CalendarDate] ) )

Catering 3P YoY % =
    DIVIDE ( [Catering 3P Sales] - [Catering 3P Sales PY], [Catering 3P Sales PY] )

Catering Traffic YoY % =
    VAR _cy = [Catering Total Traffic]
    VAR _py = CALCULATE ( [Catering Total Traffic], SAMEPERIODLASTYEAR ( DimDate[CalendarDate] ) )
    RETURN DIVIDE ( _cy - _py, _py )

Catering Avg Check YoY % =
    VAR _cy = [Catering Blended Avg Check]
    VAR _py = CALCULATE ( [Catering Blended Avg Check], SAMEPERIODLASTYEAR ( DimDate[CalendarDate] ) )
    RETURN DIVIDE ( _cy - _py, _py )
```

### 4.3 Comp store catering

```dax
Comp Catering Sales =
    CALCULATE ( [Total Catering Sales], Catering[Comp] = "Comp" )

Comp Catering Sales PY =
    CALCULATE (
        [Total Catering Sales],
        SAMEPERIODLASTYEAR ( DimDate[CalendarDate] ),
        Catering[Comp] = "Comp"
    )

Catering Comp % =
    DIVIDE (
        [Comp Catering Sales] - [Comp Catering Sales PY],
        [Comp Catering Sales PY]
    )
```

### 4.4 Cross-table KPIs (the high-value ones)

```dax
-- Catering as % of total reported sales (penetration)
Catering Penetration % =
    DIVIDE ( [Total Catering Sales], SUM ( ReportedSales[NetSalesCY] ) )

-- Catering vs OffPremiseTarget (the accountability metric)
Catering Off-Premise Target =
    SUM ( BrandTargets[OffPremiseTarget] )

Catering Target Attainment % =
    DIVIDE ( [Total Catering Sales], [Catering Off-Premise Target] )

Catering Target Gap $ =
    [Total Catering Sales] - [Catering Off-Premise Target]

-- Discounts as a spend proxy (in lieu of true Mktg Spend table)
Discounts (Spend Proxy) =
    SUM ( ReportedSales[DiscountsCY] )

Discount Rate on Catering =
    DIVIDE ( [Discounts (Spend Proxy)], SUM ( ReportedSales[CateringCY] ) )

Marketing Cost per Catering Order (Proxy) =
    DIVIDE ( [Discounts (Spend Proxy)], [Catering 1P Traffic] )

-- Loyalty correlation
Loyalty Enrollments =
    SUM ( Loyalty[Enrollments] )

Loyalty Sales =
    SUM ( Loyalty[LoyaltySales] )

Loyalty → Catering Conversion =
    DIVIDE ( [Total Catering Sales], SUM ( Loyalty[LoyaltyEarnableSales] ) )

-- Digital ↔ Catering channel overlap
Digital 1P Sales =
    SUM ( DigitalSales[FirstPartyNetSales] )

Catering 1P as % of Digital 1P =
    DIVIDE ( [Catering 1P Sales], [Digital 1P Sales] )
```

### 4.5 Operational quality (for FBC Action Board overlays)

```dax
Guest Top Score Rate =
    DIVIDE ( SUM ( GuestSatisfaction[TopScores] ), SUM ( GuestSatisfaction[Surveys] ) )

Speed Top % =
    DIVIDE ( SUM ( GuestSatisfaction[SpeedTopScores] ),
             SUM ( GuestSatisfaction[SpeedResponses] ) )

Accuracy Top % =
    DIVIDE ( SUM ( GuestSatisfaction[AccuracyTopScores] ),
             SUM ( GuestSatisfaction[AccuracyResponses] ) )

Field Audit Score Avg =
    AVERAGE ( FieldAudits[FieldAuditScore] )

Field Audit Failures =
    SUM ( FieldAudits[FieldAuditFailures] )

Food Safety Criticals =
    SUM ( FoodSafety[FoodSafetyCriticals] )

-- Channel availability
Pickup Days Available =
    SUM ( Availability[PickupAvailable] )

Dispatch Days Available =
    SUM ( Availability[DispatchAvailable] )

Combined Channels Available =
    SUM ( Availability[CombinedAvailable] )

Active Stores =
    DISTINCTCOUNT ( Catering[SBRSequence] )
```

### 4.6 Store-health flags (the heart of the FBC Action Board)

These return human-readable strings used for conditional formatting and tile color in Page 3. Each flag implements one of the 7 conditions from the transformation doc.

```dax
-- F1: 1P Channel Abandonment — 1P down >25% YoY AND 3P up or flat
Flag 1P Channel Abandonment =
    IF (
        [Catering 1P YoY %] < -0.25
            && [Catering 3P YoY %] >= 0,
        "1P Abandonment Risk",
        BLANK ()
    )

-- F2: Platform Over-Dependency — 3P share >75%
Flag Platform Dependency =
    IF (
        [Catering 3P Share %] > 0.75,
        "Platform Over-Dependent",
        BLANK ()
    )

-- F3: Check Size Erosion — avg check down >15% YoY
Flag Check Size Erosion =
    IF (
        [Catering Avg Check YoY %] < -0.15,
        "Check Size Eroding",
        BLANK ()
    )

-- F4: Catering + Ops Dual Risk — catering comp <-10% AND audit score <75
Flag Catering Ops Dual Risk =
    IF (
        [Catering Comp %] < -0.10
            && [Field Audit Score Avg] < 75,
        "ESCALATE - Dual Risk",
        BLANK ()
    )

-- F5: Discount-Propped Growth — catering up but discounts growing faster
Flag Discount Propped Growth =
    VAR _disc_yoy =
        DIVIDE (
            SUM ( ReportedSales[DiscountsCY] ) - SUM ( ReportedSales[DiscountsPY] ),
            SUM ( ReportedSales[DiscountsPY] )
        )
    VAR _cater_yoy =
        DIVIDE (
            SUM ( ReportedSales[CateringCY] ) - SUM ( ReportedSales[CateringPY] ),
            SUM ( ReportedSales[CateringPY] )
        )
    RETURN
        IF ( _cater_yoy > 0 && _disc_yoy > _cater_yoy, "Hollow Growth", BLANK () )

-- F6: Remodel-Ready Low Performer — catering declining AND remodel overdue
Flag Remodel Overdue Risk =
    IF (
        [Catering Sales YoY %] < 0
            && MAX ( Unit[NextRemodelDate] ) < TODAY (),
        "Remodel Overdue",
        BLANK ()
    )

-- F7: Availability Gap — catering low AND pickup or dispatch disabled
Flag Availability Gap =
    IF (
        [Total Catering Sales] < 5000
            && (
                SUM ( Availability[PickupAvailable] ) = 0
                || SUM ( Availability[DispatchAvailable] ) = 0
            ),
        "Capacity Gap",
        BLANK ()
    )

-- Composite alert level: counts how many flags fired for this row
Alert Count =
    VAR _f1 = IF ( NOT ISBLANK ( [Flag 1P Channel Abandonment] ), 1, 0 )
    VAR _f2 = IF ( NOT ISBLANK ( [Flag Platform Dependency] ), 1, 0 )
    VAR _f3 = IF ( NOT ISBLANK ( [Flag Check Size Erosion] ), 1, 0 )
    VAR _f4 = IF ( NOT ISBLANK ( [Flag Catering Ops Dual Risk] ), 1, 0 )
    VAR _f5 = IF ( NOT ISBLANK ( [Flag Discount Propped Growth] ), 1, 0 )
    VAR _f6 = IF ( NOT ISBLANK ( [Flag Remodel Overdue Risk] ), 1, 0 )
    VAR _f7 = IF ( NOT ISBLANK ( [Flag Availability Gap] ), 1, 0 )
    RETURN _f1 + _f2 + _f3 + _f4 + _f5 + _f6 + _f7

Alert Level =
    SWITCH (
        TRUE (),
        [Alert Count] >= 3, "RED",
        [Alert Count] >= 1, "AMBER",
        "GREEN"
    )
```

### 4.7 Formatting

For each currency measure: Measure tools → **Format → Currency → $ English (US) → 0 decimals**.
For percentages (all `*%` measures): **Percentage → 1 decimal**.
For flag-name measures: Text (default).

---

## Phase 5 — Hierarchies

In Report view, right-click a column → **Create hierarchy**:

| Hierarchy | Levels |
|---|---|
| `Brand[Brand Hierarchy]` | `BrandCategory` → `Concept` → `BrandName` |
| `Unit[Geography]` | `Country` → `Region` → `State` → `DMA` → `City` |
| `Unit[Org]` | `RVP` → `DistrictManager` → `FranchiseBusinessConsultant` → `Franchisee` → `UnitNumber` |
| `DimDate[Date Hierarchy]` | `Year` → `Quarter` → `Month` → `DayOfMonth` |
| `DimDate[Fiscal]` | `FiscalYear` → `FiscalQuarter` → `Month` |

The **Org hierarchy** is critical for Page 3 (FBC Action Board) — it must include `FranchiseBusinessConsultant`.

---

## Phase 6 — Build the 5 catering dashboard pages

Every page should have a consistent header strip with: page title, audience tag, and three slicers: `DimDate[Year]`, `DimDate[Quarter]` (relative date filter "This Year So Far" set on Quarter slicer is recommended), `Brand[BrandHierarchy].BrandCategory`. Pages 3 and 4 add a `Unit[FranchiseBusinessConsultant]` slicer.

### Page 1 — Catering Health Scorecard

*Audience: Brand Leaders, RVPs · Replaces current Catering Summary & Summary 2.0*

**KPI strip (top row — 5 Cards):**

| Card | Measure | Notes |
|---|---|---|
| Total Catering Sales | `[Total Catering Sales]` | Format $0M with `dynamic format string`: `"$"#,0,,"M"` |
| 1P Share % | `[Catering 1P Share %]` | Color green if ≥ 60%, red if ≤ 40% |
| 3P Share % | `[Catering 3P Share %]` | Color red if ≥ 60% |
| Blended Avg Check | `[Catering Blended Avg Check]` | $0 |
| Catering Comp % | `[Catering Comp %]` | Color red < 0%, green ≥ 0% |

Use the **KPI visual** (not just Card) where you want trend sparkline + target — set Trend axis = `DimDate[Year]`, Target = `[Catering Off-Premise Target]`.

**Body visuals:**

1. **1P vs 3P Revenue Mix — 100% Stacked Bar by Brand.** Visual: 100% stacked bar. Axis = `Brand[BrandName]`. Values = `[Catering 1P Sales]`, `[Catering 3P Sales]`. Sort by `[Total Catering Sales]` descending. Tooltip: include both $ values and shares.
2. **Catering Penetration % by Brand.** Visual: Clustered bar. Axis = `Brand[BrandName]`. Values = `[Catering Penetration %]`. Reference line at the system average (use a measure: `Catering Penetration % All Brands = CALCULATE([Catering Penetration %], REMOVEFILTERS(Brand))`).
3. **Target Attainment — Bullet Chart by Brand.** Visual: Use the **"Bullet Chart"** custom visual (Marketplace) OR Clustered bar with reference line. Actual = `[Total Catering Sales]`. Target = `[Catering Off-Premise Target]`. Conditional formatting on the bar: red < 90%, amber 90–99%, green ≥ 100%.
4. **Brand Ranking Table.** Visual: Table. Columns: `Brand[BrandName]`, `[Total Catering Sales]`, `[Catering Sales YoY %]`, `[Catering Comp %]`, `[Catering 1P Share %]`, `[Catering Blended Avg Check]`, `[Catering Target Gap $]`. Conditional formatting (data bars) on Total Catering Sales; Color scale on YoY % (red→green); Color scale on Target Gap $ (red on negative).

### Page 2 — Channel Intelligence

*Audience: Brand Managers, FBCs · The 1P vs 3P story*

1. **1P Share Trend — Line Chart over Time.** Visual: Line. Axis = `DimDate[Date Hierarchy]` (defaulted to Month). Values = `[Catering 1P Share %]`. Add a second line = `[Catering 1P Share %]` for prior year using `CALCULATE([Catering 1P Share %], SAMEPERIODLASTYEAR(DimDate[CalendarDate]))` — define as a measure `Catering 1P Share PY`. Format Y axis as %.
2. **Avg Check Comparison — 1P vs 3P by Brand.** Visual: Clustered column. Axis = `Brand[BrandName]`. Values = `[Catering 1P Avg Check]` and `[Catering 3P Avg Check]`. Sort by 1P descending.
3. **3P Dependency Risk Matrix — Scatter (the headline viz).** Visual: Scatter chart.
   - X axis = `[Catering 3P Share %]`
   - Y axis = `[Catering Sales YoY %]`
   - Details = `Unit[UnitNumber]` (each dot = one store)
   - Size = `[Total Catering Sales]`
   - Legend = `Unit[Region]`
   - Add **constant X line at 0.7** (75% 3P share threshold) and **constant Y line at 0**. The 4 quadrants are: top-left = Healthy 1P-led, top-right = Platform-Dependent but Growing, bottom-left = Declining (1P-led), bottom-right = At Risk (3P-only + declining).
   - Title: "Top-right = grew via 3P. Bottom-right = at risk if platform raises fees."
4. **Digital ↔ Catering Overlap.** Visual: Combo chart. Axis = `DimDate[Year]` + `DimDate[Quarter]`. Line = `[Digital 1P Sales]`. Column = `[Catering 1P Sales]`. Secondary measure tooltip = `[Catering 1P as % of Digital 1P]`.

### Page 3 — FBC Action Board

*Audience: Franchise Business Consultants · Replaces the 30-row Catering Detail table.*

Add a **`Unit[FranchiseBusinessConsultant]` slicer** at top — the FBC selects their own name and the page becomes their portfolio view.

1. **Franchisee Alert Cards — Auto-flagged.** Visual: Matrix.
   - Rows = `Unit[Franchisee]` (or `Unit[UnitNumber]` for store-level).
   - Filter = `[Alert Count] >= 1`.
   - Values = `[Total Catering Sales]`, `[Catering Sales YoY %]`, `[Catering 3P Share %]`, `[Catering Avg Check YoY %]`, `[Alert Count]`, `[Alert Level]`.
   - Conditional formatting on the row: background color tied to `[Alert Level]` — red = RED, orange = AMBER, no fill = GREEN.
   - Also use **conditional formatting → Background color → Field value** to show each individual flag's text in a column (`[Flag 1P Channel Abandonment]`, `[Flag Platform Dependency]`, …) as colored chips.
   - Sort by `[Alert Count]` descending so worst offenders surface first.
2. **Franchisee Performance Quadrant.** Visual: Scatter.
   - X = `[Catering 1P YoY %]`
   - Y = `[Catering Sales YoY %]`
   - Details = `Unit[Franchisee]`
   - Size = `[Total Catering Sales]`
   - Constant lines at X=0 and Y=0. Quadrant labels (use Text boxes overlay): top-right = Stars · top-left = Platform-only Growers · bottom-left = Decliners · bottom-right = 1P-Recovering.
3. **Guest Satisfaction Overlay.** Visual: Clustered column + line combo.
   - Axis = `Unit[Franchisee]` (filtered by Alert Count ≥ 1).
   - Column = `[Total Catering Sales]` and `[Catering Sales YoY %]`.
   - Line on secondary axis = `[Speed Top %]` and `[Accuracy Top %]`.
   - Insight surfaced: stores with declining catering AND poor speed/accuracy = service-driven decline.
4. **Field Audit + Food Safety Dual-Risk Table.** Visual: Table. Filter rows where `[Flag Catering Ops Dual Risk]` is NOT BLANK.
   - Columns: `Unit[UnitNumber]`, `Unit[Franchisee]`, `[Total Catering Sales]`, `[Catering Sales YoY %]`, `[Field Audit Score Avg]`, `[Field Audit Failures]`, `[Food Safety Criticals]`. All red-flagged with conditional formatting.

### Page 4 — Catering Trends (Rebuilt)

*Audience: Brand Managers, FBCs · The trend chart that actually answers questions*

1. **3-Line Trend Chart: Total / 1P / 3P.** Visual: Line.
   - Axis = `DimDate[CalendarDate]` (continuous; aggregated to week via `DateHierarchy` set to Week).
   - Values = `[Total Catering Sales]` (solid red), `[Catering 1P Sales]` (solid blue), `[Catering 3P Sales]` (dashed grey).
   - Add second-axis CY-vs-PY toggle using a bookmark.
2. **Target Pace Line Overlay.** Same chart as above, add a 4th line: a cumulative-by-week of `[Catering Off-Premise Target]` evenly paced across the year.
   ```dax
   Catering Target Paced =
       VAR _yearTarget = CALCULATE ( [Catering Off-Premise Target], ALL ( DimDate[CalendarDate] ), VALUES ( DimDate[Year] ) )
       VAR _daysIntoYear = MAX ( DimDate[CalendarDate] ) - DATE ( YEAR ( MAX ( DimDate[CalendarDate] ) ), 1, 1 )
       RETURN _yearTarget * DIVIDE ( _daysIntoYear, 365 )
   ```
3. **Promo / Event Annotation Layer.** *Adapted — no Mktg Spend table.* Use `ReportedSales[DiscountsCY]` instead. Visual: Combo chart on the same time axis with a Column for `[Discounts (Spend Proxy)]` and the trend line on top. Periods where the discount bar spikes mark probable promo activity.
4. **Seasonality Index Panel.** Visual: Line chart with `DimDate[Week]` (1–52) on the X axis. Plot 3 lines: one for each of the last 3 fiscal years. Add a 4th averaged line as the "expected baseline". Helps distinguish genuine growth from seasonal lift.

### Page 5 — Marketing ROI View (with proxy note)

*Audience: Brand Marketing Teams · Adapted because the synthetic dataset lacks the Catering Marketing Spend table*

Add a callout text box at the top of the page:

> **Data substitution note:** This page uses `ReportedSales[DiscountsCY]` as a proxy for total incentive spend, since the synthetic UDI dataset does not contain the `Catering Marketing Spend` table (no `PPP`, `DeliveryFee`, `EZRewards` split). When the real Mktg Spend table is connected, replace `[Discounts (Spend Proxy)]` in every visual on this page with the corresponding spend measure.

1. **Incentive Spend vs Sales Lift.** Visual: Clustered column.
   - Axis = `Brand[BrandName]`.
   - Values = `[Discounts (Spend Proxy)]` and `[Catering 1P Sales]`.
   - Secondary tooltip: `[Discount Rate on Catering]`.
   - Sort by `[Catering 1P Sales]` descending.
2. **Cost per Catering Order.** Visual: Bar.
   - Axis = `Brand[BrandName]`.
   - Value = `[Marketing Cost per Catering Order (Proxy)]`.
   - Conditional formatting: red if > $5/order.
3. **Loyalty → Catering Correlation.** Visual: Scatter.
   - X = `[Loyalty Enrollments]`.
   - Y = `[Total Catering Sales]`.
   - Details = `Unit[UnitNumber]`.
   - Add a trend line (Analytics pane → Trend line). Strong upward slope = loyalty drives catering.
4. **Loyalty Sales as % of Catering by Brand.** Visual: Bar.
   - Axis = `Brand[BrandName]`.
   - Value = `[Loyalty Sales]` and `[Total Catering Sales]` shown as 100% stacked bar to compare scales.

### Page-wide niceties

- **Theme** (View → Themes → Built-in: "Storm" or build a custom GoTo-branded JSON).
- **Page navigation buttons** (Insert → Button → Page navigation) — sticky header on every page.
- **Bookmarks**: "Last Week", "MTD", "QTD", "YTD" — bind to buttons in the top right.
- **Drill-through to Store Detail** (optional): create a hidden Page 6 with a Store Detail layout (KPI strip, sales trend, alert summary) and configure `Unit[UnitNumber]` as the drill-through field. Right-click any chart with `UnitNumber` → Drill through → Store Detail.

---

## Phase 7 — Performance & polish checks

1. **Performance Analyzer** (View → Performance Analyzer → Start recording → click each visual). Anything > 1.5 s on the FBC Action Board is worth investigating — the matrix with conditional flag columns is the heaviest visual.
2. **DAX Studio → View Metrics**: column sizes by table. If `Catering` exceeds 200 MB in-memory, consider:
   - Filtering to last 3 fiscal years for development (one of the page filters).
   - Dropping `Catering[Comp]` if you don't slice by it (Comp % is still computable via DAX with prior-year delta).
3. Check **File → Options → Current File → Regional Settings**: locale = English (United States).
4. **Save as `.pbix`** under `udi_data_gen/dashboards/Catering Analytics Transformation.pbix`.

---

## Phase 8 — Publish to Power BI Service (optional)

1. **Home → Publish** → choose a workspace.
2. After publish, in the Service:
   - **Dataset → Settings → Scheduled refresh** — won't work for local Parquet files unless you install the **On-premises data gateway** and point it at the folder.
   - **Workspace → New → App** to package the report for end users (Brand Leaders, RVPs, FBCs, Brand Managers, Marketing Teams).
3. **Subscriptions / alerts** for FBCs:
   - Open Page 3 (FBC Action Board) → "..." menu → **Subscribe** → weekly Monday morning.
   - On the Alert Count card visual: "..." → **Manage alerts** → threshold "Alert Count > 5" → daily.

---

## Validation checklist

Tick these off before declaring "catering report complete":

- [ ] All 15 tables loaded; row counts match `output/_summary.json`.
- [ ] DimDate marked as date table; Auto Date/Time OFF.
- [ ] 25+ relationships in star shape; `Catering` is the focal fact.
- [ ] `Unit[FranchiseBusinessConsultant]` visible (not hidden).
- [ ] All 12 core catering measures (Section 4.1) created.
- [ ] All 9 time-intelligence catering measures (Section 4.2) created.
- [ ] All 7 store-health flag measures + `Alert Count` + `Alert Level` (Section 4.6) created.
- [ ] Brand, Unit (Geography + Org), DimDate hierarchies built; Org includes FranchiseBusinessConsultant.
- [ ] All 5 catering pages live: Health Scorecard, Channel Intelligence, FBC Action Board, Trends Rebuilt, Marketing ROI.
- [ ] Page 3 alert matrix highlights stores in red/amber/green based on Alert Level.
- [ ] Page 5 has the "data substitution note" callout for the Mktg Spend proxy.
- [ ] Performance Analyzer shows < 1.5 s on each page.
- [ ] Published to a workspace (if Service available).

---

## Common gotchas

| Symptom | Fix |
|---|---|
| Load fails with "Parquet format is not supported" | Update Power BI Desktop — Parquet connector was buggy before May 2024. |
| YoY % returns blank | Check DimDate is marked as date table AND Auto Date/Time is OFF. Both. |
| Alert flags all show BLANK on the Health Scorecard | The flags use measures that require row context to fire (e.g., `MAX(Unit[NextRemodelDate])`). Use them on Page 3 (Franchisee/Unit-level matrix) — not on Page 1 (Brand-level summary). |
| Quadrant scatter looks empty | Likely a single-period filter — quadrants need YoY %, which needs at least 2 years of data in scope. Widen the date filter. |
| Stacked bar shows no 3P share | Some brands have very low 3P presence in the synthetic data — that's by design (brand-personality). Try a different brand filter. |
| Matrix on Page 3 has 4,000 rows | Add `[Alert Count] >= 1` as a visual-level filter — the page is supposed to surface only flagged franchisees. |
| Loading takes > 10 min | Use 25%-scale dataset (`UDI_SCALE=0.25`) for development. |
| Map visual shows fewer markers than expected | Use Azure Maps visual instead of basic Map; set Latitude/Longitude data categories on `Unit`. |
| Cards on Page 1 show whole-portfolio values regardless of slicer | Check the slicer is set to "Apply to all pages" via the Sync Slicers pane. |
| Different totals between PBI and Tableau | Most often: bi-directional cross-filter is on in one tool but not the other. Keep both single-direction. |
