# POC Guide — S.No 134: Export Formats Supported (PDF, Excel, CSV, PNG, PowerPoint)
**Category:** 14. Interoperability & Standards | **Priority:** High | **AtScale dependency:** None

> **No prerequisites needed for the core proof.** Every one of the five formats can be produced **locally and free** using **Power BI Desktop** (free download) and **Tableau Desktop** (14-day trial) or **Tableau Public** (free) — Section A in each tool below. Only the *programmatic* export (REST `ExportTo` / `populate_pdf`) needs a published workspace/site, and that is **optional** (use a free Tableau Developer site / Power BI trial — see the S.No 101 POC, Tier 2). No AtScale needed.

---

## Scenario (GTF-specific)
Different GTF consumers need different formats from the *same* content:
- **Franchise operators** → **PDF** of the catering detail (emailed, print-friendly)
- **Analysts** → **CSV / Excel** to pull the underlying numbers for their own work
- **Executives** → **PowerPoint (PPTX)** for board/leadership decks
- **Intranet / apps** → **PNG** images of a dashboard for embedding

This POC proves each tool can produce all five formats — both **interactively** (what a self-service user clicks) and **programmatically** (what the "robots"/automation produce).

**Expected verdict:** Both tools cover PDF, Excel, CSV, PNG, and PowerPoint for the common cases. Power BI splits behavior across **interactive reports** (PDF/PPTX/PNG) and **paginated reports** (adds XLSX/DOCX/CSV/XML/MHTML with pixel-perfect fidelity), and exposes it all via the **ExportTo** REST API. Tableau exports **PDF/PNG/PPTX** of views and **crosstab→Excel / data→CSV**, via UI and REST view endpoints. Likely a **Tie** for the five named formats, with Power BI ahead on **structured/operational Excel + breadth** (paginated engine) and Tableau ahead on **clean PPTX-per-dashboard** ergonomics.

---

## Data files used
From `udi_data_gen\output\parquet\`: `reported_sales.parquet`, `brand.parquet`, `unit.parquet`, `dimdate.parquet`. (Or reuse an existing dashboard from a prior POC.)

---

## Time estimate

| Section | Time |
|---|---|
| Power BI — interactive exports (PDF/PPTX/PNG/Excel/CSV) | 20 min |
| Power BI — ExportTo REST (per-format, async) | 20 min |
| Tableau — interactive exports (PDF/PNG/PPTX/Excel/CSV) | 20 min |
| Tableau — REST view export (PDF/PNG/CSV) | 15 min |
| Screenshots + findings | 15 min |
| **Total** | **~90 min** |

---

## Power BI — Export formats

### A. Interactive report exports (Power BI Service / Desktop)
1. Open a report (build on parquet or use a GTF test copy).
2. **Export to PDF:** Service → **Export → PDF** (or Desktop → File → Export → PDF). Whole report → multi-page PDF.
3. **Export to PowerPoint:** Service → **Export → PowerPoint** → choose "Embed live data" or "Image". Each report page → a slide.
4. **Export to PNG:** Service → **Export → PowerPoint → Image** (per-page images), or a single visual → **... → Export data → underlying/summarized**; for a true image, use the ExportTo REST `PNG` (below) or screenshot a pinned visual.
5. **Export visual data to Excel / CSV:** on any visual → **... (More options) → Export data** → choose **.xlsx** (summarized or underlying) or **.csv**.
6. **Screenshots:** the Export menu (PDF/PPTX), and the per-visual Export data dialog (Excel/CSV).

#### Actual findings from testing (Power BI Desktop)

| Format | Desktop | Service (browser) | Notes |
|---|---|---|---|
| **PDF** | ✅ File → Export → Export to PDF | ✅ Yes | Works in both — confirmed |
| **PowerPoint** | ❌ Not available | ✅ Service only | Must publish first (Home → Publish), then open in app.powerbi.com → File → Export → PowerPoint |
| **PNG** | ❌ Not found | ❌ Not found in Service either | Available only via REST API (`ExportTo` with `PNG` format) or manual screenshot (Windows + Shift + S) |
| **Excel / CSV** | ❌ Not found via File menu | ✅ Service only | Must publish first; in Service use visual **"..." → Export data → .xlsx / .csv** |

> **Desktop Export menu shows only two options:** Power BI template and Export to PDF. All other formats require publishing to Power BI Service.

### B. Paginated reports — the pixel-perfect, structured exports
From Report Builder / Service, a paginated (RDL) report exports to **PDF, XLSX, DOCX, CSV, XML, MHTML, and image** with full layout control and brand-level page breaks (see S.No 157 POC). This is where **structured Excel with subtotals** and **operational CSV** come from.

### C. Programmatic export — REST API workaround
For formats not available interactively (e.g. PNG in Power BI), the **ExportTo REST API** provides a programmatic workaround. Power BI reports support `PDF`, `PPTX`, and `PNG` via REST; paginated reports additionally support `XLSX`, `DOCX`, `CSV`, `XML`, `MHTML`, and Accessible PDF. This is also the recommended path for automated, per-franchise delivery — but requires a published workspace (Power BI Service).

---

## Tableau — Export formats

### A. Interactive exports (Tableau Desktop / Cloud / Server)
1. Build a worksheet + a dashboard on the parquet data.
2. **PDF:** Desktop → **File → Print to PDF** (choose sheets/dashboard); Cloud/Server → **Download → PDF** (orientation, paper size, scaling).
3. **PowerPoint (PPTX):** Desktop → **File → Export As PowerPoint**; Cloud/Server → **Download → PowerPoint**. Each dashboard/sheet → a slide.
4. **PNG image:** Desktop → **Worksheet → Export → Image** (or **Dashboard → Export Image**); Cloud/Server → **Download → Image**.
5. **Excel (crosstab):** Desktop → **Worksheet → Export → Crosstab to Excel** (opens Excel with a crosstab). Cloud/Server → **Download → Crosstab**.
6. **CSV (data):** Cloud/Server → **Download → Data → Full Data → Download (.csv)**; Desktop → select marks → **View Data → Export to CSV**.
7. **Screenshots:** the Download menu (Cloud/Server) showing Image/PDF/PowerPoint/Crosstab/Data, and the Desktop Export submenu.

#### Actual findings from testing (Tableau Desktop)

| Format | Desktop | Cloud/Server | Notes |
|---|---|---|---|
| **PDF** | ✅ File → Print to PDF | ✅ Download → PDF | Available in both — confirmed |
| **PowerPoint** | ✅ File → Export As PowerPoint | ✅ Download → PowerPoint | Available in both — confirmed |
| **PNG** | ✅ Worksheet → Export → Image (worksheet) or Dashboard → Export Image (dashboard) | ✅ Download → Image | Not under File menu — use Worksheet or Dashboard menu |
| **Excel** | ✅ Worksheet → Export → Crosstab to Excel | ✅ Download → Crosstab | Crosstab format (aggregated grid), not structured XLSX |
| **CSV** | ✅ Worksheet → View Data → Export All | ✅ Download → Data → CSV | Not under File menu — use Worksheet → View Data |

> **All five formats available in Tableau Desktop.** PNG and CSV/Excel are not under `File` — they are under the `Worksheet` or `Dashboard` menus.

### B. Programmatic export — REST API workaround
All five formats can also be exported programmatically via Tableau's REST view endpoints (`populate_pdf`, `populate_image`, `populate_csv`). This requires a published view on Tableau Cloud/Server and is a workaround for automated/scheduled delivery — not needed for interactive self-service since all formats are accessible in Desktop.

### What to document
- Each of the five named formats produced in both tools — yes/no, interactive vs programmatic.
- Excel nuance: Tableau exports a **crosstab** (presentation grid), not a multi-section structured workbook; Power BI paginated reports produce **structured XLSX with subtotals**.
- PPTX nuance: Tableau gives a clean **dashboard-per-slide**; Power BI gives **page-per-slide** (live or image).

---

## Side-by-Side Findings Summary

| Format | Power BI | Tableau |
|---|---|---|
| **PDF** | ✅ Desktop (File → Export → PDF) + ✅ Service | ✅ Desktop (File → Print to PDF) + ✅ Cloud/Server |
| **PowerPoint** | ❌ Desktop — ✅ Service only (publish first) | ✅ Desktop (File → Export As PowerPoint) + ✅ Cloud/Server |
| **PNG** | ❌ Desktop — ❌ Service (not interactive) — REST API workaround only | ✅ Desktop (Worksheet → Export → Image / Dashboard → Export Image) + ✅ Cloud/Server |
| **Excel (.xlsx)** | ❌ Desktop — ✅ Service only (visual → "..." → Export data); **paginated → structured XLSX w/ subtotals** | ✅ Desktop (Worksheet → Export → Crosstab to Excel) — crosstab grid format |
| **CSV** | ❌ Desktop — ✅ Service only (visual → "..." → Export data); paginated supports CSV | ✅ Desktop (Worksheet → View Data → Export All) + ✅ Cloud/Server |
| **Desktop self-service (all 5)** | ❌ Only PDF available natively in Desktop — others need publishing to Service | ✅ All 5 formats available in Desktop without publishing |
| **Extra formats** | Paginated adds DOCX, XML, MHTML, Accessible PDF | (none of these) |
| **REST API workaround** | ExportTo API — PDF, PPTX, PNG (report); XLSX, CSV, DOCX, XML, MHTML (paginated) | REST view endpoints — PDF, PNG, CSV |
| **Structured/operational Excel** | **Strong** (paginated engine — XLSX with subtotals) | Crosstab only (presentation grid) |
| **Winner** | **Tie when Service included**; Power BI ahead on structured Excel + format breadth; Desktop limited to PDF only | **Ahead on Desktop self-service** — all 5 formats without publishing; clean dashboard-per-slide PPTX |

---

## Key talking point for client call
> "Both tools cover the five formats GTF cares about — PDF, Excel, CSV, PNG, and PowerPoint. The key practical difference is **where** those formats are available. **Tableau Desktop** exposes all five natively without needing to publish anywhere — analysts can export PDF, PowerPoint, PNG, Excel, and CSV directly from the desktop app. **Power BI Desktop** only exports PDF natively; PowerPoint, Excel, and CSV require publishing to Power BI Service first, and PNG requires the REST API. That said, once published, Power BI's paginated engine produces **structured Excel with subtotals** and a wider set of formats (Word, XML, MHTML, Accessible PDF), all via one async **ExportTo** REST API — ideal for automated per-franchise delivery. Tableau's REST API covers PDF, PNG, and CSV programmatically. For GTF self-service users on Desktop, **Tableau is simpler**; for automated operational delivery and structured Excel, **Power BI has the edge**."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (Power BI) for S.No 134:**
> Desktop supports only **PDF** natively (File → Export → PDF). PowerPoint and Excel/CSV require publishing to Service first. PNG is not available interactively in Desktop or Service — REST API workaround only. All formats available programmatically via the async **ExportTo** REST API.

**Column G (Tableau) for S.No 134:**
> All five formats available in **Tableau Desktop** without publishing: PDF (File → Print to PDF), PowerPoint (File → Export As PowerPoint), PNG (Worksheet → Export → Image or Dashboard → Export Image), Excel/crosstab (Worksheet → Export → Crosstab to Excel), and CSV (Worksheet → View Data → Export All). Same formats available in Cloud/Server via the Download menu. Note: Excel export is a **crosstab grid** (aggregated presentation format), not a multi-section structured workbook. REST API provides PDF, PNG, and CSV programmatically as a workaround for automation.

**Column H (Power BI Proof) for S.No 134:**
> Official documentation:
> https://learn.microsoft.com/en-us/rest/api/power-bi/reports/export-to-file-in-group
> https://learn.microsoft.com/en-us/power-bi/developer/embedded/export-to
> https://learn.microsoft.com/en-us/power-bi/developer/embedded/export-paginated-report

**Column I (Tableau Proof) for S.No 134:**
> Official documentation:
> https://help.tableau.com/current/pro/desktop/en-us/save_export_data.htm
> https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_workbooks_and_views.htm
> https://tableau.github.io/server-client-python/

**Column J (Findings) for S.No 134:**
> Both tools support all five formats. Key difference: **Tableau Desktop** covers all 5 natively without publishing; **Power BI Desktop** only covers PDF natively — PowerPoint and Excel/CSV require Service, PNG requires REST API. When Service is included, it's a tie. Power BI ahead on structured Excel (paginated XLSX with subtotals) and format breadth; Tableau ahead on Desktop self-service simplicity. Neither blocks GTF. Verdict: TABLEAU for Desktop self-service; POWER BI for structured Excel + operational delivery via ExportTo API.

**Column K (Status) for S.No 134:** `COMPLETED`
