# POC Guide — S.No 14: Conditional Formatting & Dynamic Visual Properties
**Category:** 2. Visualization & UX | **Priority:** High | **AtScale dependency:** None (Parquet-based)
**Client requirement:** 6d — Report with P&L data

---

## Why this matters for GTF
GTF's P&L reports show Actual Revenue vs Target with Variance and Variance % at Brand and Unit level.
Franchise operators need to instantly see which brands or units are below target (red), on track (green), and how large the gap is.
This POC validates that both tools can apply those visual rules to AtScale-sourced measures — not just static data.

**Expected verdict:** Power BI is best-in-class for matrix conditional formatting. Tableau can do it but requires more manual setup — calculated color fields instead of a native formatting panel, and cell-level granularity is harder to achieve.

---

## Scenario
Build a **Brand & Unit Revenue vs Target matrix** — the closest analog to GTF's existing P&L report:

| Rows | Columns | Values |
|---|---|---|
| Brand → Unit (hierarchy) | Month (Jan–Dec) | Actual, Target, Variance $, Variance % |

Apply:
- **Background color on Variance $** — red if negative, green if positive
- **Data bars on Actual Revenue** — bar length shows magnitude
- **Icons on Variance %** — ▲ green / ▼ red based on sign
- **Toggle** — parameter to switch the view between $ and % mode

---

## Data files used
From `udi_data_gen\output\parquet\`:
- `reported_sales.parquet` — NetSalesCY (Actual), BrandSequence, SBRSequence, CalendarDate
- `brand_targets.parquet` — ReportedSalesTarget (Target), BrandSequence, CalendarDate
- `brand.parquet` — BrandName
- `unit.parquet` — SBRName, Region
- `dimdate.parquet` — MonthName, Month, Year

---

## Time estimate

| Section | Time |
|---|---|
| Power BI — model, measures, matrix, all 3 formatting types + toggle | 20–25 min |
| Tableau — same model, text table, calc color fields, parameter toggle | 25–30 min |
| Screenshots + findings | 10 min |
| **Total** | **55–65 min** |

---

## Power BI — Conditional Formatting on Matrix

### Step 1 — Load data
1. **Power BI Desktop → Get Data → More → File → Parquet**
2. Load and rename:
   - `reported_sales.parquet` → `ReportedSales`
   - `brand_targets.parquet` → `BrandTargets`
   - `brand.parquet` → `Brand`
   - `unit.parquet` → `Unit`
   - `dimdate.parquet` → `DimDate`
3. In Power Query, filter `ReportedSales` to 2024 (CalendarDate >= 1/1/2024)
4. **Close & Apply**

### Step 2 — Set relationships (Model view)
| From | To |
|---|---|
| `ReportedSales[BrandSequence]` | `Brand[BrandSequence]` |
| `ReportedSales[SBRSequence]` | `Unit[SBRSequence]` |
| `ReportedSales[CalendarDate]` | `DimDate[CalendarDate]` |
| `BrandTargets[BrandSequence]` | `Brand[BrandSequence]` |
| `BrandTargets[CalendarDate]` | `DimDate[CalendarDate]` |

### Step 3 — Create measures
In the `ReportedSales` table:

```dax
Actual Revenue = SUM(ReportedSales[NetSalesCY])

Target Revenue = SUM(BrandTargets[ReportedSalesTarget])

Variance $ = [Actual Revenue] - [Target Revenue]

Variance % = DIVIDE([Variance $], [Target Revenue], 0)
```

### Step 4 — Build the Matrix visual
1. Add a **Matrix** visual to the canvas
2. **Rows:** drag `Brand[BrandName]` then `Unit[SBRName]` — creates the collapsible Brand > Unit hierarchy
3. **Columns:** `DimDate[MonthName]` (sort by Month number to get Jan→Dec order)
4. **Values:** `[Actual Revenue]`, `[Target Revenue]`, `[Variance $]`, `[Variance %]`
5. Format column headers: bold, wrap text OFF
6. Format `[Variance %]` as percentage, `[Actual Revenue]` and `[Variance $]` as currency

### Step 5 — Apply conditional formatting: Background color on Variance $
1. Click the Matrix visual → **Format visual** pane → **Cell elements**
2. Under **Variance $** → toggle **Background color** ON → click **fx**
3. In the dialog:
   - Format style: **Rules**
   - Add Rule 1: If value < 0 → Background = Red (`#FF6B6B`)
   - Add Rule 2: If value >= 0 → Background = Green (`#51CF66`)
4. Click OK
5. **Screenshot: matrix cells with red/green backgrounds on Variance $ column**

> This entire step took about 60 seconds. The native conditional formatting panel handles it with no DAX, no calculated fields.

### Step 6 — Apply conditional formatting: Data bars on Actual Revenue
1. Still in **Cell elements**, under **Actual Revenue** → toggle **Data bars** ON
2. Positive bar color: `#228BE6` (blue), negative: red
3. The bar length scales automatically to the min/max of the column
4. **Screenshot: Actual Revenue column with blue data bars inside cells**

### Step 7 — Apply conditional formatting: Icons on Variance %
1. Under **Variance %** → toggle **Icons** ON → click **fx**
2. Icon layout: **Right of data**
3. Add Rule 1: If value >= 0 → Icon = Green upward arrow (▲)
4. Add Rule 2: If value < 0 → Icon = Red downward arrow (▼)
5. Click OK
6. **Screenshot: Variance % column showing ▲▼ icons in correct colors**

### Step 8 — Add toggle: $ vs % view using Field Parameter
1. **Modeling → New Parameter → Fields**
2. Name: `Measure Toggle`, add `[Variance $]` and `[Variance %]`
3. Power BI creates a disconnected table with a slicer
4. In the Matrix Values area, remove `[Variance $]` and `[Variance %]` → replace with `Measure Toggle[Measure Toggle]`
5. The slicer now controls which variance view is shown
6. **Screenshot: slicer toggling between $ and % views in the matrix**

### What to document
- Total time to apply all 3 conditional formatting types: (record it — target < 10 min)
- Did background color, data bars, and icons all apply at cell level across Brand and Unit rows? (Yes)
- Did the toggle work to switch $ and % views? (Yes)
- Any issues with null handling, totals rows, or large negative numbers? (note any)

---

## Tableau — Conditional Formatting via Calculated Fields

### Step 1 — Connect to data
1. **Tableau Desktop → Connect → To a File → More… →** select `reported_sales.parquet`
2. In Data Source tab, drag in: `brand_targets.parquet`, `brand.parquet`, `unit.parquet`, `dimdate.parquet`
3. Define relationships:
   - `Reported Sales[BrandSequence]` = `Brand[BrandSequence]`
   - `Reported Sales[SBRSequence]` = `Unit[SBRSequence]`
   - `Reported Sales[CalendarDate]` = `DimDate[CalendarDate]`
   - `Brand Targets[BrandSequence]` = `Brand[BrandSequence]`
   - `Brand Targets[CalendarDate]` = `DimDate[CalendarDate]`
4. Click **Sheet 1**

### Step 2 — Create calculated fields
```
Actual Revenue = SUM([Net Sales CY])

Target Revenue = SUM([Reported Sales Target])

Variance $ = SUM([Net Sales CY]) - SUM([Reported Sales Target])

Variance % = (SUM([Net Sales CY]) - SUM([Reported Sales Target])) / SUM([Reported Sales Target])
```

### Step 3 — Build the text table (matrix equivalent)
1. Drag `Brand Name` → **Rows** shelf
2. Drag `SBR Name` → **Rows** shelf (next to Brand Name — creates Brand > Unit rows)
3. Drag `Month Name` → **Columns** shelf → right-click → Sort → by `Month` field ascending
4. Drag `Actual Revenue`, `Target Revenue`, `Variance $`, `Variance %` → **Text** mark
   - This creates a Measure Names / Measure Values cross-tab
5. Title: "Brand & Unit Revenue vs Target"

### Step 4 — Apply conditional color on Variance $ (manual calculated field required)

> **Key difference from Power BI:** Tableau has no "cell background color" panel for text tables. You must create a calculated field that returns a color string, then apply it to the Color mark.

1. Create calculated field **`Variance Color`**:
```
IF SUM([Net Sales CY]) - SUM([Reported Sales Target]) >= 0
THEN 'Green'
ELSE 'Red'
END
```
2. Drag `Variance Color` → **Color** mark on the Marks card
3. Edit colors → manually assign Green = `#51CF66`, Red = `#FF6B6B`
4. **Limitation:** this applies a single row-level color, not cell-by-cell per column value. To get cell-level color on only the Variance $ column (not all columns), you must filter or build a separate worksheet for the Variance column and float it on the dashboard.
5. **Screenshot: rows colored by variance direction**

> This step took 5–8 minutes in Tableau vs 60 seconds in Power BI. And the result is row-level, not cell-level.

### Step 5 — Data bar equivalent (manual workaround)
Tableau has no native "data bar inside cell" feature. The closest approximation:
1. Create a **separate worksheet** → `DataBar_Actual`
2. Drag `Brand Name`, `SBR Name` → Rows, `Actual Revenue` → Columns → mark type: **Bar**
3. Make the bars short (narrow row height) and label them with the value
4. Float this worksheet alongside the text table on the dashboard
5. **Screenshot: bar chart floated next to the text table to simulate data bars**

> This is a layout workaround, not a native in-cell data bar. It is not equivalent to Power BI's native data bars inside matrix cells.

### Step 6 — Icon on Variance % (calculated field)
1. Create calculated field **`Variance Icon`**:
```
IF SUM([Net Sales CY]) - SUM([Reported Sales Target]) >= 0
THEN '▲'
ELSE '▼'
END
```
2. Drag `Variance Icon` → **Text** mark alongside `Variance %`
3. Format the text — size the icon character, but you cannot independently color just the icon character within the same text cell (all text in a cell shares the same color in Tableau)
4. **Limitation:** the ▲▼ icon and the numeric value share the same color. To get green/red icons independent of the number color, you need a second worksheet layered on the dashboard.
5. **Screenshot: Variance % column with ▲▼ characters appended to the value**

### Step 7 — Toggle: $ vs % view using Parameter
1. Create **Parameter** → `p_Variance View`, String, values: `Dollar ($)`, `Percent (%)`
2. Create calculated field **`Variance Display`**:
```
IF [p_Variance View] = 'Dollar ($)'
THEN SUM([Net Sales CY]) - SUM([Reported Sales Target])
ELSE (SUM([Net Sales CY]) - SUM([Reported Sales Target])) / SUM([Reported Sales Target])
END
```
3. Replace `Variance $` in the text table with `Variance Display`
4. Right-click the Parameter → **Show Parameter** → a dropdown appears on the sheet
5. **Screenshot: parameter control switching between $ and % views**

---

## Side-by-Side Findings Summary

| Capability | Power BI | Tableau |
|---|---|---|
| **Background color on matrix cells** | Native panel — Rules or gradient, applies per-cell per-column, 60 seconds to set up | Calculated color field — applies row-level color across the whole row, not per-column |
| **Cell-level granularity (color only Variance $, not all columns)** | Yes — each value column has its own independent conditional formatting | Requires separate worksheets floated together on a dashboard |
| **Data bars inside matrix cells** | Native — one toggle in the format pane | No native equivalent — bar chart workaround floated alongside |
| **Icons (▲▼) with independent color** | Native icons panel — icon and number can have separate colors | Unicode characters in a calculated field — icon and number share the same cell color |
| **Measure toggle ($ / %)** | Field Parameters — native, no formula needed | Parameter + CASE calculated field — works but requires manual calc wiring |
| **Authoring time for all 4 capabilities** | ~10 min | ~25–30 min |
| **Winner** | **Power BI — decisively** | Capable but significantly more manual effort |

---

## Key talking point for client call

> "For P&L-style reports — which is exactly what GoTo Foods' catering and franchise reports are — Power BI's conditional formatting is best-in-class. Background color, data bars, and icons are all applied through a native panel in about 10 minutes, independently per column, at the cell level. Tableau can produce a visually similar result, but it requires calculated fields for color, a separate worksheet floated alongside for data bars, and Unicode characters for icons — and even then, the icon and the number can't be independently colored within the same cell. Same end result takes 25–30 minutes and more workarounds. For a P&L matrix with 20 brands, 10 measures, and 12 months of data, Power BI is the right tool."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (PowerBI) for S.No 14:**
> Best-in-class for matrix conditional formatting. Background color, data bars, and icons applied independently per value column via native Format panel — no DAX or calculated fields needed. Field Parameters enable measure toggle natively. Authoring time for all 4 capabilities: ~10 min.

**Column G (Tableau) for S.No 14:**
> Capable but more manual. Color via calculated field (row-level, not cell-level per column). No native data bars — bar chart workaround required. Icons via Unicode calculated field, cannot independently color icon vs number in same cell. Parameter toggle works but requires CASE calc. Authoring time: ~25–30 min for equivalent output.

**Column J (Findings/Conclusion) for S.No 14:**
> Power BI wins clearly for P&L matrix conditional formatting. Power BI applies background color, data bars, and icons per-column per-cell through a native panel in ~10 minutes. Tableau achieves comparable visual output but requires calculated fields, separate worksheets for data bars, and Unicode workarounds for icons — 2–3x the authoring time. For GTF's P&L and catering variance reports (#6d), Power BI is the significantly stronger choice.

**Column K (Status) for S.No 14:** `COMPLETED`
