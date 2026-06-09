
GoTo Foods
Catering Analytics Transformation
From Raw Data Dump  →  Insight-Driven Decision Support

| Based on Existing Data Model No new data sources required | Audience FBCs, Brand Leaders RVPs, Franchisees | Purpose Diagnose. Prioritize. Act. Track outcomes. |
| --- | --- | --- |


Prepared for GoTo Foods — Catering Reporting Team

# Part 1 — What the Current Report Does (and Doesn't Do)

| THE CURRENT STATE: Data Without Decisions |
| --- |


The existing Catering Reporting suite in Power BI consists of 6 pages. Each page serves a purpose — but all of them stop at showing numbers. None of them complete the analytical loop by answering: So what? Who needs to act? What should they do?

| Page | What It Shows | Primary User | Core Limitation | Hidden Signal Being Missed | What User Currently Does |
| --- | --- | --- | --- | --- | --- |
| Catering Summary | Brand-level 1P/3P sales, orders, check — Period + YTD | Brand Leaders, RVPs | No target vs actual. No channel mix signal. No store-level drill. | 1P declining while total looks healthy — 3P masking a margin problem | Manually calculate % split in Excel |
| Catering Trends | Line chart: CY vs PY weekly total catering by brand | FBCs, Brand Managers | Total sales only — no 1P vs 3P trend. No target line. One chart only. | Is 1P share growing or eroding over time? Cannot tell. | Request custom chart from analyst |
| Catering Summary 2.0 | Same as Summary — adds comp store YoY alongside system YoY | Leadership, Brand Directors | Two tables with no annotation. No explanation of why comp differs from system. | Massive negative comps in FY26 P01 go unexplained — is this a data issue or real decline? | Call the data team to ask |
| Catering Detail | Franchisee-level 1P/3P breakdown — rolling 13 weeks | FBCs (primary) | No ranking, no flagging of outliers. FBC must scan 30+ rows manually. | David Jones -60% in 1P is buried in row 10. No alert, no highlight. | Sort by column manually, hope not to miss anyone |
| Catering Export | Raw unit-level flat table with all metrics — for export | Analysts, FBCs | Exists because the other pages aren't analytical enough. A workaround. | This page existing is itself a symptom of the report's failure. | Export to Excel. Build pivot. Re-analyze. Repeat weekly. |
| Catering Marketing Spend | Transaction-level incentive tracking: Delivery Fee, PPP, EZ Rewards | Marketing Teams | No ROI calculation. No comparison of spend vs incremental orders. | Is PPP discount driving new orders or just discounting existing ones? | Assume spend is effective. No validation. |


# Part 2 — The Redesigned Report (Using Existing Data Model Only)

Every insight and visual below can be built entirely from the existing 13 tables in the UDI data model. No new data sources. No new pipelines. Only smarter use of what already exists.

| PAGE 1 — Catering Health Scorecard  |  Audience: Brand Leaders, RVPs |
| --- |


PURPOSE: Replace the current summary tables with a decision-ready executive view. Answer the question: Is catering healthy across the system this period?

| Visual / Component | What It Shows | Fields From Model | What Decision It Enables | Why Better Than Current |
| --- | --- | --- | --- | --- |
| KPI Cards (5 cards, top row) | Total Catering Sales (CY vs PY), 1P Share %, 3P Share %, Avg Check, Comp % | Catering: FirstPartyNetSales, ThirdPartyNetSales, FirstPartyTraffic, ThirdPartyTraffic | Immediate pulse check — is the system growing? Is 1P holding share? | Current shows raw $; no instant read on health or channel mix |
| 1P vs 3P Revenue Mix — Stacked Bar by Brand | What % of each brand's catering comes from 1P vs 3P | Catering: FirstPartyNetSales, ThirdPartyNetSales grouped by Brand | Identify which brands are platform-dependent (margin risk) vs self-sufficient | Completely absent from current report |
| Catering vs Total Sales — Penetration % by Brand | Catering sales as % of total reported sales per brand | Catering: NetSales vs Reported Sales: NetSalesCY — joined on BrandSequence | Which brands have catering as a major revenue stream vs incidental? | Current report treats catering in isolation — no context vs total sales |
| Target Attainment — Bullet Chart by Brand | Actual catering sales vs OffPremiseTarget — showing gap or surplus | Catering: FirstPartyNetSales+ThirdPartyNetSales vs Brand Targets: OffPremiseTarget | Which brands are on plan? Where is GoTo Foods at risk of missing the year? | No target tracking anywhere in current report |
| Brand Ranking Table — Sortable | 7 brands ranked by: Sales, Comp%, 1P Share, Check Size, Target Gap — user selects sort column | Catering + Brand Targets + Brand table | Identify best/worst brand instantly. Spot patterns across dimensions. | Current has no ranking — all brands are equal rows with no priority signal |


| PAGE 2 — Channel Intelligence  |  Audience: Brand Managers, FBCs |
| --- |


PURPOSE: Surface the 1P vs 3P story with full analytical depth. This is the margin story hiding in plain sight.

| Visual / Component | What It Shows | Fields From Model | What Decision It Enables | Why Better Than Current |
| --- | --- | --- | --- | --- |
| 1P Share Trend — Line Chart over Time | % of catering from 1P over rolling weeks — CY vs PY. Are we growing or losing 1P share? | Catering: FirstPartyNetSales / (FirstPartyNetSales + ThirdPartyNetSales) by CalendarDate | Detect a systematic channel shift before it becomes a margin crisis | Current Trends page shows only total. 1P/3P split trend is invisible. |
| Average Check Comparison — 1P vs 3P by Brand | Average order value: 1P orders vs 3P orders. Which channel drives higher-value orders? | Catering: FirstPartyNetSales/FirstPartyTraffic vs ThirdPartyNetSales/ThirdPartyTraffic | Justify investment in 1P channel capability. Set realistic 1P acquisition targets. | Current shows check for each channel but no visual comparison side-by-side |
| 3P Dependency Risk Matrix | Scatter: X = 3P Share %, Y = Sales Growth. Quadrants: Healthy / Platform-Dependent / Declining / At Risk | Catering: ThirdPartyNetSales%, YoY% by Unit — joined with Unit table (Franchisee, Region) | Identify stores that are growing only because of 3P — a dependency that could reverse if platform changes fees | No risk framing exists anywhere in current report |
| Digital Sales Overlap — 1P Catering vs 1P Digital | How much of 1P catering overlaps with digital ordering? Is the digital channel supporting catering growth? | Catering: FirstPartyNetSales + Digital Sales: FirstPartyNetSales — joined by SBRSequence + CalendarDate | Understand if digital investment (app/web ordering) is actually converting into catering revenue | Catering and Digital Sales tables are never shown together in current report |


| PAGE 3 — FBC Action Board  |  Audience: Franchise Business Consultants |
| --- |


PURPOSE: Replace the current Catering Detail table (30+ rows, no prioritization) with a tool that tells the FBC exactly who needs their attention today and why.

| Visual / Component | What It Shows | Fields From Model | What Decision It Enables | Why Better Than Current |
| --- | --- | --- | --- | --- |
| Franchisee Alert Cards — Auto-flagged | Cards for franchisees meeting alert criteria: 1P down >20%, 3P share >70%, Check declining >10%. Color coded Red/Amber/Green. | Catering: FirstPartyNetSales YoY%, ThirdPartyNetSales%, Check YoY% — filtered by Unit.FranchiseBusinessConsultant | FBC opens the report and immediately sees who needs a call today — no manual scanning | Current detail page: 30+ equal rows. David Jones -60% is buried with no flag. |
| Franchisee Performance Quadrant | Scatter: X = 1P Catering Growth%, Y = Total Catering Growth%. Quadrants: Stars / Platform-only growers / Decliners / Turnaround | Catering: FirstPartyNetSales YoY% vs (FirstPartyNetSales+ThirdPartyNetSales) YoY% by Franchisee | FBC can see portfolio of franchisees in one glance — who to celebrate, who to coach, who to escalate | No portfolio view exists. Only rows of numbers. |
| Guest Satisfaction Overlay | For each flagged franchisee: catering sales trend + guest satisfaction score (Quality, Accuracy, Speed). Are service issues driving catering decline? | Catering + Guest Satisfaction: TopScores/Surveys ratio, SpeedTopScores, AccuracyTopScores — joined by SBRSequence | Diagnose root cause: is it a catering capability problem or a broader service quality problem? | Guest Satisfaction table exists in model but is never shown alongside catering data |
| Field Audit + Food Safety Flag | Stores with catering decline AND low field audit score OR food safety criticals — double-risk flag | Catering YoY% + Field Audits: FieldAuditScore, FieldAuditFailures + Food Safety: FoodSafetyCriticals — joined by SBRSequence | Prioritize FBC visits: store with catering decline + audit failures is an escalation candidate, not just a coaching call | Field Audits and Food Safety tables never combined with catering in current report |


| PAGE 4 — Catering Trends (Rebuilt)  |  Audience: Brand Managers, FBCs |
| --- |


PURPOSE: Keep the only good visual page — but make it 5x more informative by adding channel split, target line, and annotation capability.

| Visual / Component | What It Shows | Fields From Model | What Decision It Enables | Why Better Than Current |
| --- | --- | --- | --- | --- |
| 3-Line Trend Chart: Total / 1P / 3P | Weekly: Total catering (red), 1P only (blue), 3P only (dashed). CY vs PY for each. | Catering: FirstPartyNetSales, ThirdPartyNetSales by CalendarDate — rolling weekly | Immediately visible: is 3P growing while 1P flat? Is total growth healthy or hollow? | Current shows only total. Channel split trend is invisible. |
| Target Pace Line Overlay | Expected cumulative catering sales by week (paced from OffPremiseTarget) — overlaid on actual trend | Brand Targets: OffPremiseTarget divided by periods — overlaid on Catering cumulative line | Detect mid-year underperformance while there is still time to course-correct | No target line anywhere in current trends page |
| Promo / Event Annotation Layer | Vertical markers on the trend line showing when catering promotions/incentives were active (from Marketing Spend data) | Catering Marketing Spend: date range of PPP / EZ Rewards activity by brand | Correlate promotions with sales spikes/dips — measure whether campaigns actually move the needle | Marketing Spend page is completely disconnected from Trends page |
| Seasonality Index Panel | Average weekly catering sales by period (multi-year) — shows expected seasonal pattern as a baseline band on the trend chart | Catering: average CalendarDate weekly sales aggregated across 2+ fiscal years in model | Distinguish genuine growth from seasonal lift — avoid false confidence in summer/holiday spikes | No seasonality baseline exists in current report |


| PAGE 5 — Marketing ROI View  |  Audience: Brand Marketing Teams |
| --- |


PURPOSE: Transform the Catering Marketing Spend page from a transaction list into an ROI accountability view.

| Visual / Component | What It Shows | Fields From Model | What Decision It Enables | Why Better Than Current |
| --- | --- | --- | --- | --- |
| Incentive Spend vs Sales Lift — Bar Chart | Total PPP + Delivery Fee + EZ Rewards cost per store vs catering sales in same period. Side-by-side comparison. | Catering Marketing Spend: Subtotal, DeliveryFee, PPP, EZRewards vs Catering: FirstPartyNetSales — joined by Unit + date | Which stores generate strong return on incentive investment vs which are using discounts to maintain flat sales? | Current page is a pure transaction list — no ROI calculation whatsoever |
| Cost per Order by Incentive Type | Average spend per catering order broken down: Delivery Fee cost, PPP discount cost, Rewards cost | Catering Marketing Spend: PPP/Orders, DeliveryFee/Orders, EZRewards/Orders by Brand | Optimize incentive mix — if delivery fee waiver drives more incremental orders than PPP, reallocate budget | No per-order cost breakdown anywhere in current report |
| Loyalty + Catering Correlation | Stores with high loyalty enrollment vs catering performance. Do loyal customers cater more? | Loyalty: Enrollments, LoyaltySales vs Catering: FirstPartyNetSales — joined by SBRSequence + CalendarDate | If loyalty-enrolled customers drive more catering, accelerate enrollment programs at low-catering stores | Loyalty and Catering tables never shown together in current report |


# Part 3 — KPIs & Metrics: What the Existing Model Can Calculate Today

All of the following KPIs can be built as DAX measures in Power BI using the existing 13 tables. No new data required.

| CORE CATERING KPIs — From the Catering Table |
| --- |


| KPI / Metric | DAX Formula (from existing model) | Source Table | Audience | Why It Matters |
| --- | --- | --- | --- | --- |
| Total Catering Sales | SUM(Catering[FirstPartyNetSales]) + SUM(Catering[ThirdPartyNetSales]) | Catering | All users | Baseline performance number |
| 1P Revenue Share % | DIVIDE(SUM([FirstPartyNetSales]), [Total Catering Sales]) | Catering | Brand Leaders, FBCs | Channel health & margin quality signal |
| 3P Dependency Index | DIVIDE(SUM([ThirdPartyNetSales]), [Total Catering Sales]) | Catering | Brand Managers, RVPs | Platform risk — higher = more margin at risk |
| Catering Comp % | DIVIDE([Total Catering Sales CY] - [Total Catering Sales PY], [Total Catering Sales PY]) | Catering [Comp='Y'] | Leadership | True same-store growth — strips new openings |
| 1P Average Check | DIVIDE(SUM([FirstPartyNetSales]), SUM([FirstPartyTraffic])) | Catering | FBCs, Brand Mgrs | Order value quality — higher = corporate clients |
| 3P Average Check | DIVIDE(SUM([ThirdPartyNetSales]), SUM([ThirdPartyTraffic])) | Catering | FBCs, Brand Mgrs | Compare to 1P — which channel drives bigger orders? |
| Catering Traffic YoY% | DIVIDE([Total Traffic CY] - [Total Traffic PY], [Total Traffic PY]) | Catering | FBCs | Volume momentum — growing orders or just bigger orders? |
| 1P Traffic Share % | DIVIDE(SUM([FirstPartyTraffic]), SUM([FirstPartyTraffic]) + SUM([ThirdPartyTraffic])) | Catering | Brand Leaders | Is order volume shifting to platform? |


| CROSS-TABLE KPIs — Unlocked by Joining Existing Tables |
| --- |


| KPI / Metric | DAX Formula (from existing model) | Source Table | Audience | Why It Matters |
| --- | --- | --- | --- | --- |
| Catering Penetration % | DIVIDE([Total Catering Sales], SUM(Reported Sales[NetSalesCY])) | Catering + Reported Sales | Brand Directors, RVPs | How big is catering as a % of total business? |
| Target Attainment % | DIVIDE([Total Catering Sales], SUM('Brand Targets'[OffPremiseTarget])) | Catering + Brand Targets | Leadership, Brand Dirs | Are we on plan? Core accountability metric |
| Catering vs Discount Rate | DIVIDE(SUM(Reported Sales[DiscountsCY]), SUM(Reported Sales[CateringCY])) | Reported Sales | Marketing, FBCs | Are we buying catering revenue through discounts? |
| Guest Score at Catering Decliners | AVG(Guest Satisfaction[TopScores/Surveys]) FILTER stores where Catering YoY < -10% | Catering + Guest Satisfaction | FBCs, Operations | Is service quality driving catering loss? |
| Loyalty → Catering Conversion | DIVIDE([CateringCY], SUM(Loyalty[LoyaltyEarnableSales])) | Reported Sales + Loyalty | Marketing | Do loyalty-enrolled customers cater more? |
| Field Audit Risk Score | IF(FieldAuditScore < 70 AND Catering YoY < -10%, 'High Risk', 'Standard') | Field Audits + Catering | FBCs, District Mgrs | Dual-flag: performance AND compliance at risk |
| Availability vs Catering Sales | DIVIDE([CateringNetSales], [CombinedAvailable hours]) | Catering + Availability | Operations, FBCs | Are stores with pickup/dispatch available driving more catering? |
| Marketing Cost per Catering Order | DIVIDE(SUM(Mktg[PPP]+Mktg[DeliveryFee]+Mktg[EZRewards]), SUM(Catering[FirstPartyTraffic])) | Catering + Mktg Spend | Marketing | ROI of catering incentive programs |


| STORE HEALTH FLAGS — Conditional Logic Using Existing Fields |
| --- |


| Flag Name | Trigger Condition | Tables Used | FBC Action |
| --- | --- | --- | --- |
| 1P Channel Abandonment | 1P catering sales down >25% YoY AND 3P up or flat | Catering | Investigate if franchisee has stopped promoting 1P channel. Coach on direct catering tools. |
| Platform Over-Dependency | 3P share >75% for 3+ consecutive periods | Catering | Franchisee is platform-dependent. Risk: if platform raises fees, catering revenue collapses overnight. |
| Check Size Erosion | Avg check down >15% YoY — orders up but smaller | Catering | Individual/retail orders replacing corporate catering. Investigate catering client pipeline. |
| Catering + Ops Dual Risk | Catering comp <-10% AND FieldAuditScore <75 in same period | Catering + Field Audits | Escalation candidate — not a coaching call. Alert District Manager. |
| Discount-Propped Growth | Catering up but DiscountsCY growing faster than CateringCY in Reported Sales | Reported Sales | Growth is not organic. Investigate PPP/EZ Rewards usage. Unsustainable trajectory. |
| Remodel-Ready Low Performer | Catering declining AND NextRemodelDate overdue (past date) | Catering + Unit | Store facility may be deterring catering clients. Prioritize remodel to unlock revenue. |
| Availability Gap | Catering orders low AND PickupAvailable=0 or DispatchAvailable=0 | Catering + Availability | Store is not offering all catering channels. Enable pickup/dispatch to unlock capacity. |


# Part 4 — Beyond the Current Model: New KPIs That Would Unlock Full Control

These metrics require new data sources or data capture that doesn't exist in the current model. They represent the next frontier of catering intelligence for GoTo Foods.

| REVENUE QUALITY & PROFITABILITY |
| --- |


| Metric | What to Track | Data Needed (not in current model) | Decision It Enables |
| --- | --- | --- | --- |
| Net Catering Margin % | Revenue after platform commissions and delivery costs as % of gross catering sales | 3P platform commission rates (from ezCater/DoorDash contracts) per transaction | Understand true profitability — a store with 80% 3P share may look like a top performer but earn the least per dollar |
| Catering Revenue per Labor Hour | Catering sales divided by labor hours scheduled for catering prep/delivery | Labor scheduling system (e.g. HotSchedules, 7shifts) — labor hours by store by day | Identify whether catering is genuinely profitable after labor costs — high-volume, low-check stores may be labor-negative |
| Platform Commission Drain | Total 3P commission cost estimated per brand (3P Sales × avg platform rate) | Platform commission rate by contract (ezCater ~8–15%, DoorDash ~20–30%) | Quantify exactly how much GoTo Foods/franchisees are paying to 3P platforms annually — build urgency for 1P investment |
| Catering Cancellation Rate | Orders cancelled / orders placed — by channel and brand | Order management system — cancellation events with reason codes | High cancellation = operational readiness issue. Catering clients don't come back after a bad experience. |


| CLIENT QUALITY & RETENTION |
| --- |


| Metric | What to Track | Data Needed (not in current model) | Decision It Enables |
| --- | --- | --- | --- |
| Repeat Catering Client Rate | % of catering orders from clients who ordered in a prior period (30/90/365 day windows) | Client-level order history from catering platform — requires customer ID linkage across orders | One-time catering orders are costly to acquire. Repeat clients are the margin engine. This metric tells you if you're building a catering business or just events. |
| Corporate Account Penetration | % of catering revenue from identified corporate/business accounts vs one-time/retail | CRM or catering platform: account type tagging (corporate, event, individual) | Corporate accounts order 5–10x more per year than individual catering. Track how many stores have active corporate relationships. |
| Catering Churn Rate | Corporate accounts that ordered last year but not this year | Client order history — year-over-year customer ID retention | Silent churn is invisible in current data. A franchisee could lose their 5 biggest corporate clients and the report would only show comp % decline — not why. |
| Average Days Between Orders | For repeat clients: average gap between catering orders | Transaction-level timestamps with customer ID | Cadence metric — weekly corporate lunch orders are a very different business from quarterly event catering |


| OPERATIONAL READINESS & CAPACITY |
| --- |


| Metric | What to Track | Data Needed (not in current model) | Decision It Enables |
| --- | --- | --- | --- |
| Catering Lead Time | Average hours/days between order placement and fulfillment | Order management system: order_placed_timestamp vs fulfillment_timestamp | Catering clients expect >24hr lead time fulfillment. Stores with short lead times may be under-preparing or over-promising. |
| Catering Order Accuracy Rate | % of catering orders fulfilled without substitutions or complaints | Customer feedback system or catering platform order accuracy tags | Corporate catering is zero-tolerance on accuracy. One wrong order for a 50-person meeting costs the entire account. |
| Peak Hour Catering Capacity Utilization | Catering orders fulfilled during peak lunch hours as % of store's estimated catering capacity | POS timestamp data + catering order volume + kitchen capacity model | Identify stores that are leaving catering revenue on the table due to capacity constraints — not demand constraints. |
| Catering-Enabled Venue Penetration | % of non-traditional venues (airports, colleges, hospitals) actively doing catering vs total | Unit table: VenueTradNonTradByFreq + Catering: FirstPartyTraffic > 0 filter | Non-traditional venues are high-frequency catering locations. Track which are dormant on catering. |


| COMPETITIVE & MARKET INTELLIGENCE |
| --- |


| Metric | What to Track | Data Needed (not in current model) | Decision It Enables |
| --- | --- | --- | --- |
| Market Catering Share by DMA | GoTo Foods catering sales as % of estimated total catering market in each DMA | Third-party market data: Technomic, NPD Group catering market sizing by geography | Identify DMAs where GoTo Foods is underpenetrated — growth opportunity vs markets where you already lead |
| Catering Sales per Venue Type | Average catering $ per store segmented by venue (mall, airport, college, hospital, standalone) | Unit table: Venue field already exists — join to Catering by SBRSequence | Understand which venue types generate the most catering. Already possible with existing model — just never done. |
| Catering vs Competitor Pricing Index | Average check size benchmarked against competitor catering menus in same market | Competitive intelligence data: manual or third-party pricing audit | Ensure GoTo Foods catering pricing is competitive without leaving margin on the table |
| New Unit Catering Ramp Rate | Time from store opening to first catering order, and trajectory to steady-state catering sales | Unit: OpenDate + Catering: FirstPartyTraffic first occurrence date | Set realistic catering targets for new stores. Identify which new stores are slow to ramp on catering and intervene early. |



# Summary — The Transformation at a Glance

| Current Report | Transformed Report |
| --- | --- |
| 6 pages — all tables / 1 chart | 5 analytical pages — each with a decision mandate |
| Shows what happened | Shows what it means and who needs to act |
| 1P and 3P as parallel columns — no synthesis | Channel mix, channel shift trend, dependency risk — surfaced proactively |
| No target tracking | OffPremiseTarget vs actual on every relevant view |
| FBC scans 30+ rows manually to find problems | Franchisee alert cards — auto-flagged, color-coded, action-ready |
| Catering Marketing Spend is a transaction list | Incentive ROI view — cost per order, spend vs lift, loyalty correlation |
| Export page exists as workaround | Export page no longer needed — analysis is built in |
| Guest Satisfaction, Field Audits never used in catering context | Overlaid on catering performance — root cause is now diagnosable |
| No flags, no alerts, no conditional logic | 7 store health flags auto-calculated from existing model data |
| Leadership can't tell if growth is real or new-store-inflated | Comp vs system clearly labeled with context, not just two unlabeled tables |


All insights above are available today — using the existing 13-table UDI data model — with no new data sources required.

Next step: wireframe each page in Power BI layout format.