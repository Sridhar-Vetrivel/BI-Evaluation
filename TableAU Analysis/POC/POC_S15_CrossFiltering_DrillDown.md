# POC Guide — S.No 15: Cross-Filtering and Drill-Down / Drill-Through Behavior
**Category:** 2. Visualization & UX | **Priority:** High | **AtScale dependency:** None

> **Note on numbering:** S.No 14 in Discovery.xlsx is "Conditional Formatting." Cross-filtering and drill-down is **S.No 15**. Update Column F/G/J for row S.No 15.

---

## Scenario (GTF-specific)
Build a **Brand Performance Dashboard** that a Franchise Business Consultant (FBC) uses daily:

- **Page 1 — Brand Overview:** Brand slicer, KPI cards, bar chart of Revenue by Unit, line chart of Revenue over time
- **Cross-filter test:** Clicking a Brand in the slicer propagates to all visuals instantly
- **Drill-down test:** Bar chart drills from Brand-level totals → individual Unit-level bars
- **Drill-through test:** Right-click / select a Unit → navigate to a Unit Detail page showing that unit's FBC, Franchisee, ranked comp sales

This is a real GTF use case — Brand Leaders scan the Brand bar chart, drill into the units that are underperforming, and jump to the unit detail to find who the FBC is and whether the unit is comp-ranked.

**Expected verdict:** Power BI cross-filtering is on by default (zero setup). Tableau requires manually wiring Filter Actions for every visual pair. Drill-through in Power BI is a right-click context menu item. Tableau requires a Dashboard Action to be configured explicitly.

---

## Data files used
From `udi_data_gen\output\parquet\`:
- `reported_sales.parquet` — NetSalesCY, NetSalesPY, TrafficCY, CateringCY, BrandSequence, SBRSequence, CalendarDate
- `brand.parquet` — BrandSequence, BrandName, Concept
- `unit.parquet` — SBRSequence, SBRName, Region, State, FranchiseBusinessConsultant, Franchisee
- `dimdate.parquet` — CalendarDate, Year, Quarter, Month, MonthName
- `unit_ranking_base.parquet` — SBRSequence, BrandSequence, CompSalesCY, CompSalesPY, FBC, Franchisee, Ranked, CalendarDate

---

## Time estimate

| Section | Time |
|---|---|
| Power BI — model, measures, 2 pages, test all 3 behaviors | 25–30 min |
| Tableau — model, dashboard, actions, hierarchy, detail sheet | 25–30 min |
| Screenshots + findings entry | 10 min |
| **Total** | **60–70 min** |

---

## Power BI — Cross-Filtering, Drill-Down, Drill-Through

### Step 1 — Load data
1. Open **Power BI Desktop** → **Get Data → More → File → Parquet**
2. Load and rename all 5 files:
   - `reported_sales.parquet` → `ReportedSales`
   - `brand.parquet` → `Brand`
   - `unit.parquet` → `Unit`
   - `dimdate.parquet` → `DimDate`
   - `unit_ranking_base.parquet` → `UnitRanking`
3. In Power Query Editor, filter `ReportedSales` to 2024 only:
   - Select `CalendarDate` → **Filter Rows → is after or equal to** `1/1/2024`
4. **Close & Apply**

### Step 2 — Set relationships (Model view)
| From (Many) | To (One) |
|---|---|
| `ReportedSales[BrandSequence]` | `Brand[BrandSequence]` |
| `ReportedSales[SBRSequence]` | `Unit[SBRSequence]` |
| `ReportedSales[CalendarDate]` | `DimDate[CalendarDate]` |
| `UnitRanking[SBRSequence]` | `Unit[SBRSequence]` |
| `UnitRanking[BrandSequence]` | `Brand[BrandSequence]` |

All relationships: many-to-one, single direction.

### Step 3 — Create measures
In the `ReportedSales` table:

```dax
Total Net Sales = SUM(ReportedSales[NetSalesCY])

Prior Year Sales = SUM(ReportedSales[NetSalesPY])

YoY Change = [Total Net Sales] - [Prior Year Sales]

YoY % = DIVIDE([YoY Change], [Prior Year Sales], 0)

Total Traffic = SUM(ReportedSales[TrafficCY])
```

### Step 4 — Build the hierarchy for drill-down
1. In **Data pane**, go to the `Brand` table
2. Right-click `BrandName` → **Create hierarchy** → name it `Brand Hierarchy`
3. Drag `Unit[SBRName]` into this hierarchy (or in Model view, drag SBRName under BrandName)
   - Result: `Brand Hierarchy` = BrandName → SBRName

### Step 5 — Build Page 1: Brand Overview

**Visual A — Brand Slicer (top-left)**
1. Add a **Slicer** visual → field: `Brand[BrandName]`
2. Style: Dropdown, single select

**Visual B — KPI Cards (top-right row, 3 cards)**
- Card 1: `[Total Net Sales]` — label: "Net Sales 2024"
- Card 2: `[YoY Change]` — label: "YoY $ Change"
- Card 3: `[YoY %]` — label: "YoY %" → format as percentage

**Visual C — Revenue by Unit Bar Chart (center)**
1. Add **Clustered Bar Chart**
2. Y-axis: `Brand Hierarchy` (drag the hierarchy, not just BrandName)
3. X-axis: `[Total Net Sales]`
4. Sort descending
5. Title: "Revenue by Brand / Unit"
6. Notice: the visual shows a **drill-down arrow** in the top-right corner automatically

**Visual D — Revenue Over Time Line Chart (bottom)**
1. Add **Line Chart**
2. X-axis: `DimDate[MonthName]` (sort by Month number)
3. Values: `[Total Net Sales]`, `[Prior Year Sales]`
4. Title: "Monthly Revenue — CY vs PY"

### Step 6 — TEST: Cross-filtering (the key test)
1. On the Brand slicer, **click any one brand** (e.g., the first brand)
2. Observe: the bar chart, the line chart, and all KPI cards update instantly to show only that brand's data
3. Now **click a bar** in the bar chart (click directly on a unit's bar)
4. Observe: the line chart and KPI cards further filter to that unit
5. Click elsewhere to deselect
6. **This required zero setup — it is automatic in Power BI**
7. **Screenshot: one brand selected in slicer → all visuals filtered**

> To verify: go to **Format visual → Edit interactions** on any visual — you can see/modify which visuals are affected. Default is all visuals cross-filter each other.

### Step 7 — TEST: Drill-down (Brand → Unit)
1. Click the **bar chart** to select it
2. At the top of the visual, click the **down-arrow drill-down icon** (single arrow pointing down-right)
3. Now click on **any Brand bar** — the chart drills down to show that brand's individual units as separate bars
4. To drill back up: click the **up-arrow** at the top of the visual
5. Alternatively: click the **fork icon** (drill all levels) to expand all brands to show units simultaneously
6. **Screenshot: the bar chart showing Unit-level bars after drilling down from a Brand**

### Step 8 — Build Page 2: Unit Detail (drill-through target)
1. Add a new page → rename it `Unit Detail`
2. In the **Filters pane** on this page → under **Drill-through** section → drag `Unit[SBRName]`
   - This registers the page as a drill-through target for Unit-level context
3. Add these visuals on the page:
   - **Table:** `Unit[SBRName]`, `Unit[FranchiseBusinessConsultant]`, `Unit[Franchisee]`, `Unit[Region]`, `Unit[State]`
   - **KPI Card:** `[Total Net Sales]` with title "Unit Net Sales 2024"
   - **Line Chart:** Monthly Net Sales for the unit (`DimDate[MonthName]` × `[Total Net Sales]`)
4. Power BI automatically adds a **Back button** to the page — leave it visible

### Step 9 — TEST: Drill-through (Unit → Unit Detail page)
1. Go back to **Brand Overview** page
2. Drill down into a brand to see individual unit bars (Step 7)
3. **Right-click on any unit bar** → a context menu appears
4. Click **Drill through → Unit Detail**
5. Observe: you land on the Unit Detail page, showing data only for the unit you right-clicked
6. Click **Back** to return to Brand Overview
7. **Screenshot: the right-click drill-through context menu appearing on a bar**

### What to document
- Cross-filter: did it work with zero setup? (Yes)
- Drill-down: drill arrow visible on bar chart automatically? (Yes, because hierarchy was attached)
- Drill-through: right-click context menu appeared? (Yes, because Unit Detail page was registered)
- Any lag or issues navigating back?

---

## Tableau — Cross-Filtering, Drill-Down, Drill-Through

### Step 1 — Connect to data
1. Open **Tableau Desktop** → **Connect → To a File → More…** → select `reported_sales.parquet`
2. In **Data Source** tab, drag in: `brand.parquet`, `unit.parquet`, `dimdate.parquet`, `unit_ranking_base.parquet`
3. Define relationships in the logical layer:
   - `Reported Sales[BrandSequence]` = `Brand[BrandSequence]`
   - `Reported Sales[SBRSequence]` = `Unit[SBRSequence]`
   - `Reported Sales[CalendarDate]` = `DimDate[CalendarDate]`
   - `Unit Ranking Base[SBRSequence]` = `Unit[SBRSequence]`
4. Click **Sheet 1**

### Step 2 — Create calculated fields
1. **Analysis → Create Calculated Field:**
   - `Total Net Sales` = `SUM([Net Sales CY])`
   - `Prior Year Sales` = `SUM([Net Sales PY])`
   - `YoY Change` = `[Total Net Sales] - [Prior Year Sales]`
   - `YoY %` = `([Total Net Sales] - [Prior Year Sales]) / [Prior Year Sales]`

### Step 3 — Define the drill-down hierarchy
1. In the **Data** pane, find `Brand Name` (from Brand table)
2. Right-click `Brand Name` → **Hierarchy → Create Hierarchy** → name it `Brand > Unit`
3. Drag `SBR Name` (from Unit table) → onto the `Brand > Unit` hierarchy (below Brand Name)
4. Result: `Brand > Unit` hierarchy = Brand Name → SBR Name

### Step 4 — Build Sheet 1: Revenue by Brand (Bar Chart)
1. Rename **Sheet 1** → `Revenue by Brand`
2. Drag `Brand Name` → **Rows** shelf (use the hierarchy pill — shows + expand icon)
3. Drag `Total Net Sales` → **Columns** shelf
4. Sort descending: click the sort descending icon on the axis
5. Title: "Revenue by Brand / Unit"

### Step 5 — Build Sheet 2: Revenue Over Time (Line Chart)
1. New sheet → rename `Revenue Over Time`
2. Drag `Month Name` (from DimDate) → **Columns** shelf
3. Drag `Total Net Sales`, `Prior Year Sales` → **Rows** shelf
4. Right-click `Prior Year Sales` axis → **Dual Axis** → Synchronize
5. Title: "Monthly Revenue — CY vs PY"

### Step 6 — Build Sheet 3: KPI Cards
1. New sheet → rename `KPI Cards`
2. Build 3 separate text vizzes:
   - Sheet: `KPI_Sales` → Drop `Total Net Sales` on Text mark → title "Net Sales 2024"
   - Sheet: `KPI_YoY` → Drop `YoY Change` on Text mark → title "YoY $ Change"
   - Sheet: `KPI_Pct` → Drop `YoY %` on Text → format as % → title "YoY %"

### Step 7 — Build the Dashboard: Brand Overview
1. Click **New Dashboard** icon → rename it `Brand Overview`
2. Drag sheets onto the dashboard:
   - Top-left: a **Quick Filter** (right-click Brand Name on any sheet → Show Filter)
   - Center: `Revenue by Brand`
   - Bottom: `Revenue Over Time`
   - Top-right row: the 3 KPI sheets

### Step 8 — TEST and CONFIGURE: Cross-filtering (manual setup required)
1. Click on the `Revenue by Brand` chart on the dashboard
2. Click the **funnel/filter icon** that appears in the top-right corner of the sheet
3. This turns the sheet into a **filter source** — selecting a bar now filters OTHER sheets
4. Repeat for the other sheets if needed
5. Now click a brand bar → other visuals filter
6. **Screenshot: brand bar selected → other sheets filtered**

> **Key finding:** In Power BI this was automatic (zero setup). In Tableau you must explicitly click the filter icon on each source sheet, or go to **Dashboard → Actions → Add Action → Filter** to configure more granular control. For multiple sheets cross-filtering each other, each pair must be configured.

**Advanced (optional — shows the real effort):**
Go to **Dashboard → Actions → Add Action → Filter**:
- Source sheets: `Revenue by Brand`
- Target sheets: `Revenue Over Time`, all KPI sheets
- Run action on: Select
- Clearing the selection: Show all values
This gives you precise control — but it's manual work for every pair.

### Step 9 — TEST: Drill-down (Brand → Unit)
1. Click on the `Revenue by Brand` sheet (not on the dashboard — double-click to enter the sheet)
2. Click the **+** expand icon next to a Brand Name in the Rows shelf, or:
   - Click the **+** icon on the Brand Name pill at the top of the viz
3. The view expands to show individual unit rows under that brand
4. To collapse: click the **–** icon
5. **Screenshot: expanded Brand showing unit rows underneath**

> **Note:** Tableau's drill-down via hierarchy expansion is different from Power BI's visual drill. In Tableau, expanding a hierarchy adds rows to the table; it does not change the mark type or visual structure. To get a true drill-replace behavior (Brand bars replaced by Unit bars when drilling), you need a **Set Action** — which is additional configuration.

### Step 10 — Build Sheet 4: Unit Detail (drill-through target)
1. New sheet → rename `Unit Detail`
2. Drag to Rows: `SBR Name`, `FBC` (from Unit Ranking Base), `Franchisee`, `Region`, `State`
3. Drag `Total Net Sales` → Text mark
4. Sort descending by Total Net Sales
5. Add a Filter: drag `SBR Name` → Filters shelf (this will receive the context from the action)

### Step 11 — Configure the drill-through Dashboard Action
1. Go back to **Brand Overview** dashboard
2. **Dashboard → Actions → Add Action → Filter**
   - Name: `Drill to Unit Detail`
   - Source sheets: `Revenue by Brand`
   - Run action on: **Select**
   - Target sheets: `Unit Detail`
   - Source field: `SBR Name` / Target field: `SBR Name`
3. Now select a unit bar in the `Revenue by Brand` chart (after drilling down to unit level)
4. Navigate to `Unit Detail` — it is now filtered to the selected unit
5. **Screenshot: Unit Detail sheet filtered to one unit after selecting from the bar chart**

> **Note:** Unlike Power BI's right-click drill-through (which navigates to a separate page in the same flow), Tableau requires the user to manually navigate to the `Unit Detail` sheet/dashboard. There is no automatic navigation. You can add a **URL Action** to navigate, or build a separate Unit Detail dashboard and use a **Navigate Action** — but this is additional configuration.

---


## Side-by-Side Findings Summary

| Behavior | Power BI | Tableau |
|---|---|---|
| **Cross-filtering setup** | Automatic — all visuals on the same page cross-filter by default | Manual — must click the filter icon per sheet, or configure Dashboard Actions |
| **Cross-filter granularity control** | Visual interactions editor (per visual, per page) | Dashboard Actions with full source/target control |
| **Drill-down on hierarchy** | Click the drill arrow on the visual — replaces the visual with the next level | Click + to expand rows in place; Set Actions needed to replace-and-drill |
| **Drill-down feel** | Replaces the chart content — same visual, new level | Expands rows — table grows, does not replace the chart |
| **Drill-through to detail page** | Right-click → Drill through → page name (zero setup on source) | Requires a Filter/Navigate Dashboard Action to be configured |
| **Navigation back from drill-through** | Automatic Back button on the drill-through page | No automatic back; user navigates manually |
| **Hierarchy auto-detection from AtScale** | Yes — AtScale-defined hierarchies surface in Power BI automatically via XMLA | Requires manual definition in Tableau's logical layer even if AtScale defines them |
| **Winner** | **Power BI** — less setup, more intuitive for end users | Capable but every behavior requires manual wiring |

---

## Key talking point for client call

> "Both tools support cross-filtering, drill-down, and drill-through. The difference is how much the author has to wire it up. In Power BI, a report author drops visuals on a page and cross-filtering works automatically — no configuration. In Tableau, every visual pair that should cross-filter needs a manual Filter Action. Drill-through in Power BI is a right-click option that appears automatically once a drill-through page is registered. In Tableau, you configure a Dashboard Action and the user has to navigate between sheets themselves. For GTF's FBC-facing dashboards — where drill from Brand to Unit to Unit Detail is a core daily workflow — Power BI's approach is noticeably faster for both authors and end users."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (Power BI Findings) for S.No 15:**
> Cross-filtering: automatic between all visuals on a page, zero setup. Edit interactions to adjust per pair. Drill-down: hierarchy attached to a visual shows drill arrow; click to replace the chart with the next level. Drill-through: register a page as drill-through target, right-click on any data point to navigate with filter context. Back button auto-generated. AtScale hierarchies surface automatically via XMLA.

**Column G (Tableau Findings) for S.No 15:**
> Cross-filtering: not automatic — requires Filter Action per source/target pair, or filter icon click per sheet. Drill-down via hierarchy: expands rows in place (does not replace the chart view); Set Actions needed for replace-level drill. Drill-through: Filter + Navigate Dashboard Actions required; no automatic Back button. Manual but highly configurable once set up. AtScale hierarchies must be re-defined in Tableau's logical layer.

**Column J (Status) for S.No 15:** `COMPLETED`
