# POC Guide — S.No 195: Time Zone Management for Scheduled Refreshes and Report Timestamps
**Category:** 20. Localization & Internationalization | **Priority:** High | **AtScale dependency:** None

> **Approach: Documentation proof only.** No hands-on POC steps are possible for this item with free/local tools. See the "Why no hands-on POC" section below for the full explanation. All findings are validated against official vendor documentation.

---

## Scenario (GTF-specific)
GTF franchise operators are spread across four US time zones — **ET, CT, MT, PT**. Two operational problems arise:

1. **Scheduled refresh timing:** A nightly data refresh set to run at 2:00 AM may run at 2:00 AM ET (correct for East Coast) but at 11:00 PM PT the previous day (wrong for West Coast operators expecting fresh morning data).
2. **Consumer-facing timestamps:** A report showing "Last refreshed: 2025-06-09 02:00 AM" is confusing or wrong for a PT viewer — it displays in the capacity's time zone, not the viewer's.

---

## Why a hands-on POC cannot be done here

All meaningful time zone behavior in both tools is a **server-side / admin-level feature** — none of it is exposed in the free desktop applications:

| What we want to prove | Why Desktop can't show it |
|---|---|
| Power BI capacity-level time zone setting | Requires a **Power BI Premium or Fabric capacity** — paid, admin-portal-only. Not available in Power BI Desktop or the free Power BI Service tier. |
| Power BI scheduled refresh time zone | Scheduled refresh requires publishing to Power BI Service with a gateway or cloud source. Power BI Desktop has no scheduler. |
| Power BI subscription delivery time zone | Subscriptions are a Power BI Service feature — not available in Desktop at all. |
| Tableau per-site time zone setting | Site Settings are a Tableau Cloud / Tableau Server admin feature. Tableau Desktop has no concept of a "site" — it only connects to published servers. |
| Tableau per-schedule time zone (Server) | Tableau Server admin console feature — requires a live Tableau Server instance (not free). |
| Tableau per-subscription time zone picker | Tableau Cloud / Server feature — not available in Desktop. |

The one thing that could be partially shown in Desktop — datetime column rendering from a plain CSV — behaves **identically in both tools** (displays as stored, no conversion), so it does not demonstrate any meaningful difference and would not add value to the proof.

The full feature set only manifests with a live Power BI Premium/Fabric tenant or a live Tableau Cloud/Server — both require paid access that is not part of the free POC setup. Official documentation from both vendors is the authoritative and sufficient proof for this item.

---

## Documentation proof

### Power BI — Time zone behavior (from official docs)

**1. Capacity-level time zone (the only setting available):**
Documented at: `learn.microsoft.com/en-us/power-bi/admin/service-admin-portal-capacity-settings`
- In the Power BI Admin Portal, a capacity admin can set one time zone for the entire Premium/Fabric capacity.
- This single setting applies to **all workspaces** hosted on that capacity — no per-workspace or per-report override exists.
- Default is UTC.

**2. Scheduled refresh:**
Documented at: `learn.microsoft.com/en-us/power-bi/connect-data/refresh-scheduled-refresh`
- Users schedule refresh times in the dataset settings. Power BI interprets these times in the capacity's time zone.
- The UI note reads: *"Times are in [capacity timezone]"*.
- A franchise wanting a 6:00 AM ET refresh and another wanting 6:00 AM PT **cannot both be served on the same capacity** — the capacity can only be in one time zone at a time.
- Workaround: separate Premium/Fabric capacities per region — but this multiplies infrastructure cost.

**3. Subscriptions:**
Documented at: `learn.microsoft.com/en-us/power-bi/collaborate-share/end-user-subscribe`
- Subscription delivery time is set by the creator and applies in the capacity time zone.
- Recipients receive the email at the scheduled time regardless of their own local time zone.

---

### Tableau — Time zone behavior (from official docs)

**1. Per-site time zone (Tableau Cloud):**
Documented at: `help.tableau.com/current/online/en-us/sites_add.htm`
- Each Tableau Cloud site has its own independently configurable time zone (Site Settings → General → Time zone).
- All extract refreshes and subscriptions on that site run in the site's time zone.
- GTF could have an "East" site set to ET and a "West" site set to PT — each nightly refresh runs at 2:00 AM local time with no workaround needed.

**2. Per-schedule time zone (Tableau Server):**
Documented at: `help.tableau.com/current/server/en-us/schedule_add.htm`
- On Tableau Server, individual refresh schedules each have their own time zone setting.
- Example: schedule "Nightly-ET" at 2:00 AM ET and "Nightly-PT" at 2:00 AM PT can coexist on the same server.
- This is more granular than Tableau Cloud's per-site approach.

**3. Datetime handling and extract timezone:**
Documented at: `help.tableau.com/current/pro/desktop/en-us/dates_timezones.htm`
- For timezone-aware database columns (e.g., `TIMESTAMPTZ` in PostgreSQL), Tableau can convert stored timestamps to the viewer's browser local time at render time via the **Extract timezone** setting.
- Subscription delivery: each subscription has an individual time and time zone picker — the recipient can configure their own delivery time zone.

---

## Side-by-Side Findings Summary

| Capability | Power BI | Tableau |
|---|---|---|
| **Scheduled refresh time zone granularity** | ❌ Capacity-level only — all workspaces share one time zone | ✅ Per-site (Cloud) + per-schedule (Server) |
| **Per-workspace time zone override** | ❌ Not available | ✅ Per-site on Cloud; per-schedule on Server |
| **Consumer-facing timestamp display** | Displays as stored — no automatic viewer-timezone conversion | Converts to viewer local time for timezone-aware source columns |
| **Subscription delivery time zone** | Fixed to capacity time zone (set by creator) | Per-subscription time zone picker |
| **Multi-timezone workaround needed?** | Yes — separate Fabric capacities per region (additional cost) | No — native per-site/per-schedule control handles it |
| **Winner** | ❌ Capacity-level constraint is a real operational gap | ✅ Advantage — granular control without workarounds |

---

## Key talking point for client call
> "Time zone management is one area where the tools differ meaningfully for GTF. Tableau Cloud lets each site have its own time zone, so East Coast and West Coast franchises can each get their nightly data refresh at their local 2:00 AM — no workarounds. Tableau Server goes further with per-schedule time zones. In Power BI, the time zone setting lives at the Fabric capacity level: every workspace on that capacity shares one setting. To support ET and PT franchises on separate refresh schedules, GTF would need separate Premium/Fabric capacities — adding cost and admin overhead. This is a concrete operational advantage for Tableau in a multi-timezone franchise environment."

---

## Findings to enter in Discovery.xlsx after POC

**Column F (Power BI) for S.No 195:**
> Time zone setting is **capacity-level only** (Power BI Admin Portal → Capacity settings → Time zone). All workspaces on the same capacity share this single setting — no per-workspace or per-report override. Scheduled refresh times are interpreted in the capacity time zone. Consumer-facing timestamps display as stored with no automatic viewer-timezone conversion. Subscription delivery time is fixed to capacity time zone. Workaround for multi-timezone GTF franchises: separate Fabric capacities per region (additional infrastructure cost).

**Column G (Tableau) for S.No 195:**
> **Per-site time zone** configurable in Tableau Cloud site settings — each site runs extract refreshes and subscriptions in its own time zone independently. Tableau Server additionally supports **per-schedule time zones** — individual refresh schedules each have their own time zone, enabling region-specific nightly refreshes on one server without workarounds. Subscription delivery has a per-subscription time zone picker. Datetime columns from timezone-aware database sources convert to viewer's local time at render time via the Extract timezone setting.

**Column H (Power BI Proof) for S.No 195:**
> Official documentation:
> https://learn.microsoft.com/en-us/power-bi/admin/service-admin-portal-capacity-settings
> https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-scheduled-refresh
> https://learn.microsoft.com/en-us/power-bi/collaborate-share/end-user-subscribe

**Column I (Tableau Proof) for S.No 195:**
> Official documentation:
> https://help.tableau.com/current/online/en-us/sites_add.htm
> https://help.tableau.com/current/server/en-us/schedule_add.htm
> https://help.tableau.com/current/pro/desktop/en-us/dates.htm

**Column J (Findings) for S.No 195:**
> Advantage Tableau for GTF's multi-timezone franchise operations. Tableau's per-site (Cloud) and per-schedule (Server) time zone control is meaningfully more granular than Power BI's capacity-level-only setting. For GTF with ET/CT/MT/PT franchises, Tableau enables region-specific refresh schedules natively. Power BI requires separate Fabric capacities per region to achieve the same — adding cost and admin overhead. Consumer-facing timestamp rendering is similar in both tools for plain datetime sources; Tableau adds viewer-local-time conversion for timezone-aware database columns. Advantage: TABLEAU — per-site and per-schedule time zone granularity; Power BI limited to capacity-level.

**Column K (Status) for S.No 195:** `COMPLETED`
