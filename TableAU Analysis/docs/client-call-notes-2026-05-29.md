# Client Call Notes — GTF Tableau vs Power BI Evaluation

**Date:** 29 May 2026 · **Duration:** 36m 48s · **Type:** Approach review + client requirement alignment

> Source: `docs/Tableau evaluation - Discussion .docx` (meeting transcript). This file distills the **critical client inputs and directives** for future context. Pairs with [`powerBI-vs-tableau-requirements.md`](powerBI-vs-tableau-requirements.md) (formal requirements) and [`project-context.md`](project-context.md) (architecture).

---

## Participants

**Client (GTF / GoTo Foods):**
- **Narsimha Daram** — owns the BI area; primary point of contact; has an expert internal team.
- **John Kister** — Senior Director, owns this area; the expert who built the current system over 8–10 years. Will advise which reports to prioritize. (Was not on this call.)
- **Ni / Nia** — Power BI developer; will provide Power BI copies, data, and volume numbers.
- **Jeff** — Architect; can explain the semantic-layer design and help with AtScale access.

**Psiog:** Sridhar Vetrivel, Prasanna Venkatesh, Aditya (presenter).

---

## ⭐ Critical Scope Directives (these change how we work)

1. **Do HIGH priority items only.** Explicitly: *"only do high, don't even do medium and low… I don't want to make this very large exercise."* Even if time permits, do not do other priorities. (Example given: Snowflake connectivity was Low — *"will never happen, we continue being in Databricks"*.)

2. **Do NOT rebuild or POC Power BI.** GTF has a working Power BI system of 8–10 years. *"You don't have to spend any time on Power BI because we know exactly how it works."* Reuse their existing system — Ni will give a **copy in a test location** (don't touch production). For Power BI the only question is *"does it support X? If yes, show a demo/POC of how it works."*

3. **Run the POC in GTF's environment**, not ours (environment address was provided).

4. **Time intelligence / performance is already proven on Tableau — do NOT re-test it.** *"We don't worry about time intelligence because we already tested with Tableau, we know it's fast."* What they actually want validated is the **foundation**: authentication, authorization, access, and visibility (RLS) on Tableau.

5. **Don't focus on data volumes.** *"Tableau can handle it."* Not important for the evaluation (they already run Power BI; if they switch they know Tableau handles volume). Psiog flagged volumes still matter slightly for **viz/UX differences**, not performance.

---

## Company & Current-State Background

- GTF is a **restaurant company**; customers are **franchises** — thousands across multiple brands. Franchises range from owning **1 store to hundreds of stores**.
- Current stack: **everything Power BI**, backed by **SQL Server + SSAS + SSIS**, in place 8–10 years. **~50–100 reports.**
- User types: internal **corporate/executive** (revenue, trending), internal **analysts** (catering, online, store), and external **franchises** (reports delivered via **email + Power BI access**).
- **Catering** is a **growth area**. Channels: catering, online, store.
- Business also connects via **Excel**.
- **Data exports = "Power BI bots/robots"** — the automation that filters and emails data to franchisees.

---

## The Foundation = the Real Ask (Auth / Authz / RLS)

The whole system foundation is built around **how internal + external users are authenticated and authorized**:

- Authorize not only on **brands** (e.g., Moe's, Carvel) but also on the **specific stores** a franchise owns.
- **Hierarchy within the franchise side**: branch manager / store manager / supervisor each see a different scope. RLS is built into the foundation.
- **Three Active Directories today:**
  - **Okta** — external franchises (separate system)
  - **Internal on-prem AD**
  - **Azure AD** — the newest one
  - A **3-way sync runs daily.**
- **For the POC: connect ONLY to Azure Active Directory** (assume everything is in one AD for the POC).
- **Long-term IDP = Azure** (migrating on-prem → Azure; anything new — web apps, mobile, data science — connects to Azure AD).
- **Caveat:** GTF is *also* evaluating **AWS/Amazon** (better AI capabilities). Azure → AWS migration is possible in future, which could change the IDP again. Don't hard-assume Azure permanence.

---

## Architecture & Migration

- New **"data platform" on Databricks** is being built; migrating off SQL Server + SSAS → **AtScale** as the semantic layer.
- **AtScale rationale:** modern, open — serves not just reporting but **Excel pivots, Python, and other AI tools**. Supports big-data and near-real-time demand. (Microsoft stack doesn't follow this open approach.)
- Timeline: Databricks/data platform **~3 years** in progress; **last ~1 year** cutting over legacy → new.
- Domains already built in the new system: **catering, gift cards**, and a couple of others.

### The Performance Problem (the trigger for this evaluation)

- The Power BI issue is **specifically with time intelligence** (current year vs prior year trend, shown side by side). Takes **a couple of minutes** instead of ~30 seconds.
- **Design principle:** ALL metrics/measures live in the **semantic layer (AtScale)** — *"we don't want anything in Power BI or Tableau to be smart or do any logic."* The BI tool must be a **thin client**. The slowness appears on the **visualization side** when crossing current/prior-year metrics.
- **Root cause = the combination Power BI ↔ AtScale**, not one tool. Power BI generates **huge multi-page SQL** sent to AtScale; no indexing/partitioning fixes it. AtScale is working on **in-memory + aggregation** improvements.
- **The same time-intelligence works fast via Excel → AtScale and Tableau → AtScale. Only Power BI → AtScale is slow.**
- Tried and failed: **Power BI Import mode**, **InfoRiver** (3rd-party front-end pagination). InfoRiver only paginates (shows 1k–10k of millions) — but enterprise reporting *should never* surface millions of rows, so volume isn't the real issue; even a low-volume time-intelligence report is slow.
- Of ~10 reports built on Power BI + AtScale, **only 1 shows the issue**, but **many other reports need time intelligence** → hence building Tableau readiness in parallel. If AtScale's fix lands, they *might* stay on Power BI; if not, the migration is at risk.

---

## Self-Service — Definition (very important to client)

New executive leaders (ex-**Amazon**, ex-**Albertsons** retail) are **very into self-service**, but each defines it differently:

- (a) **Data arrives in their email inbox** daily.
- (b) A **UI (Power BI/Tableau) with standard reports**, where teams can build **custom reports** and share with the enterprise.
- (c) **AI-driven LLM** — ask questions in natural language, get answers.

> **Unifying definition:** *"they don't want to talk to people to get any data/reporting needs."* No human help required = self-service.

---

## Vision Themes (the 6 anchors of the evaluation)

1. **Self-service** (very important)
2. **AI readiness / modern capabilities** (preparing for the AI era)
3. **Insight-driven** — show trends/insights, not data dumps the business must interpret
4. **Time intelligence performance**
5. **Internal + external stakeholder handling**
6. **Role-level security (RLS)** — multiple stakeholder types makes this critical

### Insight-driven nuance
- GTF reporting = **corporate + franchise reporting** (trends and metrics). **Not** deep insight models.
- **Deep models** (marketing mix model, digital sales channel/funnel) are **NOT GTF's to build** — specialist vendors do those; GTF just gives them data.
- **Maturity curve:** immature orgs want "data everywhere" (lists/tables); mature orgs want insights (trends, color, visual story). The **insight-driven catering POC** is meant as a starting point to *"think differently."*

---

## Insight-Driven Catering POC (Psiog initiative)

- Psiog is building a **more insight-driven version of the catering report** (the report that had the perf issue), applying patterns from other client environments.
- **6 candidate reports identified; 1 already built.**
- **Action:** share a **screenshot first** with **John Kister**, who will recommend **which report to build next** (saves time, picks the right ones). Don't build more until he weighs in.

---

## Approach Validation (client feedback)

- Client validated the approach: 20 categories, high/medium/low criticality grading, GTF-context mapping, POC-vs-documentation confidence. *"Very professionally done, very detailed than what we expected."*
- Their own requirement list maps into the **11 High categories** — all client requirements land in **High**. Email/export reports confirmed covered.
- Evaluation tracked in Excel: **~200 subcategories (~10 per category)**, prioritized High / Medium / Low / Not-needed.
- **Cross-filtering demo finding:** Power BI = **zero-setup** cross-filtering + drill-through; Tableau = a **lag** and needs a **manual workaround** (source–target pair mapping for drill-through; manual filter for cross-filter). Not fully blocked. The workaround is **end-user-side**, not implementation-side.

---

## Dependencies / Blockers

1. **AtScale access** — no free tier. Need access **inside the GTF environment** to connect Tableau → AtScale. Client will help provide a license. Note: when their dev connected, she used a **Tableau license, not an AtScale license** — our connection method may differ. Contacts: **Prasanna, Jeff, Ni.**
2. **Volume estimates** — client says **don't focus on volumes** (Tableau handles them; not decision-relevant). Ni/Prasanna can supply numbers if needed.

---

## Timeline & Commercial

- **Evaluation:** ~2 weeks to wrap (faster now that it's High-only).
- **Tool selection decision:** next **3–4 months** (≈ Q3 2026).
- **Coexistence:** Power BI licenses valid through **end of 2026, into 2027**. Tableau, if adopted, only covers **some domains** — Power BI remains for domains still on SSAS.
- **Next step:** client to share **2–3 morning (Eastern Time) slots**, ~week of 8 June 2026, for a detailed 1-hour call with **John Kister + team**.

### 🔒 Confidential licensing numbers (client: *do not share with Tableau or anybody*)
- **Power BI:** ~**$50,000/year for unlimited users**. Microsoft is moving "unlimited" → **Fabric** model, so this will change in 2027.
- **Tableau (via Salesforce):** **3 tiers** — basic / middle / top (all-AI, **>$100k–150k**). Quoted count ≈ **$75,000** (basic). Numbers **don't match Power BI yet.**
- Scope assumption: thousands of franchises, but **~500 franchises actually use reports** (can scale later).

---

## Action Items (Psiog)

- [ ] **Refocus the evaluation on HIGH priority items only** — pause Medium/Low/not-needed.
- [ ] **Stop building Power BI POCs** — get a Power BI copy/test location from **Ni**; reuse the existing system; only demo "does it support X" where needed.
- [ ] **Validate the foundation on Tableau**: Azure-AD auth, brand+store authorization, franchise hierarchy RLS, email/export delivery ("robots" equivalent).
- [ ] **Obtain AtScale access** in the GTF environment (via Prasanna/Jeff/Ni).
- [ ] **Share the catering insight-POC screenshot with John Kister**; get his pick for the next report before building more.
- [ ] **POC to run in GTF's environment.**
- [ ] Prepare for the detailed 1-hour follow-up call (client to send ET slots ~week of 8 June 2026).
