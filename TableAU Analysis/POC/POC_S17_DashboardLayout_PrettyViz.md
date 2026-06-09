# POC Guide — S.No 17: Dashboard Layout Flexibility (Pretty Visualization)
**Category:** 2. Visualization & UX | **Priority:** High | **AtScale dependency:** None
**Client requirement:** 6c — Report with pretty visualization

---

## Why Tableau wins here
This is the one area in the 8 client requirements where **Tableau is the clear winner**.

Every other requirement — Azure AD, Gateways, Apps, RLS, Bookmarks, P&L, Large rows, Robots — favors Power BI. But for visual design quality and layout freedom, Tableau's floating container model gives designers pixel-perfect control that Power BI's snap-to-grid canvas cannot match.

**The core difference:**
- **Power BI:** fixed canvas, snap-to-grid, visuals cannot overlap, mobile layout requires completely separate authoring
- **Tableau:** two layout modes (Tiled + Floating), visuals can overlap, pixel-exact positioning, Device Designer builds desktop/tablet/phone in one workbook

---

## Scenario (GTF-specific)
Build a **GoTo Foods Brand Executive Catering Scorecard** — the kind of dashboard a Brand Leader or RVP would open on an iPad before a quarterly review:

- Branded header bar (GoTo Foods color + title text)
- 3 KPI cards in a row: Net Sales, YoY%, Total Active Units
- Unit location map (plot by Latitude/Longitude)
- Bar chart: Top 10 Brands by Catering Revenue
- Monthly trend line chart
- A visual overlay: KPI text floating over a colored background zone

Build the same layout in both tools. The difference in visual precision and design freedom is immediately visible.

---

## Data files used
From `udi_data_gen\output\parquet\`:
- `reported_sales.parquet` — NetSalesCY, NetSalesPY, BrandSequence, SBRSequence, CalendarDate
- `brand.parquet` — BrandName, Concept
- `unit.parquet` — SBRName, Latitude, Longitude, Region, State, SBRStatus
- `brand_targets.parquet` — for Target vs Actual KPI
- `dimdate.parquet` — Year, Month, MonthName

---

## Time estimate

| Section | Time |
|---|---|
| Tableau — floating layout, branded header, map, overlay | 25–30 min |
| Power BI — grid layout, same 5 visuals, mobile layout attempt | 20–25 min |
| Side-by-side screenshots | 5–10 min |
| **Total** | **50–65 min** |

---

## Tableau — Pixel-Perfect Floating Dashboard

### Step 1 — Connect to data
1. Open **Tableau Desktop** → Connect → `reported_sales.parquet`
2. In Data Source tab, drag in: `brand.parquet`, `unit.parquet`, `dimdate.parquet`
3. Set relationships:
   - `Reported Sales[BrandSequence]` = `Brand[BrandSequence]`
   - `Reported Sales[SBRSequence]` = `Unit[SBRSequence]`
   - `Reported Sales[CalendarDate]` = `DimDate[CalendarDate]`
4. Click **Sheet 1**

### Step 2 — Create calculated fields
```
Total Net Sales = SUM([Net Sales CY])
Prior Year Sales = SUM([Net Sales PY])
YoY % = (SUM([Net Sales CY]) - SUM([Net Sales PY])) / SUM([Net Sales PY])
Active Units = COUNTD([SBR Sequence])
```

### Step 3 — Build the 4 worksheets

**Sheet 1 — KPI: Net Sales**
- Drop `Total Net Sales` on **Text** mark
- Format: Currency, large bold font (28–32pt), center align
- Title: "Net Sales"
- Remove all gridlines, borders, zero lines (Format → Borders → None)
- Sheet background: white, no row/column dividers

**Sheet 2 — Bar: Top Brands**
- Drag `Brand Name` → Rows, `Total Net Sales` → Columns
- Sort descending → Analysis → Filter → Top 10 by `Total Net Sales`
- Remove the axis labels, keep only bar values
- Apply a single brand color (e.g., deep red `#B31B1B`) to all bars
- Remove gridlines, remove axis title
- Title: "Catering Revenue — Top Brands"

**Sheet 3 — Line: Monthly Trend**
- Drag `Month Name` → Columns (sort by Month number)
- Drag `Total Net Sales`, `Prior Year Sales` → Rows → Dual axis → Synchronize
- Mark type: Line for both, CY = solid, PY = dashed gray
- Remove axis, remove gridlines
- Title: "Monthly Sales — CY vs PY"

**Sheet 4 — Map: Unit Locations**
- Double-click `Latitude` (from Unit) → Tableau auto-generates a map
- Drag `Longitude` to the view if not auto-added
- Drag `Total Net Sales` → **Size** mark (bubble size = sales volume)
- Drag `Region` → **Color** (regional color coding)
- Title: "Unit Locations by Region"

### Step 4 — Build the Dashboard with FLOATING layout

1. Click **New Dashboard** → rename `Brand Executive Scorecard`
2. In **Dashboard** pane (left): set **Size** → Fixed (1200 × 800 px)
3. Set Layout to **Floating** (bottom of the left panel — toggle from Tiled to Floating)

**Add the branded header (this is only possible cleanly in Tableau):**
4. From the left panel → drag a **Blank** object onto the canvas → position it at the very top spanning the full width: X=0, Y=0, W=1200, H=60
5. Right-click the blank object → **Format** → Background Color → set to a dark brand color (e.g., `#1F3A5F`)
6. Drag a **Text** object → float it over the header → type: **"GoTo Foods | Catering Performance Dashboard"** → font: white, 18pt bold
7. Position it: X=20, Y=15, W=600, H=35

**Add KPI cards row:**
8. Float **Sheet 1 (KPI: Net Sales)** → X=0, Y=70, W=300, H=120
9. Create 2 more KPI sheets (YoY% and Active Units) similarly → float them at X=300,Y=70 and X=600,Y=70 each W=300, H=120
10. Float a **Blank** container behind the 3 KPIs → X=0, Y=70, W=900, H=120 → light gray background `#F5F5F5` — the KPI row sits on a colored band

**Add the main visuals:**
11. Float **Bar chart (Top Brands)** → X=0, Y=200, W=600, H=350
12. Float **Line chart (Monthly Trend)** → X=0, Y=560, W=900, H=230
13. Float **Map (Unit Locations)** → X=620, Y=200, W=580, H=590

**Add a visual overlay (the Tableau signature move):**
14. Float a **Text** object over the map → X=630, Y=210, W=200, H=50 → type: "4,000 Active Units" → large font, white, semi-transparent background
15. This text floats ON TOP of the map visual — **this is not possible without workarounds in Power BI**

### Step 5 — Set precise positions using the Layout panel
1. Click any floating object → in the **Layout** tab (left panel) → you see exact X, Y, W, H fields
2. Type precise pixel values: e.g., set the map to exactly X=622, Y=198 to align with the bar chart right edge
3. **Screenshot this panel** showing the pixel-precise positioning — this is the key demo point

### Step 6 — Device Designer (one workbook, three layouts)
1. **Dashboard** menu → **Device Layouts → Add Phone**
2. Tableau opens a phone-sized canvas — drag only the KPI cards and bar chart here (map is too dense for phone)
3. **Dashboard** menu → **Device Layouts → Add Tablet** → arrange 2×2 grid
4. All 3 device layouts live in ONE workbook — no duplication
5. **Screenshot all 3 layouts side by side**

### What to document
- Total authoring time
- Visual: does the dashboard look polished and professionally designed?
- Can you position elements with pixel precision? (Yes — Layout panel)
- Can you overlap visuals? (Yes — floating text over map)
- Can you create a branded color header band? (Yes — blank container with background color)
- Device layouts: single workbook covers all 3 devices

---

## Power BI — Grid-Based Layout

### Step 1 — Load data
1. Open **Power BI Desktop** → Get Data → Parquet
2. Load: `reported_sales.parquet` → ReportedSales, `brand.parquet` → Brand, `unit.parquet` → Unit, `dimdate.parquet` → DimDate
3. Set relationships: ReportedSales ↔ Brand, ReportedSales ↔ Unit, ReportedSales ↔ DimDate
4. Create the same 3 measures: `Total Net Sales`, `Prior Year Sales`, `YoY %`, `Active Units`

### Step 2 — Build the 4 visuals
1. **KPI Card** → field: `Total Net Sales` — format as currency, large font
2. **Clustered Bar Chart** → Y: `Brand[BrandName]` (Top N filter = 10), X: `[Total Net Sales]`
3. **Line Chart** → X: `DimDate[MonthName]`, Y: `[Total Net Sales]` + `[Prior Year Sales]`
4. **Map** → Location: `Unit[Latitude]` + `Unit[Longitude]`, size: `[Total Net Sales]`, color: `Unit[Region]`

### Step 3 — Arrange the layout (observe the grid constraint)

**Header bar attempt:**
1. Insert → **Text Box** → type the dashboard title → drag to the top of the canvas
2. Observe: the text box snaps to the grid. You cannot place it at exactly pixel 0,0 without it jumping to the nearest grid position.
3. To create a colored header band: **Insert → Shapes → Rectangle** → drag across the top
4. Observe: the shape also snaps to grid. Getting a perfectly full-width colored header requires manual dragging and guessing — **no pixel-coordinate input field**.

**Arranging the 4 visuals:**
5. Drag the KPI card, bar chart, line chart, and map onto the canvas
6. Try to align the bar chart's right edge with the map's left edge
7. Observe: Power BI provides **alignment guides** (blue snap lines) but not exact pixel coordinate entry in the basic format pane
8. To get exact positioning: select the visual → **Format visual → General → Properties** → X, Y, Width, Height in cm (not pixels) — achievable but less intuitive than Tableau's Layout panel

**Attempting to overlap a visual over another:**
9. Try to place a text card floating over the map (like the "4,000 Active Units" overlay in Tableau)
10. Observe: Power BI renders visuals in Z-order but the layering is not intuitive; bringing a visual to the front requires right-click → **Bring to front**. Achievable but fiddly.

### Step 4 — Test the mobile layout limitation
1. **View** menu → **Mobile layout**
2. You are now in a SEPARATE phone canvas — this is a completely different view from the desktop canvas
3. Drag the KPI card, bar chart, and line chart from the right-side panel into the phone canvas
4. Notice: any layout changes here do NOT affect the desktop view — they are entirely independent
5. **Screenshot both the desktop and mobile canvases** — two separate layouts that must be maintained independently
6. **This is the key Power BI limitation:** any time you update the desktop layout, the mobile layout needs a separate update

### Step 5 — Compare the final result
- **Screenshot** the Power BI dashboard on the same scale as the Tableau dashboard
- Compare:
  - Header band precision
  - KPI card alignment
  - Visual overlap capability
  - Overall visual polish

---

## Side-by-Side Findings Summary

| Dimension | Power BI | Tableau |
|---|---|---|
| **Layout model** | Snap-to-grid only | Tiled (snap) + Floating (pixel-free) |
| **Pixel-exact positioning** | cm-based via Format pane; no pixel grid lines | Pixel-exact X/Y/W/H in the Layout panel |
| **Visual overlapping** | Possible via Z-order but fiddly | Natural with floating objects |
| **Branded color header** | Via shapes/rectangles, snaps to grid | Blank container with background fill, pixel-perfect |
| **Text floating over a visual** | Workaround (bring to front, Z-order) | Native floating text object |
| **Device layouts** | Separate mobile layout view; desktop and mobile maintained independently | Device Designer: desktop/tablet/phone in one workbook |
| **Authoring effort for polished layout** | More adjustment attempts needed | Fewer — precise inputs available |
| **Visual polish outcome** | Good | Better — more design freedom produces cleaner results |
| **Winner** | | **Tableau** — clearly better for executive/pixel-perfect dashboards |

---

## Key talking point for client call

> "Both tools can build dashboards. The difference shows up when you're designing an executive-facing scorecard that needs to look polished and branded. Tableau's floating layout means you position every element with exact pixel coordinates — no snapping, no guessing. You can layer a text overlay on top of a map, create branded color header bands with a single container, and author desktop, tablet, and phone layouts in one workbook. Power BI's grid is fine for operational reports, but for the kind of visually precise executive dashboards that GTF's Brand Leaders and RVPs use on iPads, Tableau produces a noticeably better-looking result with less rework."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (Power BI Findings) for S.No 17:**
> Grid-based canvas with snap-to-grid. Pixel positioning available via Format > Properties (cm units) but no live pixel grid. Visual overlapping possible via Z-order but not intuitive. Mobile layout requires a fully separate canvas — any desktop change must be manually replicated for mobile. Branded header achievable via shapes. Overall: good for operational reports, constrained for pixel-perfect executive dashboards.

**Column G (Tableau Findings) for S.No 17:**
> Two layout modes: Tiled (snap) and Floating (pixel-free). Layout panel provides exact X/Y/W/H in pixels for every object. Floating text and blank containers with background color enable branded headers and visual overlays natively. Device Designer (desktop/tablet/phone) lives in one workbook — no duplication. Authoring effort for polished executive dashboard is noticeably lower than Power BI. Clear winner for visual design quality and layout precision.

**Column J (Status) for S.No 17:** `COMPLETED`
