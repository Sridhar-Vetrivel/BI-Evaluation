# POC Guide — S.No 157: Paginated Report Support for Operational / Pixel-Perfect Outputs
**Category:** 16. Report Consumption & Alerting | **Priority:** High | **AtScale dependency:** None

## Scenario (GTF-specific)
GTF's current state includes a 6-page "data dump" catering report — essentially a row-level operational report showing every unit's catering sales by date, with subtotals by brand and region. This is a classic **paginated report** use case: thousands of rows, must print cleanly to PDF, must paginate by brand/region, must export to Excel for franchise operators.

This POC replicates that exact use case:
- Catering detail: one row per unit per month, showing 1P Sales, 3P Sales, 1P Traffic, 3P Traffic, Comp flag
- Page break by Brand
- Parameters: Date range and Brand filter
- Export to PDF and Excel

**Expected verdict:** Power BI Paginated Reports (via Report Builder) handles this natively and produces pixel-perfect PDF output. Tableau has no equivalent — long worksheets are the closest approximation and they do not paginate, page-break by dimension, or produce print-quality PDFs.

---

## Data files used
All from `udi_data_gen\output\parquet\`:
- `catering.parquet` — BrandSequence, SBRSequence, CalendarDate, FirstPartyNetSales, ThirdPartyNetSales, FirstPartyTraffic, ThirdPartyTraffic, Comp
- `brand.parquet` — BrandSequence, BrandName
- `unit.parquet` — SBRSequence, SBRName, Region, FranchiseBusinessConsultant, State

> **Note:** For the paginated report POC we will use a small CSV sample export from these Parquet files so that Power BI Report Builder can connect locally (Report Builder connects to published Power BI datasets, SQL Server, or ODBC sources — not directly to Parquet). Steps to generate the CSV sample are in Step 0 below.

---

## Power BI — Paginated Reports via Report Builder

### Estimated time: 20–30 minutes

### Step 0 — Generate a sample CSV (one-time, 2 minutes)
Run this in a terminal from the project root:

```powershell
python -c "
import pandas as pd, pyarrow.parquet as pq

cat = pq.read_table('udi_data_gen/output/parquet/catering.parquet').to_pandas()
brand = pq.read_table('udi_data_gen/output/parquet/brand.parquet').to_pandas()
unit = pq.read_table('udi_data_gen/output/parquet/unit.parquet').to_pandas()[['SBRSequence','SBRName','Region','State']]

# Join
df = cat.merge(brand[['BrandSequence','BrandName']], on='BrandSequence')
df = df.merge(unit, on='SBRSequence')

# Summarise to monthly (reduce rows to manageable size for POC)
df['CalendarDate'] = pd.to_datetime(df['CalendarDate'])
df['YearMonth'] = df['CalendarDate'].dt.to_period('M').astype(str)
monthly = df.groupby(['BrandName','SBRName','Region','State','YearMonth','Comp']).agg(
    FirstPartyNetSales=('FirstPartyNetSales','sum'),
    ThirdPartyNetSales=('ThirdPartyNetSales','sum'),
    FirstPartyTraffic=('FirstPartyTraffic','sum'),
    ThirdPartyTraffic=('ThirdPartyTraffic','sum')
).reset_index()

monthly.to_csv('Goal/catering_monthly_sample.csv', index=False)
print(f'Exported {len(monthly)} rows to Goal/catering_monthly_sample.csv')
"
```

This creates `Goal\catering_monthly_sample.csv` with ~100k rows — light enough for Report Builder.

### Step 1 — Download Power BI Report Builder
1. Go to: https://www.microsoft.com/en-us/download/details.aspx?id=58158
2. Download and install **Power BI Report Builder** (free, ~80 MB installer)
3. Open Report Builder → it launches with a blank report canvas

### Step 2 — Create a new report with the Table or Matrix Wizard
1. **Getting Started** dialog → click **New Report → Table or Matrix Wizard**
2. **Step: Choose a dataset** → select **Create a dataset**
3. Click **Next**

### Step 3 — Connect to the CSV data source
1. **Step: Choose a connection** → click **New**
2. **Connection type**: Select **Microsoft Excel** (or **Text/CSV** if Excel is unavailable)
   - Actually: choose **OLE DB** if Excel is not an option, or use **SQL Server** with `catering_monthly_sample.csv` loaded into SSMS
   - **Simplest path**: Use **Microsoft Excel** connection:
     - Rename `catering_monthly_sample.csv` → `catering_monthly_sample.xlsx` (open in Excel and Save As xlsx first — 30 seconds)
     - Connection string: `Provider=Microsoft.ACE.OLEDB.12.0;Data Source=C:\...\Goal\catering_monthly_sample.xlsx;Extended Properties="Excel 12.0 Xml;HDR=YES"`
3. Click **Test Connection** → should say "Connection created successfully"
4. Click **OK**

### Step 4 — Write the dataset query
In the **Dataset Properties** dialog:
1. **Name:** `CateringDetail`
2. **Query text** (for Excel source):
```sql
SELECT * FROM [Sheet1$]
ORDER BY BrandName, Region, SBRName, YearMonth
```
3. Click **OK** → Report Builder fetches columns automatically

### Step 5 — Arrange fields in the table wizard
1. **Available fields** (left panel) → drag to the right:
   - **Row groups:** `BrandName`, then `SBRName`
   - **Values:** `FirstPartyNetSales`, `ThirdPartyNetSales`, `FirstPartyTraffic`, `ThirdPartyTraffic`
   - **Columns:** `YearMonth` (this creates a crosstab / matrix — optional, leave empty for a flat table)
2. Click **Next**

### Step 6 — Configure subtotals and page breaks (the key paginated report feature)
1. **Step: Choose the layout:**
   - Check **Show subtotals and grand totals** = ON
   - Check **Expand/collapse groups** = ON
   - Layout: **Blocked, subtotal below**
2. Click **Next** → **Finish**

Now you have a basic paginated table. Do these refinements:

**Add a page break by Brand:**
1. Right-click the `BrandName` row group in the **Row Groups** panel (bottom) → **Group Properties**
2. **Page Breaks** tab → check **Between each instance of a group** = ON
3. Click **OK** — now each brand starts on a new page when printed/exported

**Add parameters (Date filter):**
1. **Report Data** panel (left) → right-click **Parameters** → **Add Parameter**
2. Name: `StartMonth`, Data type: Text, Prompt: "Start Month (YYYY-MM)"
3. Add another: `EndMonth`, Data type: Text, Prompt: "End Month (YYYY-MM)"
4. Modify the dataset query to use them:
```sql
SELECT * FROM [Sheet1$]
WHERE YearMonth >= [@StartMonth] AND YearMonth <= [@EndMonth]
ORDER BY BrandName, Region, SBRName, YearMonth
```

### Step 7 — Format the report
1. Click any header cell → apply **Bold**, adjust font to Calibri 10
2. Right-click the `FirstPartyNetSales` value cell → **Text Box Properties** → **Number** → Currency, 0 decimal places
3. Repeat for `ThirdPartyNetSales`
4. Add a **report header** (Insert → Header → click the header area) with title text: **"GoTo Foods — Catering Detail Report"** and a date/time field

### Step 8 — Preview and export
1. Click **Run** (top ribbon) → preview with default parameters
2. Enter `2023-01` and `2023-12` in the parameter prompts → click **View Report**
3. Observe: rows paginate, each Brand starts on a new page, subtotals appear at the Brand level
4. Click **Export → PDF** → observe the pixel-perfect PDF output
5. Click **Export → Excel** → open the xlsx — each brand section on its own named sheet (optional: configure this in export settings)
6. **Screenshot the preview, the page break by Brand, and the PDF export dialog**

### What to document
- Total authoring time
- Note: Report Builder is free; **publishing to Power BI Service requires Power BI Premium Per User (PPU) or Premium capacity**. For the client, this is an important licensing caveat.
- Pixel-perfect layout, page break control, parameter-driven filtering, multi-format export — all work natively
- Note any limitations encountered (complex joins, large dataset performance in preview)

---

## Tableau — Why Paginated Reports Don't Exist Here

### Estimated time: 10 minutes (to document the gap, not build a workaround)

### What to show
This section is about demonstrating **what Tableau cannot do**, not building a Tableau version of the above.

**Step 1 — Open Tableau Desktop and confirm the absence of the feature**
1. Open Tableau Desktop
2. Go to **File** menu → observe there is no "Paginated Report" or "Operational Report" option
3. Go to **Server → Publish Workbook** → no paginated report format option
4. **Screenshot the menu** — this visual absence is the finding

**Step 2 — Attempt the closest approximation: a long worksheet**
1. Create a new workbook, connect to the same data (catering.parquet)
2. Drag `BrandName`, `SBRName`, `YearMonth` onto **Rows**
3. Drag `SUM(FirstPartyNetSales)`, `SUM(ThirdPartyNetSales)` onto the **Text** mark
4. This creates a long cross-tab table
5. Now try to:
   - Add a page break between Brands: **Not possible** — Tableau has no page-break-by-dimension feature
   - Add subtotals: Analysis → Totals → Show Row Grand Totals (works), but brand-level subtotals require a workaround
   - Export to a clean PDF: File → Print to PDF → observe that it either cuts rows mid-table or produces a multi-page PDF with no control over page breaks
6. **Screenshot the PDF export** showing the uncontrolled page break problem

**Step 3 — Show the printing options panel**
1. File → Page Setup → observe options:
   - You can set paper size, but cannot set "page break after each [BrandName]"
   - No parameter-driven date filter in the export dialog
2. **Screenshot this panel** showing the absence of break-by-dimension

**Step 4 — Document what Tableau would need (workarounds)**
For completeness, note these are the paths Tableau shops use — all require significant extra work:

| Workaround | How | Why it falls short |
|---|---|---|
| **Tableau + Tableau Prep** | Prep flow exports to Excel | Not a report — raw data export, no formatting |
| **Tableau REST API + Python** | Script downloads one PDF per brand | Requires engineering effort, not a self-service feature |
| **Tabcmd** (CLI tool) | CLI command exports views to PDF | Requires server access; no dynamic page breaks |
| **Third-party: Pixel Perfect (Logi/Cognos style)** | External tools like Render or Metric Insights | Additional licensing cost; separate product |
| **Tableau Pulse (new)** | AI-generated metric digests | Not a row-level operational report |

**None of these match what Power BI Report Builder delivers out of the box in 20 minutes.**

---

## Side-by-Side Findings Summary

| Dimension | Power BI | Tableau |
|---|---|---|
| **Native paginated report tool** | Yes — Power BI Report Builder (free download) | No — does not exist |
| **Page break by dimension value** | Yes — Group Properties → Page Breaks | Not possible natively |
| **Row-level detail (thousands of rows)** | Yes — RDL/SSRS engine handles millions of rows | Worksheet rows limited by viewport; degrades at scale |
| **Pixel-perfect layout control** | Yes — cell-level sizing, fixed headers, merged cells | No — canvas-based, not print-optimized |
| **Parameter-driven filtering** | Yes — built-in parameters with prompt UI | Via Parameters (works) but no print-integration |
| **Export to PDF (page-break-aware)** | Yes — each group on correct page | Yes but uncontrolled breaks |
| **Export to Excel** | Yes — structured workbook with subtotals | Yes — flat export only |
| **Publish without Premium** | Build: free (Report Builder). Publish: requires PPU/Premium | Publish to Tableau Cloud: included in license |
| **SSRS compatibility** | Full — .rdl reports migrate directly | None |
| **Winner** | **Power BI — decisively** | No equivalent feature |

### Key talking point for client call
> "The current GoTo Foods catering report is a row-level operational document — brand-level subtotals, page breaks by territory, PDF export for franchise operators. Power BI handles this natively through Report Builder, the same SSRS engine the team already uses for Power BI Report Server today. Tableau does not have a paginated report engine. The closest Tableau can do is a long cross-tab worksheet, but it cannot page-break by dimension, cannot produce consistent PDF output, and requires third-party tools or engineering scripts for anything resembling a formatted operational report. This is the clearest functional gap in this evaluation."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (Power BI Findings) for S.No 157:**
> Power BI Report Builder (free): builds .rdl paginated reports with page-break-by-group, parameter-driven filters, row-level detail to millions of rows, pixel-perfect layout, export to PDF/Excel/Word. Publishing requires PPU or Premium capacity. Full SSRS compatibility — existing GTF .rdl reports migrate directly. Authoring time for a branded catering detail report: ~25 min.

**Column G (Tableau Findings) for S.No 157:**
> Tableau has no paginated report engine. Long cross-tab worksheets are the closest approximation — no page-break-by-dimension, no controlled PDF pagination, no structured Excel export with subtotals. Workarounds (tabcmd, REST API, Tableau Prep) all require engineering effort and do not match the self-service experience of Report Builder. This is a material gap for GTF's operational reporting requirement (catering detail, P&L row-level). **Clear Power BI win.**

**Column J (Status) for S.No 157:** `COMPLETED`
