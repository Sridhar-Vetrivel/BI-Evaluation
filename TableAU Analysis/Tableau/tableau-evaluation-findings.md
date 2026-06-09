# Tableau Evaluation — Findings & Tableau-Side Answers

Companion to [powerBI-vs-Tableau.md](powerBI-vs-Tableau.md). For each of the 9 evaluation
areas this document gives: **(a) Capabilities** — what Tableau can do; **(b) How-to** — the
concrete features and setup involved; **(c) Limitations vs Power BI** — honest gaps.

Architecture assumed: **EDW → Databricks + ADF → AtScale → Tableau**, with Tableau Cloud
and/or Tableau Server. Research current as of 2025/2026.

---

## Executive Summary

| # | Area | Verdict |
|---|------|---------|
| 1 | Azure AD / Entra ID | ✅ Fully supported (SAML/OIDC + SCIM). More setup than Power BI, but no functional gap. |
| 2 | Gateways / refresh | ✅ Supported. Tableau Bridge ≈ Power BI gateway. With AtScale, the story is **live connections**, so refresh scheduling largely moves to AtScale. |
| 3 | Power BI Apps equivalent | ⚠️ Partial. Projects + Sites + Collections cover most of it; **no true packaged "App" with publish/staging**. |
| 4 | Row Level Security | ✅ Strong. Virtual Connections + Data Policies = centralized RLS. Needs **Data Management add-on**. |
| 5 | Bookmarks equivalent | ⚠️ No single equivalent — assemble Custom Views + Dynamic Zone Visibility + parameter actions. More effort. |
| 6 | Visualizations | ✅ Strong on interactivity & "pretty"; ⚠️ **weak on P&L / matrix-style financial tables**. |
| 7 | Large-row detail reports | ❌ Weakest area. **No SSRS-style paginated reports**, no true pagination. |
| 8 | Power BI "Robots" equivalent | ⚠️ No native per-recipient bursting. Needs **REST API scripting or 3rd-party tooling**. |
| 9 | SSAS / AAS / AtScale | ✅ AtScale is the key win — Tableau sees it as **SQL**, avoiding the OLAP cube-connector limitations. |

**The two real risk areas to weigh: Area 7 (catering detail report) and Area 8 (franchise bursting).**

---

## 1. Azure AD / Entra ID Connectivity

**(a) Capabilities**
- Both Tableau Cloud and Tableau Server support **SAML 2.0** and **OpenID Connect (OIDC)** with Entra ID as the IdP, plus **SCIM 2.0** user/group provisioning.
- **MFA** is enforced through the IdP — delegated to Entra ID Conditional Access. Tableau Cloud has *required* IdP-based MFA since Feb 2022.
- **Multiple auth methods per site** (Tableau 2024.3+): up to ~18–20 auth configurations on one site; individual users can be assigned Tableau ID vs. external IdP.
- SAML attribute assertions can feed Tableau's **user attribute functions** for dynamic content/row control (2025.3+).

**(b) How-to**
- **Tableau Cloud SAML**: add the "Tableau Cloud" app from the Entra ID enterprise-apps gallery → exchange metadata XML in *Settings > Authentication*.
- **Tableau Server SAML**: requires a server-wide **SSL certificate (SHA-2)** first; configured via TSM or `tsm authentication saml`.
- **SCIM**: requires SAML/OIDC/Google SSO already configured; uses an **OAuth 2.0 bearer token**; Entra ID auto-provisioning syncs users and groups.
- **OAuth for data connections** is configured separately ("Configure Azure AD for OAuth and Modern Authentication").

**(c) Limitations vs Power BI**
- Power BI is **natively built on Entra ID** — zero SSO setup, identity is intrinsic. Tableau requires explicit IdP configuration and (for Server) certificate lifecycle management.
- No native MFA — fully dependent on Entra ID Conditional Access.
- SCIM group → Tableau group mapping works but is less seamless than Power BI's direct use of Entra groups in security/permissions.
- **Net:** no functional gap, just more configuration and operational overhead.

---

## 2. Tableau Gateways for Refreshing Reports

**(a) Capabilities**
- Two connection modes: **Live** (queries source at view time) and **Extract** (`.hyper` snapshot on a schedule). Both on Cloud and Server.
- **Tableau Server** connects **directly** to any data source on its network — no gateway component needed.
- **Tableau Cloud** uses **Tableau Bridge** (free, self-hosted Windows client) to reach private/on-prem data — the direct analog to Power BI's on-premises data gateway.

**(b) How-to**
- **Extract refresh scheduling**: set at publish time or in the Server/Cloud UI; reusable hourly/daily/weekly/monthly schedules.
- **Incremental refresh**: configured in Desktop/web authoring *before* publishing, keyed on a date/datetime/integer column (2024.1+ supports non-unique keys; 2024.2+ adds a minimum date-range re-capture window).
- **Tableau Bridge**: install client → register to site → create **Bridge pools** for load balancing. Runs in *Application mode* (interactive) or *Service mode* (Windows service). Limits: 16 live queries / 10 concurrent extract refreshes per client (tunable).

**(c) Limitations vs Power BI**
- Bridge is **Windows-only and self-managed** (you size/patch/scale it). Power BI's gateway gets monthly Microsoft updates and has more mature clustering.
- Tableau's **incremental refresh is weaker** — append-oriented; no true partition management like Power BI.
- No equivalent to Power BI's **DirectQuery + composite models / aggregations** hybrid modeling.
- **AtScale impact:** semantic-layer connections are **live-only** (extracts generally not supported against a semantic layer). With AtScale, the refresh story shifts to **AtScale's own aggregate management** — AtScale's aggregate cache provides extract-like performance, and Bridge mainly serves **live query pass-through** for Tableau Cloud. Extract-refresh scheduling becomes largely moot.

---

## 3. Equivalent Feature to Power BI Apps

**(a) Capabilities**
- **Sites** — top-level tenant boundary (isolated users/content/admin). Closest to a Power BI tenant/capacity separation, not a workspace.
- **Projects** — containers for workbooks/data sources/flows; **support nesting** (sub-projects). The primary org unit ≈ Power BI **Workspaces**, but with hierarchy Power BI lacks.
- **Collections** — user-created, cross-project curated groupings (like playlists). Partial analog to the curated-consumption side of Power BI Apps.
- **Permissions** — granular capability-based model (View, Filter, Download, Web Edit, etc.) at project/workbook/view/data-source level, with inheritance + per-item overrides.
- **Project Leader** role — delegated admin over a project and all nested content (≈ Workspace Admin).

**(b) How-to**
- Create Projects; nest for App-like grouping. Use **"Manage Permissions with Projects"** — *lock* permissions to enforce inheritance, or *unlock* for per-item control.
- Assign **Project Leader** for delegated governance.
- Build **Collections** from the Explore page; use **Groups** (SCIM-synced from Entra) as permission grantees.
- Recommended mapping: Power BI Workspace → Tableau **Project** (use nesting); Workspace Admin → **Project Leader**; the polished "App" consumer layer → Projects + Collections + curated permissions.

**(c) Limitations vs Power BI**
- **No true "App" equivalent.** Power BI Apps are a packaged, versioned, navigation-curated consumer experience with a publish/staging step. Tableau **Collections do not control permissions** — each user still sees only items they individually have access to, so a Collection can look different per user. There is **no app-level publish/staging or release management** — content is live the moment it's published (mitigate with dev/prod projects or sites).
- **Conversely, Tableau is stronger on hierarchy and granularity:** nested projects + per-item permission overrides exceed Power BI's flat Workspace + 4 fixed roles.

---

## 4. Row Level Security (RLS)

**(a) Capabilities** — four approaches, increasing robustness:
1. **User filters** — manual UI mapping of users/groups to dimension values. Small static lists only.
2. **Calculated-field RLS** — `USERNAME()`, `FULLNAME()`, `ISMEMBEROF('group')`, `USERDOMAIN()` applied as a **data source filter**. Works live or extract.
3. **Entitlement-table RLS** — a security table joins user identity → permitted values (e.g., user → franchise). Scales to thousands of users; supports many-to-many.
4. **Virtual Connections + Data Policies** — Tableau's **centralized RLS**: a data policy defined once on a virtual connection auto-enforces on every workbook/data source/dashboard built on it.

**(b) How-to** — for franchise-level / role-based security, use **Virtual Connections + Data Policies** (requires the **Data Management** add-on):
- Create a Virtual Connection; add the **entitlement table** (franchise → user/group) and set it hidden.
- Create a Data Policy: designate **policy tables** (fact tables to filter), **mapped columns** (entitlement → fact), and a **policy condition** (`USERNAME() = [Username]` or `ISMEMBEROF()`).
- Publish — all downstream content inherits it.
- **AtScale note:** AtScale exposes SQL, so Tableau-side data policies apply at query time. Alternatively push RLS down into AtScale's own security model. **Pick one enforcement layer** to avoid double-filtering. `ISMEMBEROF()` against Tableau Server groups is cleanest for dynamic/role-based access.

**(c) Limitations vs Power BI**
- Power BI RLS = **Roles + DAX filters in the model**, included in Pro. Tableau's strongest, centralized RLS is **paywalled behind the Data Management add-on**.
- Power BI RLS lives in the semantic model (one definition); Tableau's non-virtual-connection RLS can scatter across workbooks unless discipline is enforced.
- Power BI roles are first-class and testable ("View as role"); Tableau RLS testing is more manual (impersonate user).
- **Net:** comparable power; Tableau needs the add-on to match Power BI's centralized convenience.

---

## 5. Bookmarks Equivalent

Power BI bookmarks capture a full state (filters, slicers, visibility, sort, selection) in one click. **There is no single Tableau equivalent** — it's a combination:

**(a) Capabilities / (b) How-to**
- **Custom Views** (Server/Cloud) — closest to a *personal* bookmark: saves a user's filter/sort/parameter state of a published view; shareable, settable as default.
- **Dashboard navigation objects / buttons** — page-to-page navigation between dashboards/sheets.
- **Show/Hide buttons** (2019.2+) — toggle floating containers manually.
- **Dynamic Zone Visibility** (2022.3+) — show/hide zones programmatically via a boolean field/parameter; the modern automatic equivalent of bookmark visibility groups.
- **Sheet swapping** — parameter-driven swap of which viz displays inside a container.
- **Parameter actions** — click a mark to set a parameter and switch measures/views.

**(c) Limitations vs Power BI**
- Power BI bundles *everything* into one click with a built-in Bookmark pane + Selection pane. Tableau requires assembling 3–4 separate features — more developer effort, harder to maintain.
- **Custom Views are per-user / runtime**, not author-designed snapshots baked into the workbook.
- **Tableau Story** handles guided narrative but is not a bookmark replacement and is widely seen as dated.
- **Net:** outcomes are achievable, but with noticeably more friction.

---

## 6. Visualizations

### a. Report with User Input / Action — ✅ Strong (matches or exceeds Power BI)
- **Parameters** (string/numeric/date/boolean), **dynamic parameters** (refresh values from data), **dynamic spatial parameters** (2025.2).
- **Dashboard actions**: filter, highlight, URL, go-to-sheet, **parameter actions** (click a mark → set a parameter), **set actions** (click → modify set membership; great for drill/compare).
- What-if analysis via parameters + calculated fields.

### b. Reports with Many Filters — ✅ Capable, with tuning
- Multiple quick filters, cascading filters ("Only Relevant Values"), wildcard/range filters.
- **Context filters** materialize a temp table to speed up downstream filters — use sparingly (one large-reduction filter, not many).
- **"Apply" button** on filters batches user selections before querying — directly comparable to Power BI's Apply button.
- *Friction:* many cross-filtering quick filters on large live datasets each fire a query; performance tuning is more of a manual craft than Power BI's import mode. **AtScale's aggregate awareness mitigates this.**

### c. Pretty Visualization — ✅ Tableau's traditional strength
- Pixel-level design control, **layout containers**, device-specific layouts, **Tableau Story**, **Viz Extensions** (2024+) and dashboard extensions, Data Guide, light/dark mode.
- Generally regarded as **superior to Power BI** for executive/polished dashboards.
- *Friction:* responsive design is less automatic than Power BI; containers can be fiddly.

### d. P&L Reporting — ⚠️ Tableau's known weakness
- Tableau **does** support hierarchies, drilldowns, subtotals, grand totals, custom number formatting, and matrix-style cross-tabs.
- **But:** there is **no true equivalent of Power BI's Matrix visual.** Multi-level financial statements with custom row ordering, indentation, mixed-sign subtotals, ratio rows, and inserted calculation rows are awkward — Tableau subtotals are aggregations of displayed rows, not flexible inserted lines. Custom P&L line-item ordering typically needs a helper/ordering table. Dense financial tables render slower and look less native.
- **Net:** for finance-heavy reporting, expect rework and workarounds in Tableau.

---

## 7. Reports with Large Number of Rows (e.g., Catering Detail Report) — ❌ Weakest Area

**(a) Capabilities**
- No enforced row/column limit on imported/extract data — the **Hyper engine** handles large volumes. The *view* is the bottleneck: default cap of 6 dimensions on Rows/Columns, raisable to 16 via *Analysis > Table Layout > Advanced*.
- **View Data** popup is capped (~10,000 rows in the UI); full data only via export.
- **Crosstab export** to Excel/CSV handles larger detail dumps (Excel export bound by Excel's ~1,048,576-row limit).

**(b) How-to**
- For tabular detail: text-table worksheet + *Analysis > Table Layout > Advanced* to lift the dimension cap.
- Export: *Worksheet > Export > Crosstab to Excel*, or *Download > Crosstab* on Server/Cloud — exclude formatting to speed large exports.
- **Pagination is faked** — no true paginated reports. Common workaround: an `INDEX()` calculated field + a "Page Number" parameter to filter N rows per "page".

**(c) Limitations vs Power BI**
- Tableau is explicitly built for **visualization, not large tabular detail dumps** — big text tables degrade rendering badly.
- **No SSRS equivalent.** Power BI **Paginated Reports** (RDL/SSRS-based, Report Builder) are purpose-built for pixel-perfect, multi-page, printable, large-row operational reports with true pagination, headers/footers, and reliable PDF/Excel rendering. **Tableau has nothing comparable** — the "catering detail report" use case is a genuine weak spot.
- Mitigations: pre-aggregate/pre-join in the source or AtScale, hide unused columns, limit date ranges, avoid wide varchar tables. **If pixel-perfect large operational reports are a hard requirement, this is the area most likely to require keeping Power BI (paginated reports) or another tool.**

---

## 8. Equivalent to Power BI Robots (Automation / Bursting)

**(a) Capabilities**
- **Subscriptions** — scheduled email delivery of a view/workbook as image or PDF.
- **Data-Driven Alerts** — email when a continuous numeric measure crosses a threshold.
- **REST API** — programmatic creation/management of subscriptions and content.

**(b) How-to**
- *Subscription*: open view → **Subscribe** → set format, schedule, recipients. Filters are only respected if you subscribe from a filtered view state — fragile, not per-recipient.
- *Data-Driven Alert*: select a continuous axis → **Alerts panel > Create** → condition/threshold/schedule/recipients (content must be published; not buildable in Desktop).
- *Bursting (recommended)*: use the **REST API** (`Subscriptions` methods) **plus RLS/User Filters** so each franchise user sees only their data; script per-recipient filtered PDFs via API / `tabcmd` / Hyper exports. Or use **third-party bursting tools** (e.g., ChristianSteven, Rollstack).

**(c) Limitations vs Power BI**
- **Native subscriptions do NOT do per-recipient filtering well** — no native "burst by franchise"; long-standing open community feature requests.
- True personalized bursting requires **REST API scripting or third-party software** — budget engineering effort for this.
- Power BI offers per-user subscriptions, **paginated-report data-driven subscriptions** (true bursting in Premium), and **Power Automate** flows — more turnkey for this exact "Robots" use case.
- **Net:** achievable in Tableau, but it's a build, not a feature toggle.

---

## 9. SSAS / Azure Analysis Services Connectivity (and AtScale)

**(a) Capabilities — cube connectors**
- Tableau connects **live** to **SSAS multidimensional cubes**, **SSAS Tabular**, and **Azure Analysis Services** via the MSOLAP/MDX-based "Cube" connector. Always live — no extracts from cubes.

**(b) How-to — cubes**
- Connect via the **Microsoft Analysis Services** connector → server, database, cube. For calculations, use *Analysis > Create Calculated Member* (MDX syntax) instead of standard Tableau calcs.

**(c) Cube connector limitations — significant**
- **Calculated fields**: measures only — **cannot create calc fields from dimensions**; **no LOD expressions**.
- **Unsupported**: forecasting, clustering, trend lines, cross-dimension set actions.
- You lose a meaningful chunk of Tableau's analytical surface; power users must hand-write **MDX calculated members** — a steep skill requirement.

**AtScale + Tableau — the key win for the new architecture**
- AtScale exposes its semantic models to Tableau as a **relational data source over SQL** — Tableau connects **live** and treats it like a SQL database. AtScale now offers a **native Tableau Cloud connector** (no driver download, no Tableau Bridge, OAuth SSO).
- Because Tableau sees **SQL, not MDX/OLAP**, you **avoid all the cube-connector limitations** — LOD expressions, normal calculated fields, trend lines, forecasting, and clustering all work normally.
- AtScale handles dimensional modeling, governed metrics, and **smart/in-memory aggregates** that push aggregation down to Databricks — "import-mode performance with live-connection flexibility".
- AtScale's **multi-protocol** support (SQL / DAX / MDX) means the *same* semantic layer serves both Power BI and Tableau consistently — valuable during a phased migration.

**(c) Limitations vs Power BI**
- Direct (non-AtScale) cube connectivity is clearly weaker in Tableau than Power BI's native SSAS/AAS handling.
- **But with AtScale in the path, this area becomes a strength** — and is the main reason the new architecture de-risks a Tableau adoption.

---

## Recommendation

Tableau can support the enterprise BI requirements on the AtScale architecture. **AtScale neutralizes the historic Tableau-on-OLAP weakness (Area 9)** and is the linchpin of the strategy. Areas 1–6 are all viable, with the main caveats being extra setup (1, 3), an add-on license for centralized RLS (4), more build effort for bookmark-like behavior (5), and workarounds for P&L/matrix layouts (6d).

**The two areas that need an explicit decision before committing:**
- **Area 7 — large detail reports (catering detail report):** Tableau has no SSRS-style paginated reporting. Decide whether to keep Power BI paginated reports for these, push detail extracts to another channel, or accept crosstab-export workarounds.
- **Area 8 — franchise-specific bursting:** budget for REST API development or a third-party bursting tool; it is not a native feature.
