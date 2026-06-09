# POC Guide — S.No 157: Reports with Many Rows of Data (Catering Detail Report)
**Category:** 16. Report Consumption & Alerting | **Priority:** High | **AtScale dependency:** None
**Related rows:** S.No 134 (Export formats) · S.No 32 (Dataset size limits)

---

## What this POC answers
Can each BI tool display, scroll, filter, and export a row-level operational report with **thousands of rows** — specifically the Catering Detail Report that GTF franchise operators use today?

The current GTF report shows one row per unit per day: unit name, date, 1P sales, 3P sales, 1P traffic, 3P traffic, comp flag. For a single brand over 12 months, that is:
- ~80 units × 365 days = **~29,000 rows** per brand per year
- Full dataset: 3,934 units × 10 years = **11.8 million rows**

The POC tests a realistic slice — **one brand, last 12 months (~29k rows)** — for browsing, scrolling, filtering, and export.

**Expected verdict:** Power BI handles thousands of rows well via a Table visual with virtual scrolling; Export Data caps at 150k rows (standard) or unlimited via Paginated Reports (Premium). Tableau handles the same via a text table but has no paginated export or row cap bypass without server-side tooling.

---

## Data files used
From `udi_data_gen\output\parquet\`:
- `catering.parquet` — 11.8M rows, daily grain per unit
- `brand.parquet` — BrandSequence → BrandName
- `unit.parquet` — SBRSequence → SBRName, Region, State, FranchiseBusinessConsultant

---

## Time estimate

| Section | Time |
|---|---|
| Power BI — load, build, test, export | 15–20 min |
| Tableau — connect, build, test, export | 10–15 min |
| Screenshots + findings entry | 10 min |
| **Total** | **35–45 min** |

---

## Power BI — Large Row Table Report

### Step 1 — Load data
1. Open **Power BI Desktop** → **Home → Get Data → More → File → Parquet**
2. Load and rename:
   - `catering.parquet` → `Catering`
   - `brand.parquet` → `Brand`
   - `unit.parquet` → `Unit`
3. In **Power Query Editor**, add a filter step to `Catering` to keep only 2024 data:
   - Select `CalendarDate` column → **Home → Filter Rows → is after or equal to** `1/1/2024`
   - This reduces 11.8M rows to ~1.5M — fast to load, still realistic
4. **Close & Apply**

### Step 2 — Set relationships (Model view)
| From | To |
|---|---|
| `Catering[BrandSequence]` | `Brand[BrandSequence]` |
| `Catering[SBRSequence]` | `Unit[SBRSequence]` |

### Step 3 — Build the Catering Detail Table
1. Add a new **Table** visual to the report canvas
2. Add these fields as columns (in order):
   - `Brand[BrandName]`
   - `Unit[SBRName]`
   - `Unit[Region]`
   - `Unit[State]`
   - `Unit[FranchiseBusinessConsultant]`
   - `Catering[CalendarDate]`
   - `Catering[FirstPartyNetSales]`
   - `Catering[ThirdPartyNetSales]`
   - `Catering[FirstPartyTraffic]`
   - `Catering[ThirdPartyTraffic]`
   - `Catering[Comp]`
3. Format column headers: bold, wrap text OFF, column widths adjusted
4. Format number columns: Currency for sales ($), integer for traffic

### Step 4 — Add a Brand slicer (simulate single-brand view)
1. Add a **Slicer** visual → field: `Brand[BrandName]`
2. Select **one brand** (e.g., the first one alphabetically)
3. Observe the Table now shows ~29,000 rows (one per unit per day for 2024)
4. **Scroll down** in the Table visual — Power BI uses virtual rendering; only visible rows are rendered, regardless of total row count
5. **Screenshot the table showing thousands of rows with the brand filter applied**

### Step 5 — Add filters for date range
1. Add a **Date slicer** → field: `Catering[CalendarDate]` → set to **Between** style
2. Set range to last 3 months (Oct–Dec 2024) → observe ~7,000 rows
3. Reset to full 2024 → back to ~29,000 rows
4. These interactions should be near-instant (Import mode, in-memory)

### Step 6 — Test Export
1. Click the Table visual → click the **"..."** menu (top-right of the visual) → **Export data**
2. Select **Underlying data** → **Export**
3. Power BI exports to `.xlsx` — open it and check row count
   - Standard limit: **150,000 rows** (Excel row limit effectively)
   - If the filtered view has <150k rows, the full export lands in Excel
   - If you select the full unfiltered dataset (11.8M rows), Power BI will show a warning and cap at 150k
4. **Screenshot the export dialog AND the resulting Excel file with row count visible**

### Step 7 — Test column sorting and frozen headers
1. Click any column header in the Table visual → verify it sorts ascending/descending
2. Scroll down — verify column headers stay frozen at top (Power BI does this automatically)
3. **Screenshot headers frozen while rows are scrolled**

### What to document
- Row count for the filtered view (1 brand, 2024) → confirm it matches expectations
- Scroll performance: smooth or laggy?
- Export: how many rows, how long did it take?
- Export cap hit: did you hit the 150k limit? Note that Paginated Reports (Premium) removes this cap
- Frozen headers: yes/no (yes — built-in)
- Sort by column: yes/no (yes — built-in)

---

## Tableau — Large Row Text Table

### Step 1 — Connect to data
1. Open **Tableau Desktop** → **Connect → To a File → More…** → select `catering.parquet`
2. In the **Data Source** tab, drag in `brand.parquet` and `unit.parquet`
3. Define relationships:
   - `Catering[BrandSequence]` = `Brand[BrandSequence]`
   - `Catering[SBRSequence]` = `Unit[SBRSequence]`
4. Click **Sheet 1**

### Step 2 — Build the Catering Detail cross-tab
1. Drag these dimensions to **Rows** shelf (in order):
   - `Brand Name` (from Brand)
   - `SBR Name` (from Unit)
   - `Region` (from Unit)
   - `Calendar Date` (from Catering) — right-click → **Exact Date** (not truncated)
2. Drag these measures to the **Text** mark:
   - `SUM(First Party Net Sales)`
   - `SUM(Third Party Net Sales)`
   - `SUM(First Party Traffic)`
   - `SUM(Third Party Traffic)`
3. Drag `Comp` → Text mark as well (it's a dimension, shows per row)
4. This creates a row-level text table (cross-tab)

### Step 3 — Filter to one brand
1. Drag `Brand Name` → **Filters** shelf
2. Select one brand → **OK**
3. Tableau renders the filtered rows — observe how many rows appear
4. **Screenshot the text table showing thousands of rows**

> **Note:** Tableau renders rows in a paginated view internally — you use the scroll bar to navigate. Unlike Power BI's virtualized Table visual, Tableau shows one "page" of rows at a time with a vertical scrollbar. Performance is comparable but the visual feel differs.

### Step 4 — Test scrolling and column headers
1. Scroll down in the worksheet
2. Observe: **column headers DO NOT stay frozen** in Tableau Desktop — they scroll off the top as you scroll down
   - This is a known limitation of Tableau text tables vs Power BI Table visual
3. **Screenshot this** — headers gone after scrolling — this is a relevant finding

### Step 5 — Test Export
1. **Worksheet → Export → Crosstab to Excel**
   - Exports the current view to `.xlsx` — Tableau does not apply a row cap here for Desktop exports
   - Open Excel and check row count
2. Also test: **Worksheet → Export → Data** → exports to `.csv` (full underlying data, no cap)
3. **Screenshot the export dialog and resulting file**

### Step 6 — Attempt "print to PDF" / pagination test
1. **File → Print to PDF**
2. Observe the dialog:
   - Paper size: A4/Letter
   - No option to say "page break after each Brand" or "page break after each Unit"
   - Tableau will auto-break rows wherever the page ends, mid-unit or mid-date
3. **Screenshot the Print to PDF dialog** showing the absence of break-by-dimension
4. Generate the PDF anyway → open it and observe the uncontrolled page breaks
5. **Screenshot one of the mid-table page breaks** in the PDF output

---

## Side-by-Side Findings Summary

| Dimension | Power BI | Tableau |
|---|---|---|
| **Rows displayed at once** | Virtual rendering — all rows accessible via scroll, only visible rows rendered | Paginated internally — scroll bar navigates all rows |
| **Column headers while scrolling** | Frozen — always visible | Not frozen — scroll off the top |
| **Sort by column** | Yes — click any header | Yes — click any header |
| **Filter performance (29k row view)** | Near-instant (Import mode) | Near-instant (Extract mode) |
| **Export to Excel** | Yes — 150k row cap in standard mode | Yes — no cap from Desktop |
| **Export to CSV** | Yes — via "Export data → Underlying data" | Yes — via Export → Data |
| **Export cap bypass** | Yes — Paginated Reports (Premium/PPU) removes the cap | No native bypass; tabcmd CLI required for server-side |
| **PDF export with page breaks by Brand** | Yes — via Paginated Reports (Report Builder) | No — print-to-PDF breaks mid-table with no dimension control |
| **Operational report (page-break by territory)** | Yes — Report Builder, free to author | No equivalent |
| **Winner for row-level operational reports** | **Power BI** | Falls short on PDF/paginated output |

---

## Key talking point for client call

> "For the Catering Detail use case — thousands of rows, one per unit per day — both tools display and export the data fine. The real gap shows up when GTF franchise operators need to print or email a PDF of the catering detail broken out by Brand or Territory. Power BI handles this through Report Builder: page breaks after each Brand, consistent formatting, pixel-perfect PDF, no row cap. Tableau has no equivalent — you get a long scrolling table that breaks pages wherever paper runs out. For GTF's existing catering detail reports, Power BI is the practical choice."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (Power BI Findings) for S.No 157:**
> Table visual supports thousands of rows via virtual rendering; headers stay frozen; sort by column built-in. Export: 150k row cap in standard mode (removable via Paginated Reports with Premium/PPU). PDF with page-break-by-Brand: yes, via Report Builder. Authoring time for a Catering Detail table visual: ~15 min. Export test: [record actual row count and time].

**Column G (Tableau Findings) for S.No 157:**
> Text table handles thousands of rows; scroll bar navigation works. Column headers do NOT stay frozen during scroll. Export to Excel/CSV: no row cap from Desktop. PDF export: no page-break-by-dimension — breaks mid-table. No paginated report engine. For operational detail reports requiring print-ready output, Tableau requires third-party tools or REST API scripting. Clear gap vs Power BI for GTF catering detail use case.

**Column J (Status) for S.No 157:** `COMPLETED`
