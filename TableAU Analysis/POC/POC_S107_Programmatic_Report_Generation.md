# POC Guide — S.No 107: Programmatic Report Generation (Templating, Parameterized Reports)
**Category:** 11. Extensibility & Developer Ecosystem | **Priority:** High | **AtScale dependency:** None

> **Most of this is provable locally and free — no account needed.** The headline proofs run entirely on the desktop: Power BI **`.pbit` template + parameter prompt** works in free **Power BI Desktop** (Path 1), and Tableau **Document API** templating runs on local `.twb` files (`pip install tableaudocumentapi`, Path 1). Only the *deployment/replication* paths — REST Clone+Rebind, paginated `ExportTo`, TSC publish — need a published workspace/site, and those are **optional** (use a free Tableau Developer site / Power BI trial — see the S.No 101 POC, Tier 2). No AtScale needed.

---

## Scenario (GTF-specific)
GTF delivers the **same report, parameterized per brand or per franchise** — a Brand Summary / catering scorecard that looks identical but is scoped to one brand's data. Doing this by hand for every brand (and re-doing it when the design changes) doesn't scale. The question: **can one template generate N branded report instances programmatically?**

Two flavors to prove:
1. **Templating** — one design → many outputs (one per brand), built/deployed by script.
2. **Parameterized reports** — a single report whose content is driven by input parameters at open/render time (e.g., `BrandName = "Carvel"`).

**Expected verdict:** Power BI has **three distinct, mature paths** — `.pbit` templates (parameter prompt on open), REST **Clone + Rebind** (replicate a report against a different dataset per brand), and **paginated RDL** with parameters rendered to per-brand PDFs via `ExportTo`. Tableau relies on the community **Document API** (XML-level `.twb` edit) + **TSC publish**, plus **URL/workbook parameters** for runtime parameterization — capable but more DIY and partly unsupported. Likely **Power BI advantage**, especially for paginated/parameterized operational output.

---

## Data files used
From `udi_data_gen\output\parquet\`:
- `reported_sales.parquet`, `brand.parquet`, `unit.parquet`, `dimdate.parquet`
- (Reuse `Goal\catering_monthly_sample.csv` from the S.No 157 POC if you want a flat source for paginated/RDL.)

---

## Time estimate

| Section | Time |
|---|---|
| Power BI — .pbit template + parameter prompt | 15 min |
| Power BI — REST Clone + Rebind per brand (script) | 20 min |
| Power BI — paginated RDL parameter → per-brand PDF via ExportTo | 20 min |
| Tableau — Document API templating + TSC publish | 25 min |
| Tableau — URL/workbook parameter demo | 10 min |
| Screenshots + findings | 15 min |
| **Total** | **~105 min** |

---

## Power BI — Three paths to programmatic generation

### Path 1 — `.pbit` template with a parameter (design once, prompt per use)
1. Build a report in **Power BI Desktop** on the parquet data (e.g., a Brand Summary page).
2. **Home → Transform data → Manage Parameters → New Parameter:** name `BrandName`, Text, default `Carvel`. Use it to filter the `Brand` query (`= Table.SelectRows(Brand, each [BrandName] = BrandName)`).
3. **File → Export → Power BI template** → save `BrandSummary.pbit`.
4. **Test the template:** double-click `BrandSummary.pbit` → the **Enter Parameters** dialog appears → type `Moe's` → a fully populated report is generated for that brand.
5. **Screenshot:** the parameter prompt + the resulting brand-scoped report.

> This is the canonical "template + parameter" proof: one `.pbit`, N reports, each scoped by the parameter value the author supplies. Official: *Create and use report templates (.pbit)*.

### Path 2 — REST Clone + Rebind (replicate one report across brand workspaces)
Generate a per-brand copy of a published report, each bound to that brand's dataset:
```powershell
Connect-PowerBIServiceAccount
$srcWs   = "<source-workspace-id>"
$srcRep  = "<source-report-id>"
$brands  = @{ "Carvel" = "<carvel-dataset-id>"; "Moes" = "<moes-dataset-id>" }

foreach ($b in $brands.Keys) {
  $body = @{ name = "Brand Summary - $b"; targetModelId = $brands[$b] } | ConvertTo-Json
  Invoke-PowerBIRestMethod -Method Post `
    -Url "groups/$srcWs/reports/$srcRep/Clone" -Body $body
  Write-Host "Cloned for $b"
}
```
- **Clone** (`POST /groups/{groupId}/reports/{reportId}/Clone`) copies the report; `targetModelId` **rebinds** it to a different dataset → same layout, different brand data.
- **Screenshot:** multiple branded report copies in the Service.

### Path 3 — Paginated RDL with parameters → per-brand PDF (operational templating)
1. In **Power BI Report Builder**, build a parameterized catering report with a `@Brand` parameter (reuse the S.No 157 RDL).
2. Publish it, then render one PDF per brand programmatically via **Export To File**:
```powershell
$ws = "<workspace-id>"; $rep = "<paginated-report-id>"
foreach ($b in @("Carvel","Moes","Auntie Annes")) {
  $body = @{
    format = "PDF"
    paginatedReportConfiguration = @{ parameterValues = @(@{ name="Brand"; value=$b }) }
  } | ConvertTo-Json -Depth 5
  $job = Invoke-PowerBIRestMethod -Method Post -Url "groups/$ws/reports/$rep/ExportTo" -Body $body
  # poll GetExportToFileStatus, then download the file when status = Succeeded
  Write-Host "Queued PDF export for $b"
}
```
- `ExportTo` is asynchronous: poll **GetExportToFileStatus**, then GET the file. Paginated reports accept `parameterValues` → true per-brand parameterized rendering.
- **Screenshot:** the generated per-brand PDFs.

---

## Tableau — Templating via Document API + parameterized views

### Path 1 — Document API: template a .twb and generate per-brand workbooks
Install: `pip install tableaudocumentapi`
```python
from tableaudocumentapi import Workbook
import shutil

brands = {
    "Carvel": "brand_carvel.hyper",
    "Moes":   "brand_moes.hyper",
}
for brand, datasource in brands.items():
    shutil.copy("BrandSummary_template.twb", f"BrandSummary_{brand}.twb")
    wb = Workbook(f"BrandSummary_{brand}.twb")
    for ds in wb.datasources:
        for conn in ds.connections:
            conn.dbname = datasource      # repoint each brand to its data
    wb.save()
    print(f"Generated workbook for {brand}")
```
- The Tableau **Document API** edits the workbook XML (data source connection, server, dbname) to spin out per-brand `.twb` files from one template.
- **Limitation (call it out):** the Document API **cannot create workbooks from scratch** and cannot edit field/calculation logic — it only modifies an existing template's connections/parameters. It is an **open-source, unsupported** tool.

### Path 2 — Publish each generated workbook via TSC
```python
import tableauserverclient as TSC
# (sign in as in the S.No 101 POC)
for brand in brands:
    wb = TSC.WorkbookItem(project_id="<brand-project-id>", name=f"Brand Summary - {brand}")
    server.workbooks.publish(wb, f"BrandSummary_{brand}.twb", TSC.Server.PublishMode.CreateNew)
```

### Path 3 — Runtime parameterization via URL parameters
Tableau views accept filter/parameter values in the URL — one published view, many parameterized renderings:
```
https://<site>/views/BrandSummary/Overview?Brand=Carvel
https://<site>/views/BrandSummary/Overview?Brand=Moes
```
Combine with the REST **view PDF/image** endpoints to render a per-brand PDF/PNG without cloning the workbook.
- **Screenshot:** the same view rendered for two brands via URL parameter.

### What to document
- Whether the Document API successfully repointed the template per brand.
- That field/logic templating is **not** supported by the Document API (design changes mean re-templating).
- That URL parameters cover runtime parameterization but there is **no `.pbit`-style "prompt for parameters and generate a new report"** experience.

---

## Side-by-Side Findings Summary

| Capability | Power BI | Tableau |
|---|---|---|
| **Template file format** | `.pbit` — prompts for parameters on open, generates a report | `.twb` XML edited via Document API (no native "template + prompt") |
| **Parameter prompt on open** | Yes — built-in Enter Parameters dialog | No equivalent; parameters set in-workbook or via URL |
| **Replicate report across data (per brand)** | REST **Clone + Rebind** (`targetModelId`) | Document API repoints connection; then TSC publish |
| **Parameterized operational output (per-brand PDF)** | Paginated RDL + **ExportTo** with `parameterValues` | URL parameter + REST view PDF (no RDL-grade pagination) |
| **Official vs community tooling** | All paths first-party (Desktop, REST, Report Builder) | Document API is **community / unsupported**; TSC is official |
| **Field/logic templating** | Full (template carries model, measures, queries) | Document API limited to connections/parameters only |
| **Programmatic dataset parameters** | REST **UpdateParameters** (`Default.UpdateParameters`) | Connection edit via Document API |
| **Winner** | **Power BI** — three mature, first-party paths incl. parameterized paginated output | Capable for per-brand replication, but more DIY and partly unsupported |

---

## Key talking point for client call
> "For generating the same report across many brands or franchises, Power BI gives you three first-party options: `.pbit` templates that prompt for a parameter and build a report, REST Clone+Rebind to mass-produce report copies each pointed at a different brand's data, and parameterized paginated reports that render one PDF per brand on a schedule. Tableau can do per-brand replication too, but it leans on a community, unsupported Document API to edit workbook XML, plus URL parameters for runtime scoping — it works, but it's more engineering and there's no equivalent to the 'fill in the parameter and generate a report' template experience. For GTF's per-franchise report generation, Power BI is the lower-effort, better-supported path."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (Power BI) for S.No 107:**
> Three first-party paths: (1) `.pbit` templates — carry model/measures/queries and prompt for parameter values on open to generate a report; (2) REST Clone + Rebind (`targetModelId`) to replicate a report across brand workspaces against different datasets; (3) paginated RDL with parameters rendered per-brand via ExportTo (`parameterValues`, async). REST UpdateParameters sets dataset parameters programmatically. Full design templating (layout + logic).

**Column G (Tableau) for S.No 107:**
> Templating via the community **Document API** (Python) — edits `.twb` XML to repoint connections/parameters per brand, then publish via TSC. Runtime parameterization via in-workbook parameters and **URL parameters** (`?Brand=Carvel`) combined with REST view-PDF/image rendering. Limitations: Document API is open-source/unsupported, cannot create workbooks from scratch, and cannot template field/calculation logic; no `.pbit`-style parameter-prompt generation.

**Column H (Power BI Proof) for S.No 107:**
> Official documentation:
> https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-templates
> https://learn.microsoft.com/en-us/rest/api/power-bi/reports/clone-report-in-group
> https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/update-parameters-in-group

**Column I (Tableau Proof) for S.No 107:**
> Official documentation:
> https://tableau.github.io/document-api-python/
> https://tableau.github.io/server-client-python/
> https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_workbooks_and_views.htm

**Column J (Findings) for S.No 107:**
> Power BI wins for programmatic/templated report generation. It offers three mature first-party paths — `.pbit` templates with parameter prompts, REST Clone+Rebind for per-brand replication, and parameterized paginated reports rendered to per-brand PDFs via ExportTo. Tableau can replicate workbooks per brand but depends on the community/unsupported Document API plus URL parameters, with no equivalent template-and-prompt experience. For GTF's per-franchise report generation this is a lower-effort, better-supported workflow in Power BI. Advantage: POWER BI — first-party templating + parameterized paginated output; Tableau capable but more DIY.

**Column K (Status) for S.No 107:** `COMPLETED`
