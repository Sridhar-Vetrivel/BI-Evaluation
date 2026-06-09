# POC Guide — S.No 16: Tooltip Customization & Rich Interactivity
**Category:** 2. Visualization & UX | **Priority:** High | **AtScale dependency:** None

## Scenario (GTF-specific)
Build a **Catering Revenue by Brand** bar chart. When the user hovers over any brand bar, a rich tooltip appears showing:
- Monthly 1P vs 3P catering sales trend for that brand (sparkline / mini bar)
- Top 5 Units by catering revenue for that brand

This mirrors exactly how a GoTo Foods Brand Manager would use the report — scan the brand-level summary, hover to see the trend and which units are driving or dragging performance.

**Expected verdict:** Tableau's Viz-in-Tooltip produces this with a single checkbox. Power BI requires authoring a separate tooltip page (more setup, same outcome).

---

## Data files used
All from `udi_data_gen\output\parquet\`:
- `catering.parquet` — FirstPartyNetSales, ThirdPartyNetSales, BrandSequence, SBRSequence, CalendarDate
- `brand.parquet` — BrandSequence, BrandName, Concept
- `unit.parquet` — SBRSequence, SBRName, FranchiseBusinessConsultant, Region
- `dimdate.parquet` — CalendarDate, MonthName, Year, Month

---

## Power BI — Report Page Tooltips

### Estimated time: 25–35 minutes

### Step 1 — Load data (skip if model already loaded)
1. Open **Power BI Desktop** → **Get Data → More → File → Parquet**
2. Load these 4 files, renaming queries in Power Query Editor:
   - `catering.parquet` → `Catering`
   - `brand.parquet` → `Brand`
   - `unit.parquet` → `Unit`
   - `dimdate.parquet` → `DimDate`
3. Click **Close & Apply**

### Step 2 — Set relationships (Model view)
In **Model view**, drag to create these relationships (all many-to-one, single direction):
| From | To |
|---|---|
| `Catering[BrandSequence]` | `Brand[BrandSequence]` |
| `Catering[SBRSequence]` | `Unit[SBRSequence]` |
| `Catering[CalendarDate]` | `DimDate[CalendarDate]` |

### Step 3 — Create measures
In the **Catering** table, create 3 measures:

```dax
1P Net Sales = SUM(Catering[FirstPartyNetSales])

3P Net Sales = SUM(Catering[ThirdPartyNetSales])

Total Catering Sales = [1P Net Sales] + [3P Net Sales]
```

### Step 4 — Build the main report page
1. **Rename Page 1** → `Catering by Brand`
2. Add a **Clustered Bar Chart** visual:
   - Y-axis: `Brand[BrandName]`
   - X-axis: `[Total Catering Sales]`
   - Sort descending by Total Catering Sales
3. Resize to take up the left 60% of the canvas
4. Format → title: **"Catering Revenue by Brand"**

### Step 5 — Build the Tooltip page
1. Click the **"+"** icon to add a new page → rename it `Tooltip_BrandDetail`
2. In the **Page settings** pane (click on blank canvas area):
   - Under **Page information** → toggle **"Allow use as tooltip"** = **ON**
   - Under **Canvas settings** → Page size → set to **Tooltip** (320 × 240 px)
3. On this tooltip page, add two visuals:

   **Visual A — Monthly Trend (Line chart):**
   - X-axis: `DimDate[MonthName]` (sort by Month number)
   - Values: `[1P Net Sales]`, `[3P Net Sales]`
   - Legend: on
   - Title: **"Monthly Catering Trend"**
   - Resize to fill top half of the tooltip canvas

   **Visual B — Top Units (Table):**
   - Columns: `Unit[SBRName]`, `[Total Catering Sales]`
   - Under Filters pane → add **Top N filter** on `[Total Catering Sales]`, show top **5**
   - Title: **"Top 5 Units"**
   - Resize to fill bottom half of the tooltip canvas

### Step 6 — Attach tooltip to the main bar chart
1. Go back to **Catering by Brand** page
2. Click the bar chart visual to select it
3. In **Format visual** pane → **General** tab → scroll to **Tooltips**
4. Set **Type** = **Report page**
5. Set **Page** = **Tooltip_BrandDetail**

### Step 7 — Test
1. Hover over any brand bar → the tooltip page appears showing the trend and top units filtered to that brand
2. **Screenshot this result** — this is your deliverable for the client

### What to document
- Time taken to author the tooltip page
- Did the cross-filter to the hovered brand work automatically? (Yes — Power BI passes the visual's filter context automatically)
- Any limitations: tooltip canvas is small (fixed 320×240), cannot scroll, cannot interact with tooltip visuals (hover-only)
- Capture the tooltip appearing in the screenshot

---

## Tableau — Viz in Tooltip

### Estimated time: 15–20 minutes

### Prerequisite
- Tableau Desktop 2020.1 or later (Viz in Tooltip available since 2017.1, but 2020+ is recommended)
- If Tableau Desktop is not installed, this section can be shown via screenshots/documentation alone

### Step 1 — Connect to data
1. Open **Tableau Desktop** → **Connect → To a File → More…**
2. Select `catering.parquet` — Tableau auto-loads it
3. In the **Data Source** tab, also drag in `brand.parquet`, `unit.parquet`, `dimdate.parquet`
4. In the logical layer, define relationships:
   - `Catering[BrandSequence]` = `Brand[BrandSequence]`
   - `Catering[SBRSequence]` = `Unit[SBRSequence]`
   - `Catering[CalendarDate]` = `DimDate[CalendarDate]`

### Step 2 — Create the Tooltip worksheet (the viz that will appear inside the tooltip)
1. Click **Sheet 2** tab → rename it `Tooltip_MonthlyTrend`
2. Drag `DimDate[MonthName]` → Columns shelf
3. Right-click MonthName on the shelf → Sort → By field → `DimDate[Month]` (ascending)
4. Create a calculated field: `1P Net Sales` = `SUM([First Party Net Sales])`
5. Create a calculated field: `3P Net Sales` = `SUM([Third Party Net Sales])`
6. Drag both measures → Rows shelf → this creates a dual-axis chart
7. Change mark type to **Bar** for a clean mini bar chart
8. Set title to **"Monthly Catering Trend — <Brand Name>"** (use the dynamic title with the Brand Name field inserted)

### Step 3 — Build the main bar chart
1. Click **Sheet 1** tab → rename it `Catering by Brand`
2. Drag `Brand[Brand Name]` → Rows shelf
3. Drag `SUM([First Party Net Sales])` + `SUM([Third Party Net Sales])` → Columns shelf (stacked bar)
4. Sort descending by total
5. Title: **"Catering Revenue by Brand"**

### Step 4 — Embed the tooltip viz (the key step)
1. Click on the **Catering by Brand** sheet
2. In the **Marks** card → click **Tooltip**
3. In the tooltip editor, click **Insert → Sheets → Tooltip_MonthlyTrend**
4. This inserts the tag: `<Sheet name="Tooltip_MonthlyTrend" maxwidth="300" maxheight="200" filter="yes">`
5. The `filter="yes"` attribute means Tableau automatically filters the tooltip viz to show only the hovered Brand's data
6. Add text above the viz tag: **"Catering trend for <Brand Name>:"** using the Insert → Field menu
7. Click **OK**

### Step 5 — Test
1. Hover over any brand bar → a fully rendered mini bar chart appears, filtered to that brand's monthly trend
2. **Screenshot this** — this is your strongest Tableau deliverable

### Step 6 — (Optional but impressive) Add a Top 5 Units sheet to the tooltip
1. Create **Sheet 3** → `Tooltip_TopUnits`
2. Drag `Unit[SBR Name]` → Rows, `SUM([First Party Net Sales])` → Columns
3. Sort descending → Analysis → Filters → Add filter → Top 5 by `SUM([First Party Net Sales])`
4. Go back to the Tooltip editor on **Catering by Brand** → insert this sheet too
5. Now the tooltip shows BOTH the trend chart AND the top units list simultaneously

---

## Side-by-Side Findings Summary

| Dimension | Power BI | Tableau |
|---|---|---|
| **Setup complexity** | Medium — must author a separate tooltip page, set page type, attach to visual | Low — embed any existing sheet with a single tag in the tooltip editor |
| **Visual richness** | Good — multi-visual tooltip page, but fixed 320×240 canvas | Excellent — full rendered Tableau viz, responsive to canvas size |
| **Dynamic filtering** | Automatic — passes the host visual's filter context | Automatic via `filter="yes"` attribute |
| **Interactivity inside tooltip** | None — hover only, cannot click or interact | Limited — cannot interact, but the viz renders fully |
| **Multiple vizzes in one tooltip** | Yes — add multiple visuals to the tooltip page | Yes — embed multiple sheets in the same tooltip editor |
| **Custom text + viz mix** | Limited — tooltip page is visual-only; separate "default tooltip" for text | Flexible — mix static text, dynamic field values, and embedded vizzes in one editor |
| **Winner** | | **Tableau** — Viz-in-Tooltip is native, faster to author, and visually richer |

### Key talking point for client call
> "Both tools support rich tooltips. But Tableau's Viz-in-Tooltip is a first-class feature — you embed any worksheet you've already built into a tooltip with one line. Power BI requires you to create a dedicated tooltip report page, configure it separately, and attach it. Same end result, but Tableau gets you there in about half the authoring time, and the tooltip renders at any size rather than a fixed 320×240 canvas."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (Power BI Findings) for S.No 16:**
> Report page tooltips: author a separate page, set page type = Tooltip, attach to host visual. Fixed canvas (320×240). Passes filter context automatically. Cannot interact with tooltip visuals. Authoring time ~20 min. No Premium required.

**Column G (Tableau Findings) for S.No 16:**
> Viz-in-Tooltip: embed any existing worksheet into a tooltip via a single tag in the tooltip text editor. Filter context passed automatically with `filter="yes"`. Supports multiple embedded sheets plus mixed text/field values. Renders at configurable size. Authoring time ~10 min once the source sheet exists. Clear advantage over Power BI for visual richness and authoring speed.

**Column J (Status) for S.No 16:** `COMPLETED`
