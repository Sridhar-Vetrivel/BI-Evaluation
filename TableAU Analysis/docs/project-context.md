# Project Context: Tableau vs Power BI Evaluation for GTF

## Project Purpose
A **discovery and evaluation exercise for GTF** to determine whether **Tableau** can replace or coexist with **Power BI** as the enterprise BI tool, given a recent architectural shift to an AtScale-based semantic layer.

---

## Architectural Shift (the trigger for this evaluation)

**Old Architecture:**
```text
EDW --> SSIS --> SSAS --> Power BI
```

**New Architecture:**
```text
EDW --> Databricks + ADF --> AtScale --> Power BI / Tableau
```

The introduction of **AtScale as the analytical/semantic layer** is the pivotal change — it decouples the BI tool from the underlying data model, which is what makes Tableau a viable contender alongside Power BI.

**Early signal:** Initial performance tests (summary + detail reports) on Tableau via AtScale already outperformed Power BI.

---

## Two Layers of Evaluation Criteria

### Layer 1 — Client-stated must-haves (9 items)

1. **Azure AD / Entra ID connectivity** — SSO, MFA, auth/authz
2. **Gateways & refresh architecture** — scheduling, live connections, bridge setup
3. **Power BI "Apps" equivalent** — Projects / Sites / Collections in Tableau
4. **Row-Level Security (RLS)** — franchise-level, dynamic, role-based
5. **Bookmarks equivalent** — views, navigation, filter state management
6. **Visualizations** — interactive (params/actions/what-if), many-filter, pretty/executive, P&L matrix
7. **Large-row reports** (e.g., catering detail) — performance, pagination, export
8. **Power BI "Robots" equivalent** — subscriptions, REST APIs, franchise-filtered email delivery
9. **SSAS / Azure Analysis Services connectivity** — semantic models, live cube

### Layer 2 — Broader enterprise BI lens (20 categories)

1. Data Connectivity & Integration
2. Visualization & UX
3. Governance, Security & Compliance
4. Performance & Scalability
5. Collaboration & Sharing
6. Licensing & TCO
7. AI/ML & Advanced Analytics
8. Deployment & IT Operations
9. Data Modeling & Semantic Layer
10. Embedded Analytics
11. Extensibility & Developer Ecosystem
12. Vendor Maturity & Ecosystem
13. Mobile & Accessibility
14. Interoperability & Standards
15. Self-Service & Authoring Experience
16. Report Consumption & Alerting
17. Data Lineage & Audit Trail
18. Version Control & CI/CD for BI
19. Real-time & Streaming Analytics
20. Localization & Internationalization

---

## Implementation Workflow

1. **Trim the 20 categories** — confirm which evaluation criteria are actually needed for the AtScale → Tableau/Power BI use case
2. **Add a reasoning column** in the evaluation Excel, tying each criterion back to the use case
3. **Run the evaluation**
4. **Back claims with POCs + official documentation** as proofs
5. **Categorize findings** as high vs low confidence (with human review)
6. **Deepen research on low-confidence areas**

---

## Domain Hints

- "Franchise-level filtering" + "catering detail report" suggests a **food service / hospitality / franchised QSR** business.
- **P&L matrix reporting** is a non-trivial requirement — Power BI's matrix visual is famously strong here; Tableau has historically been weaker. Worth flagging early.
- **"Power BI Robots"** is non-standard terminology — likely refers to Power Automate flows or an internal automation framework that filters and emails reports per franchisee.

---

## Early Observations / Flags

- The 20 categories overlap heavily with the 9 client requirements — Step 1 (trimming) should **consolidate**, not just filter.
- Some categories (Localization, Real-time streaming, Embedded Analytics) may not apply at all to internal franchise reporting — worth confirming with the client before researching.
- **AtScale is doing a lot of heavy lifting** in the new architecture. Several "BI tool" capabilities (semantic modeling, RLS, time intelligence, certified metrics) may actually be answered at the AtScale layer, not at Tableau/Power BI. This reframes the evaluation:
  > It's less "which BI tool is better" and more "which BI tool is the better **thin client** on top of AtScale."

---

## Strategic Objective

Evaluate whether Tableau can support enterprise BI requirements **alongside or instead of** Power BI, using the new AtScale semantic layer architecture.
