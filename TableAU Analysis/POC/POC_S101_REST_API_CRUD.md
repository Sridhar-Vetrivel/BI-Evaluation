# POC Guide — S.No 101: REST API Coverage (CRUD on Reports, Datasets, Workspaces, Users)
**Category:** 11. Extensibility & Developer Ecosystem | **Priority:** High | **AtScale dependency:** None

> **Reality of this item:** REST *management* APIs (create workspace, add user) act on a hosted backend — there is no purely offline "create a workspace" call. So this item is best proven as **documentation-confidence + a lightweight hands-on demo**. Pick whichever execution tier below matches the access you have. **No AtScale needed.**

---

## Scenario (GTF-specific)
GTF onboards franchises continuously and organizes BI content **by brand**. The current "Power BI robots" already automate report delivery — so the client cares whether the *same automation muscle* exists in Tableau. This POC proves both tools can be driven entirely by API for the operational lifecycle:

- **Create** a workspace (Power BI) / project (Tableau) for a new brand — e.g., "Brand-Carvel"
- **Publish** a dataset/data source and a report/workbook into it programmatically
- **Read** the inventory (list all workspaces, datasets, reports, users)
- **Update** — add a franchise user to the right group with Viewer access; clone a report
- **Delete** — tear down the test workspace/project

This is the real GTF need: **provision brand workspaces and onboard hundreds of franchise users without manual clicks.**

**Expected verdict:** Both tools expose mature, well-documented REST APIs covering full CRUD on the four object types. Power BI adds first-class **PowerShell cmdlets** + **service-principal** auth (unattended automation, Azure-native). Tableau offers a clean **Personal Access Token** auth model and an official **Python client (TSC)**. Likely a **Tie**, with Power BI slightly ahead for Azure-native unattended automation (service principals + Entra) and Tableau slightly ahead for developer ergonomics (TSC). 

---

## Execution tiers — pick by what you have (no prerequisites required for Tier 1)

| Tier | What you need | What it proves | Effort |
|---|---|---|---|
| **1. Local mock (recommended start)** | **Just Python** — no account, no install, no internet | The CRUD **automation pattern** works end-to-end against both vendors' REST URL shapes | 2 min |
| **2. Free real endpoints** | A **free Tableau Developer site** + a **free Power BI/Fabric trial** | The **live vendor platforms** accept the CRUD calls | 20–30 min |
| **3. GTF environment** | GTF's existing Power BI tenant (via Ni) + provisioned Tableau site | CRUD in the **actual target environment** | depends on access |

> The official REST API documentation is authoritative proof that the *platform* supports these operations (see proof links). Tier 1 proves *your code* drives them; Tier 2/3 confirm against a live endpoint when you want a screen-share demo.

---

### Tier 1 — Local, zero-account, zero-install (do this first)
Run the bundled script — it starts an in-memory mock of the Power BI **and** Tableau REST endpoints on `localhost` and runs the full Create→Read→Update→Delete lifecycle (workspace/project, dataset, report/workbook, user) against both, asserting each step:

```powershell
python POC/poc_s101_local_demo.py
```
Expected output: **16/16 CRUD operations PASS** for both vendor REST shapes. Requires **Python 3.8+ only** — nothing else.
**Screenshot:** the PASS transcript. This demonstrates the exact provisioning flow GTF needs (auto-create a brand workspace, publish content, onboard a franchise user, tear down) without any tenant.

> **What Tier 1 does and doesn't prove:** it proves the integration/automation code performs correct CRUD and parses responses. It does **not** prove the live vendor accepts the calls — that's what the official docs (authoritative) and Tier 2 cover.

---

### Tier 2 — Free real endpoints (for a live demo, still no cost)
**Tableau (easiest genuine proof — a permanent free site):**
1. Join the **Tableau Developer Program** (free) → you get a **free, non-expiring Tableau Cloud developer site**.
2. In the site: **User → My Account Settings → Personal Access Tokens → create token**.
3. Locally: `pip install tableauserverclient`, then run the TSC script in the "Tableau — Full CRUD" section below against your dev site. Real CRUD, driven from your laptop, $0.

**Power BI (free trial or browser console):**
1. Sign up for a **free Microsoft Fabric / Power BI trial** (60 days) with a work/school email — gives you a tenant with "My workspace" and the ability to create workspaces.
2. Easiest demo with **no code and no app registration**: open any Power BI REST operation page on Microsoft Learn and use the built-in **"Try it"** console — it signs in with your account and calls the **live** API in-browser (e.g., GET `/groups`, GET datasets/reports, POST add user).
3. For scripted CRUD, run the PowerShell in the "Power BI — Full CRUD" section using `Connect-PowerBIServiceAccount` (interactive login — no service principal needed for a demo).

> Tier 2 needs only free sign-ups. Tier 3 (GTF tenant) is optional and only if you want to demo in the production-adjacent environment.

---

### Reference scripts (used by Tier 2/3)
The PowerShell and Python below are the **real** scripts for a live site/tenant. For Tier 1 you don't need them — the bundled demo already exercises the same lifecycle locally. Sample content to publish: build a `.pbix` / `.twbx` from the parquet sample, or reuse an existing GTF test copy from Ni.

---

## Time estimate

| Section | Time |
|---|---|
| Power BI — auth, CRUD on all 4 objects (PowerShell + REST) | 30–40 min |
| Tableau — auth, CRUD on all 4 objects (TSC Python) | 30–40 min |
| Screenshots + findings entry | 15 min |
| **Total** | **75–95 min** |

---

## Power BI — Full CRUD via PowerShell + REST

### Step 1 — Authenticate
**Option A — interactive (fastest for POC):**
```powershell
Install-Module MicrosoftPowerBIMgmt -Scope CurrentUser
Connect-PowerBIServiceAccount        # opens Entra login
```
**Option B — unattended (service principal, the production pattern):**
```powershell
$tenant = "<tenant-guid>"
$appId  = "<app-registration-client-id>"
$secret = ConvertTo-SecureString "<client-secret>" -AsPlainText -Force
$cred   = New-Object System.Management.Automation.PSCredential($appId, $secret)
Connect-PowerBIServiceAccount -ServicePrincipal -Credential $cred -TenantId $tenant
```
> The service-principal path requires the tenant setting **"Allow service principals to use Power BI APIs"** (Admin portal → Developer settings). This is the unattended-automation enabler — flag it for GTF's admin.

### Step 2 — CREATE a workspace (the "new brand" object)
```powershell
$ws = New-PowerBIWorkspace -Name "POC-Brand-Carvel"
$ws.Id
```
REST equivalent: `POST https://api.powerbi.com/v1.0/myorg/groups` with body `{ "name": "POC-Brand-Carvel" }`.
**Screenshot:** the new workspace appearing in the Power BI Service.

### Step 3 — PUBLISH a dataset + report (Import a .pbix)
```powershell
New-PowerBIReport -Path "C:\poc\BrandSummary.pbix" -Name "Brand Summary" -WorkspaceId $ws.Id -ConflictAction CreateOrOverwrite
```
This single call creates **both** a dataset and a report. REST equivalent: `POST /groups/{groupId}/imports?datasetDisplayName=...` (multipart upload).

### Step 4 — READ the inventory (CRUD = Read)
```powershell
Get-PowerBIWorkspace -All | Select Id, Name | Format-Table
Get-PowerBIDataset  -WorkspaceId $ws.Id | Select Id, Name
Get-PowerBIReport   -WorkspaceId $ws.Id | Select Id, Name, DatasetId
```
REST: `GET /groups`, `GET /groups/{groupId}/datasets`, `GET /groups/{groupId}/reports`.

### Step 5 — UPDATE: add a franchise user + clone a report
**Add a user (workspace access):**
```powershell
Add-PowerBIWorkspaceUser -Id $ws.Id -UserPrincipalName "franchise.user@gtf.com" -AccessRight Viewer
Get-PowerBIWorkspaceUser -Id $ws.Id
```
REST: `POST /groups/{groupId}/users` with `{ "identifier":"franchise.user@gtf.com", "principalType":"User", "groupUserAccessRight":"Viewer" }`.

**Clone the report (templating-adjacent — covered deeper in S.No 107):**
```powershell
$rep = Get-PowerBIReport -WorkspaceId $ws.Id | Select-Object -First 1
$body = @{ name = "Brand Summary - Clone" } | ConvertTo-Json
Invoke-PowerBIRestMethod -Method Post -Url "groups/$($ws.Id)/reports/$($rep.Id)/Clone" -Body $body
```
Official op: **Reports - Clone Report In Group** (`POST /groups/{groupId}/reports/{reportId}/Clone`).

### Step 6 — DELETE (tear down)
```powershell
Remove-PowerBIWorkspaceUser -Id $ws.Id -UserPrincipalName "franchise.user@gtf.com"
Invoke-PowerBIRestMethod -Method Delete -Url "groups/$($ws.Id)/reports/$($rep.Id)"
Remove-PowerBIWorkspace -Id $ws.Id
```
**Screenshot:** the workspace gone from the Service.

### What to document
- All four object types (workspace, dataset, report, user) created/read/updated/deleted via API — yes/no per object.
- Whether service-principal (unattended) auth worked, or if the tenant switch blocked it.
- Cmdlet vs raw REST: cmdlets cover most; some ops (Clone, UpdateParameters) need `Invoke-PowerBIRestMethod`.

---

## Tableau — Full CRUD via Tableau Server Client (Python)

### Step 1 — Authenticate with a Personal Access Token
```python
import tableauserverclient as TSC

server_url = "https://<your-site>.online.tableau.com"   # or Tableau Server URL
tableau_auth = TSC.PersonalAccessTokenAuth(
    token_name="poc-token",
    personal_access_token="<token-secret>",
    site_id="<site-content-url>"        # the part after /site/ in the URL; "" for default
)
server = TSC.Server(server_url, use_server_version=True)
server.auth.sign_in(tableau_auth)
print("Signed in. Site:", server.site_id)
```
REST equivalent: `POST /api/<ver>/auth/signin` with PAT credentials → returns auth token + site id.

### Step 2 — CREATE a project (the "new brand" object)
```python
new_project = TSC.ProjectItem(name="POC-Brand-Carvel", description="POC brand project")
new_project = server.projects.create(new_project)
print("Created project:", new_project.id)
```
REST: `POST /api/<ver>/sites/{siteId}/projects`.

### Step 3 — PUBLISH a workbook (+ its data source)
```python
wb = TSC.WorkbookItem(project_id=new_project.id, name="Brand Summary")
wb = server.workbooks.publish(wb, "C:/poc/BrandSummary.twbx",
                              mode=TSC.Server.PublishMode.Overwrite)
print("Published workbook:", wb.id)
```
REST: `POST /api/<ver>/sites/{siteId}/workbooks` (multipart).

### Step 4 — READ the inventory
```python
print([ (p.id, p.name) for p in TSC.Pager(server.projects) ])
print([ (w.id, w.name) for w in TSC.Pager(server.workbooks) ])
print([ (d.id, d.name) for d in TSC.Pager(server.datasources) ])
print([ (u.id, u.name) for u in TSC.Pager(server.users) ])
```
REST: `GET .../projects`, `.../workbooks`, `.../datasources`, `.../users`.

### Step 5 — UPDATE: add a franchise user + assign to a group
```python
# Add the user to the site as a Viewer
new_user = TSC.UserItem(name="franchise.user@gtf.com", site_role="Viewer")
new_user = server.users.add(new_user)

# Create a group and add the user (group-based access = how GTF should scale franchises)
grp = server.groups.create(TSC.GroupItem("Carvel-Franchisees"))
server.groups.add_user(grp, new_user.id)
print("Added user", new_user.id, "to group", grp.id)
```
REST: `POST .../users`, `POST .../groups`, `PUT .../groups/{groupId}/users`.

### Step 6 — DELETE (tear down)
```python
server.workbooks.delete(wb.id)
server.users.remove(new_user.id)
server.groups.delete(grp.id)
server.projects.delete(new_project.id)
server.auth.sign_out()
```
**Screenshot:** the project gone from the Tableau site.

### What to document
- All four object types created/read/updated/deleted via TSC — yes/no per object.
- PAT auth experience (no password in script — good for automation).
- Note: TSC is the **official, supported** Python wrapper; raw REST also available for anything TSC doesn't cover.

---

## Side-by-Side Findings Summary

| Capability | Power BI | Tableau |
|---|---|---|
| **Workspace/Project CRUD** | Full — `*-PowerBIWorkspace` cmdlets + REST `/groups` | Full — `server.projects` + REST `/projects` |
| **Dataset/Data source CRUD** | Full — import/publish, list, delete, UpdateParameters | Full — publish, list, delete, refresh |
| **Report/Workbook CRUD** | Full — publish, list, Clone, Rebind, delete, ExportTo | Full — publish, list, download, delete |
| **User/Group management** | Full — add/remove workspace users; Entra-backed | Full — add users, create groups, assign roles |
| **Auth model** | Entra OAuth2 + **service principal** (unattended) | **Personal Access Token** + username/password |
| **Official client library** | PowerShell `MicrosoftPowerBIMgmt`; .NET SDK | **Python `tableauserverclient` (TSC)** — clean, supported |
| **Unattended automation** | Strong — service principals, Azure-native, CI/CD friendly | Strong — PAT-based, no UI login needed |
| **Admin/governance APIs** | Scanner API (full tenant metadata) | Metadata GraphQL API + REST |
| **Winner** | **Tie** — both cover full CRUD; PBI edges Azure-native unattended auth, Tableau edges developer ergonomics (TSC) | — |

---

## Key talking point for client call
> "Both Power BI and Tableau can be fully driven by REST API — create a brand workspace, publish a dataset and report, provision franchise users into groups, and tear it all down, with zero manual clicks. This matters for GTF because onboarding hundreds of franchises by hand doesn't scale. Power BI's advantage is **service-principal authentication** — unattended automation that lives natively in your Entra/Azure environment, the same identity model your 'Power BI robots' already use. Tableau's advantage is the **official Python client (TSC)**, which is the cleanest developer experience of the two. Functionally it's a tie — neither tool will block GTF's automation needs."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (Power BI) for S.No 101:**
> Full CRUD via REST API (`api.powerbi.com/v1.0/myorg`) on workspaces (`/groups`), datasets, reports, and users — plus PowerShell cmdlets (`MicrosoftPowerBIMgmt`) and a .NET SDK. Service-principal (Entra app-registration) auth enables unattended automation; tenant switch "Allow service principals to use Power BI APIs" must be on. Extra ops: Clone, Rebind, UpdateParameters, ExportTo. Scanner API for tenant-wide metadata governance.

**Column G (Tableau) for S.No 101:**
> Full CRUD via REST API (`/api/<ver>/sites/{siteId}/...`) on projects, data sources, workbooks, users, and groups — wrapped by the official Python client `tableauserverclient` (TSC). Personal Access Token auth is clean for scripted/unattended use (no stored password). Metadata GraphQL API for governance/lineage. tabcmd CLI also available.

**Column H (Power BI Proof) for S.No 101:**
> Official documentation:
> https://learn.microsoft.com/en-us/rest/api/power-bi/
> https://learn.microsoft.com/en-us/powershell/power-bi/overview
> https://learn.microsoft.com/en-us/rest/api/power-bi/reports/clone-report-in-group

**Column I (Tableau Proof) for S.No 101:**
> Official documentation:
> https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm
> https://tableau.github.io/server-client-python/
> https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_workbooks_and_views.htm

**Column J (Findings) for S.No 101:**
> Tie — both expose mature, fully documented REST APIs covering CRUD on workspaces/projects, datasets/data sources, reports/workbooks, and users/groups. Power BI edges ahead for **Azure-native unattended automation** (service principals + Entra), aligning with GTF's existing automation identity model; Tableau edges ahead for **developer ergonomics** via the official TSC Python library. Neither blocks GTF's franchise-provisioning automation. Advantage: TIE — PBI for service-principal automation, Tableau for the cleaner client library.

**Column K (Status) for S.No 101:** `COMPLETED`
