# Power BI Evaluation — Findings & Power BI-Side Answers

Companion to [powerBI-vs-Tableau.md](powerBI-vs-Tableau.md) and the Tableau-side
[tableau-evaluation-findings.md](tableau-evaluation-findings.md). For each of the 9
evaluation areas this document gives: **(a) Capabilities** — what Power BI can do;
**(b) How-to** — the concrete features and setup involved; **(c) Limitations vs Tableau**
— honest gaps where Tableau is better.

Architecture assumed: **EDW → Databricks + ADF → AtScale → Power BI**. Research current as
of 2025/2026.

---

## Executive Summary

| # | Area | Verdict |
|---|------|---------|
| 1 | Azure AD / Entra ID | ✅ **Power BI strength** — natively built on Entra; SSO/MFA/Conditional Access are effectively free. Weaker only for non-Entra (Okta/Ping) estates. |
| 2 | Gateways / refresh | ✅ Mature. On-prem gateway + DirectQuery/Composite models. Refresh is **license-capped** (8/day Pro, 48/day Premium). |
| 3 | Apps & Workspaces | ✅ **Power BI strength** — true packaged Apps with audiences + publish/staging + deployment pipelines. Flatter hierarchy than Tableau projects. |
| 4 | Row Level Security | ✅ Strong — static + dynamic roles, "View as role" testing, plus **Object Level Security** (Tableau has no clean equivalent). |
| 5 | Bookmarks | ✅ **Power BI strength** — native, full-state capture. The reference feature this whole evaluation is named after. |
| 6 | Visualizations | ✅ Strong on input/filters; ✅ **strong on P&L / Matrix** (clear win vs Tableau); ⚠️ weaker on "pretty"/executive polish. |
| 7 | Large-row detail reports | ✅ **Power BI strength** — Paginated Reports (SSRS engine), true pagination, unlimited rows. Requires **Premium/Fabric capacity**. |
| 8 | "Robots" / bursting | ✅ **Power BI strength** — native **dynamic per-recipient subscriptions** + Power Automate. Requires **Premium/Fabric**. |
| 9 | SSAS / AAS / AtScale | ✅ Strong — native Live Connection with **full DAX**; AtScale via native DAX/XMLA connector. Slightly more setup than Tableau→AtScale. |

**Power BI's main cost consideration: several strengths (paginated reports, dynamic subscriptions, deployment pipelines) sit behind Premium/Fabric capacity licensing.**

---

## 1. Azure AD / Entra ID Connectivity

**(a) Capabilities**
- Power BI Service **is** built on Microsoft Entra ID — identity is intrinsic, not a bolt-on. SSO is automatic for anyone signed into Microsoft 365.
- Tenant-level **MFA and Conditional Access** policies flow through to Power BI Service, Desktop, and mobile apps with no extra config. CA supports Power BI-specific policies (require compliant device, require MFA, block legacy auth, restrict by location).
- **Entra security groups** are first-class — assignable to workspace roles, app audiences, RLS roles, and tenant settings.
- 2025/2026: **External MFA support** (OIDC-based) lets orgs use third-party MFA providers while keeping Conditional Access enforcement.

**(b) How-to**
- Identity is managed in the **Entra admin center**, not Power BI. Conditional Access: Entra admin center → Protection → Conditional Access → target the "Power BI Service" cloud app → set grant controls.
- Security groups: create in Entra, then add under workspace **Access**, app **Audiences**, or tenant settings.
- For unattended refresh that MFA/CA would block, use a **service principal** (Entra app registration) — authenticates without interactive prompts, no password expiry.

**(c) Limitations vs Tableau**
- This is a **Power BI strength** — for an all-Microsoft shop the integration is essentially free and frictionless, where Tableau requires explicit SAML/OIDC setup.
- Honest gaps: Power BI is **far less flexible for non-Entra identity** — if the client has Okta, Ping, or a mixed IdP estate, Tableau's per-site SAML/OIDC connectors are cleaner.
- Tableau offers more granular site-level auth settings and connected-app trust for embedding; Power BI embedding leans on service principals / Entra app tokens, which some teams find more rigid.

---

## 2. Gateways for Refreshing Reports

**(a) Capabilities**
- Four connectivity modes: **Import** (cached in-model, fastest queries, needs refresh), **DirectQuery** (live queries to source at runtime), **Live Connection** (to Analysis Services / Power BI semantic models / Fabric), and **Composite models** (mix Import + DirectQuery, including DirectQuery over another model).
- The **on-premises data gateway** bridges Power BI Service to non-cloud / VNet-isolated sources. **Standard (enterprise) mode** supports all modes, multiple users/sources, clustering, HA, load balancing. **Personal mode** supports only Import refresh for one user.
- **Incremental refresh** auto-partitions large tables so only recent partitions refresh; supports real-time/hybrid tables on Premium.

**(b) How-to**
- Install the standard gateway on a domain-joined server; register under a tenant admin. In Power BI Service → *Settings → Manage connections and gateways* → add data source + credentials.
- For SSO to a semantic layer: run the gateway service as a domain account, configure SPNs and **Kerberos constrained delegation** against AtScale, enable "Use SSO via Kerberos for DirectQuery queries" (AtScale documents inbound-Kerberos SSO for Power BI Service explicitly).
- Schedule refresh under semantic model *Settings → Scheduled refresh*. Configure incremental refresh in Desktop via RangeStart/RangeEnd parameters → table → Incremental refresh policy → publish.
- **Refresh limits: 8/day on Pro (shared capacity), 48/day on Premium/PPU/Fabric.**

**(c) Limitations vs Tableau**
- The scheduled-refresh cap (8x Pro / 48x Premium) is a **hard, license-tiered ceiling**; Tableau's extract refresh scheduling is more flexible and not tiered the same way.
- **DirectQuery carries well-known restrictions** — limited DAX, query-folding constraints, per-query row limits. Tableau's live connections are generally regarded as more permissive against a semantic layer.
- Composite models are powerful but add modeling complexity Tableau avoids by treating the source as authoritative.
- **AtScale impact:** the typical pattern is DirectQuery/Live to AtScale, with AtScale's autonomous aggregates providing performance — similar to the Tableau story, so refresh scheduling is largely moot either way.

---

## 3. Apps & Workspaces

**(a) Capabilities**
- **Workspaces** — collaboration containers where developers build/store content (semantic models, reports, dashboards).
- **Power BI Apps** — the packaged, read-only **consumer experience** published *from* a workspace: a curated, navigable bundle for end users. **App audiences** let one app show different content sets to different Entra groups.
- Four workspace roles: **Admin** (full control), **Member** (edit, publish/update app), **Contributor** (edit, no app publish/access mgmt), **Viewer** (read-only).
- **Deployment pipelines** (Premium/Fabric) — structured Dev → Test → Prod stages with automated promotion and per-stage data source rules.
- 2025/2026: **Org apps (preview)** — multiple apps per workspace, bulk audience management, deployment-pipeline + Git integration.

**(b) How-to**
- Create a workspace → assign roles under *Access*. Build content → **Create app** → define audiences (content tabs) → assign Entra groups per audience → Publish (with staging/update flow).
- Set up a deployment pipeline → assign Dev/Test/Prod workspaces → use deployment rules to swap gateway/data source bindings per stage.
- Centralized access = manage Entra groups once, map them to workspace roles and app audiences.

**(c) Limitations vs Tableau**
- **This is a Power BI strength** — it has a true packaged "App" with publish/staging and audiences, which Tableau lacks (Tableau approximates with Projects + Collections).
- But Power BI's two-layer model (workspace + app) is **flatter and more rigid** than Tableau's **nested projects with inherited permissions** — Tableau gives finer folder-style governance.
- Classic Power BI allowed only **one app per workspace** (org apps fixing this is still **preview**, not GA).
- Deployment pipelines require **Premium/Fabric capacity** — a cost gate Tableau doesn't impose for promotion workflows.
- Tableau's permission model is more granular at the individual content/capability level; Power BI's four fixed roles are coarser.

---

## 4. Row Level Security (RLS)

**(a) Capabilities**
- **Static (role-based) RLS** — hard-codes a filter per role (e.g., "Franchise_TX" → `Franchise = "TX"`). Good for a fixed, small set of groups.
- **Dynamic RLS** — uses the logged-in identity to look up access from a security/bridge table; scales to thousands of users with one role.
- **Object Level Security (OLS)** — restricts *tables and columns* (not just rows); restricted objects throw an error if queried directly or indirectly. RLS + OLS can coexist.

**(b) How-to**
- Power BI Desktop: **Modeling → Manage roles** → define roles with DAX filter expressions (e.g., `[Franchise] = "West"`).
- Dynamic RLS: build a `UserSecurity` table mapping email → franchise, relate it to the fact table, filter with `[Email] = USERPRINCIPALNAME()`.
- Test with **Modeling → View as** ("View as role" / "View as other user").
- Publish, then assign Entra users/groups to roles in the Service under the semantic model's **Security** page. OLS is configured via **Tabular Editor** (no native Desktop UI).
- **AtScale note:** AtScale enforces its own RBAC/RLS/CLS centrally and pushes governance down to the warehouse. If RLS is enforced at AtScale, Power BI connects with the user's identity passed through (SSO/Kerberos delegation) and does **not** re-implement RLS — franchise filtering lives in AtScale. Cleaner architecture, but requires correct SSO config. **Pick one enforcement layer.**

**(c) Limitations vs Tableau**
- For a **Live Connection to a semantic model / Analysis Services**, RLS is enforced *in the model* — the Security option doesn't appear in the connecting report, and report authors can't add/override roles.
- Broadly comparable to Tableau's user filters / `USERNAME()` / data-source RLS — neither tool is dramatically ahead.
- **Power BI's OLS is a genuine extra** — Tableau lacks a clean native equivalent for column/table-level security.

---

## 5. Bookmarks

**(a) Capabilities**
- This is the **Power BI native strength** the evaluation is literally named after. A bookmark captures full page state: filters, slicer selections, sort order, drill level, spotlight/focus, and the **visibility** of every object.
- Two types: **Report bookmarks** (author-created, saved with the report) and **Personal bookmarks** (consumer-created in the Service, max 20 per report).

**(b) How-to**
- Enable **View → Bookmarks pane**, arrange the page, click **Add**. Use the **Selection pane** to show/hide objects and reorder layers — combined with bookmarks this drives show/hide "pop-up" panels and toggles.
- Each bookmark's scope (Data / Display / Current page / All or Selected visuals) is configurable.
- Insert **Buttons → Navigator → Bookmark navigator** (auto-syncs to all bookmarks) or **Page navigator** for nav menus; individual Buttons/Images/Shapes can each trigger a bookmark via the Action property.

**(c) Limitations vs Tableau**
- **Power BI is clearly ahead here** — Tableau has no direct equivalent that captures full layout/visibility state in one click (it approximates with Custom Views + Dynamic Zone Visibility + parameter actions).
- Honest gap: bookmarks can become **fragile/hard to maintain at scale** — every visibility change must be re-captured with **Update** — and personal bookmarks are capped at 20.

---

## 6. Visualizations

### a. Report with User Input / Action — ✅ Strong
- **Slicers** (list, dropdown, between, hierarchy, **input slicer** for text/numeric entry); **What-if parameters** (numeric-range scenario modeling, generates a slicer + measure); **Field parameters** (let users swap dimensions/measures in a visual via a slicer); **Drill-through** pages; **cross-filtering/cross-highlighting**; **Buttons** with Action (bookmark, page nav, drill-through, Q&A).

### b. Reports with Many Filters — ✅ Strong
- The **Filter pane** (report/page/visual-level filters, lockable and hideable); **slicers** and **Sync slicers** (one slicer drives multiple pages).
- For performance with many slicers, add an **Apply all slicers** button (+ **Clear all slicers**) so visuals re-query once instead of on every selection. Individual slicers also have a per-slicer **Apply** button.

### c. Pretty Visualization — ⚠️ Honest gap vs Tableau
- Power BI offers **report Themes** (JSON-based), 100s of **AppSource custom visuals** (Zebra BI, ZoomCharts, etc.), and a developer SDK.
- **However, Tableau is still widely considered better for polished, executive/board-facing dashboards** — Power BI's native visuals are less customizable, fine design tweaks often need workarounds even with custom visuals, and pixel-level layout control is weaker. Flag this to the client.

### d. P&L Reporting — ✅ Clear Power BI strength vs Tableau
- The **Matrix visual** is purpose-built for financial statements: hierarchical rows, stepped/expandable hierarchies, drill-down, **subtotals/grand totals**, period columns.
- **DAX measures** compute line items; **Calculation Groups** (built in Tabular Editor) elegantly handle time intelligence (YTD, PY, variance) without dozens of measures.
- **Custom formatting** — conditional formatting, per-row format strings, persist-hierarchy-level matrix behavior.
- Native limitations (custom row ordering, calculated subtotal *lines*, blank spacer rows) are real but solved with DAX patterns or custom visuals (**Profitbase Financial Reporting Matrix**, **Inforiver**, **Zebra BI**).
- **Tableau struggles here** — no true matrix-with-subtotals equivalent; financial-statement layouts are notoriously awkward. **Clear advantage Power BI.**

---

## 7. Reports with Large Number of Rows (e.g., Catering Detail Report) — ✅ Power BI Strength

**(a) Capabilities**
- Two report types: *standard (interactive) reports* (visualization-first, not for detail dumps) and **Paginated Reports** — the RDL/SSRS-based engine for pixel-perfect, multi-page, printable "banded" detail reports.
- The **tablix** (table/matrix) in a paginated report has **no row-count limit** — it renders and exports as many rows as the source returns, paginating across pages automatically.
- Export to PDF, Excel, CSV, Word, PowerPoint, image, accessible PDF — with print-ready layout (headers/footers, page breaks, repeating group headers).

**(b) How-to**
- Author with **Power BI Report Builder** (free download; the supported authoring tool). Build a dataset (can point at the AtScale semantic model, a Power BI semantic model, Databricks, etc.), drop a **Tablix**, set group headers/footers and page breaks, then **publish the .rdl to a Power BI/Fabric workspace**.
- Consumers export via the service, or it's delivered by subscription. Programmatic export via the **Export-to-File API**.

**(c) Limitations vs Tableau**
- **Capacity requirement is the big one:** paginated reports only run in a workspace on **Premium Per User (PPU)** or **Fabric/Premium capacity (F64+ / P1+ for free-license viewers)**. No Pro-tier paginated report — a real licensing cost to budget.
- Standard Power BI report visuals are weak for detail data: table/matrix ~30,000 data points by default; matrix export caps at 150,000 intersections; visual CSV export caps at 30,000 rows, xlsx at 150,000, underlying data up to 500,000 (Import). So large detail reports **must** use paginated reports.
- Report Builder is a separate, older, Windows-only tool with a clunkier authoring experience than Power BI Desktop; paginated reports cap at 250 data sources per report.
- **Versus Tableau:** Power BI genuinely wins here — Tableau has no SSRS-style paginated engine and handles pixel-perfect, unlimited-row, printable banded reports awkwardly. The catering detail report is a Power BI strength.

---

## 8. Equivalent to Power BI Robots (Automation / Bursting) — ✅ Power BI Strength

**(a) Capabilities**
- **Standard email subscriptions** (per-user) — send a snapshot of a report/dashboard page on a schedule.
- **Dynamic per-recipient subscriptions** — the true SSRS-style "data-driven subscription" / bursting feature: one subscription delivers a *differently filtered* copy to each recipient. Ideal for **automated franchise-specific filtered delivery**. Available for **both paginated and standard Power BI reports**.

**(b) How-to**
- Create a **semantic model mapping recipients to filter/parameter values** (columns: email, parameter/filter value, optional subject, attachment type).
- In the Service, create a **Dynamic subscription** on the report, point it at that mapping model, pick the schedule. At send time Power BI reads the latest mapping rows and bursts a personalized file to each recipient.
- For conditional/branded delivery, use **Power Automate** with the "Export to File for Power BI Reports/Paginated Reports" action + "Send an email" — enabling branded HTML, conditional logic ("only send if metric changed"), Teams/SharePoint delivery.

**(c) Limitations vs Tableau**
- Dynamic subscriptions require **Premium/Fabric or PPU** (same capacity gate as paginated reports).
- Hard limits: recipient mapping model capped at **1,000 rows**; dynamic paginated subscriptions have a **10-minute timeout**.
- Native subscriptions can't do complex branching/branding — that needs Power Automate flows (extra complexity; premium connectors may apply).
- **Versus Tableau:** largely a **Power BI strength** — Tableau's subscriptions are simpler and its bursting story is weaker (needs REST API / tabcmd / third-party tools). Power BI's dynamic subscriptions + Power Automate give more out-of-the-box bursting.

---

## 9. SSAS / Azure Analysis Services Connectivity (and AtScale)

**(a) Capabilities**
- First-class **Live Connection** to **SSAS Tabular, SSAS Multidimensional, Azure Analysis Services, and Power BI semantic models** — the only four live-connection sources. No data imported; every interaction queries the model.
- For Tabular / AAS / Power BI semantic models, **full native DAX** is supported, including **report-level measures** — meaningfully better than Tableau's MDX cube connector.

**(b) How-to**
- Power BI Desktop → **Get Data → SQL Server Analysis Services database** (or Azure Analysis Services database) → **Connect live**. Model tables, columns, hierarchies, and measures appear in the Data pane.
- An **on-premises data gateway** is required when publishing live-connected reports for on-prem SSAS. Semantic models can also be reached via the **XMLA endpoint** (Premium/Fabric).
- **AtScale + Power BI:** AtScale exposes its semantic model through a **jointly developed native DAX connector** — Power BI connects in **Live Connection mode** over an **XMLA endpoint (compatibility level 1600)** with **full native DAX** (no DAX-to-SQL translation penalty), plus MDX/Excel cube-function support. AtScale's autonomous aggregates deliver sub-second queries over Databricks. **User impersonation** passes credentials to AtScale for policy enforcement. Fits the EDW → Databricks+ADF → AtScale → Power BI architecture cleanly.

**(c) Limitations vs Tableau**
- SSAS **Multidimensional**: live connection works but you **cannot author report-level measures** — only model-defined measures are usable. AAS doesn't support multidimensional models at all (Tabular only).
- AtScale-to-Power BI requires configuring/maintaining the AtScale XMLA endpoint, gateway/network routing, and SSO — robust but **a bit more setup-heavy** than Tableau→AtScale, which AtScale positions as its most mature "out-of-the-box" integration.
- **Net:** close to **parity** — slight edge to Tableau on setup simplicity, slight edge to Power BI on analytical depth (full DAX vs Tableau's MDX constraints).

---

## Recommendation

Power BI is a strong fit for the enterprise BI requirements on the AtScale architecture, and is **clearly ahead of Tableau in the areas this evaluation prioritizes**: Azure AD integration (1), Apps/Workspaces with packaging and staging (3), bookmarks (5), P&L/Matrix financial reporting (6d), large-row paginated reports (7), and automated per-recipient bursting (8).

**The trade-offs to weigh against Tableau:**
- **Licensing/cost:** several of Power BI's strengths — paginated reports (7), dynamic subscriptions (8), deployment pipelines (3) — require **Premium Per User or Fabric/Premium capacity**. Budget for this explicitly.
- **"Pretty" / executive dashboards (6c):** Tableau retains an edge in polished, board-facing visual design.
- **Identity flexibility (1):** Power BI's Entra-centric model is a strength for a Microsoft shop but a constraint if the IdP estate is mixed (Okta/Ping).
- **Refresh cadence (2):** Power BI's scheduled-refresh caps are license-tiered; less relevant under a live AtScale connection.
- **Governance hierarchy (3):** Tableau's nested projects give finer-grained folder governance than Power BI's flatter workspace model.

Given the client already runs Power BI on the old SSAS architecture and is Microsoft-centric, Power BI on AtScale is the lower-risk continuation — with the main open question being whether Tableau's visualization polish and governance granularity justify adopting it alongside or instead.
