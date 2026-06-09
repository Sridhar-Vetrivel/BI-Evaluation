# Tableau Evaluation Requirements

Thanks for your help to do Tableau evaluation for us.

Please find below our evaluation needs and let us know if have any questions.

We already evaluated the performance of Tableau summary and detail reports with new AtScale analytical layer. It performed well compared to Power BI.

---

# Evaluation Requirements given by the client

## 1. Azure AD Connectivity

- Validate Tableau integration with Azure AD / Entra ID
- Single Sign-On (SSO)
- MFA support
- User authentication and authorization

---

## 2. Tableau Gateways for Refreshing Reports

- Refresh scheduling
- Live connection support
- Gateway/Bridge setup
- Data refresh architecture

---

## 3. Equivalent Feature to Power BI Apps

Need a way to:
- Group reports
- Publish dashboards
- Manage user access centrally

Tableau equivalents:
- Projects
- Sites
- Collections

---

## 4. Row Level Security (RLS)

Need user-based data security:
- Franchise-level filtering
- Dynamic access control
- Role-based visibility

---

## 5. Bookmarks Equivalent

Power BI bookmarks are used for:
- Changing views
- Navigation
- Filter state management

Need Tableau equivalent implementation.

---

# 6. Visualizations

## a. Report with User Input / Action

- Interactive dashboards
- Parameters
- Actions
- What-if analysis

---

## b. Reports with Many Filters

- Multiple filters
- Dynamic filtering
- High usability
- Performance validation

---

## c. Pretty Visualization

Need visually rich dashboards:
- Executive reporting
- Storytelling
- Modern UI/UX

---

## d. P&L Reporting

Need support for:
- Financial reporting
- Hierarchies
- Drilldowns
- Matrix-style layouts
- Subtotals and formatting

---

# 7. Reports with Large Number of Rows

Example:
- Catering detail report

Need to validate:
- Performance
- Pagination
- Export capability
- Detail-level reporting

---

# 8. Equivalent to Power BI Robots

Need automation support for:
- Filtering reports
- Scheduled emails
- Franchise-specific report delivery

Possible Tableau options:
- Subscriptions
- REST APIs
- Automation tools

---

# 9. SSAS and Azure Analysis Services Connectivity

Need Tableau connectivity validation for:
- SSAS
- Azure Analysis Services
- Semantic models
- Live cube connectivity

---

# Architecture Flow

## Older Architecture

```text
EDW --> SSIS --> SSAS --> Power BI
```

---

## New Architecture

```text
EDW --> Data Platform (Databricks + ADF) --> AtScale --> Power BI / Tableau
```

---

# Strategic Objective

Evaluate whether Tableau can support enterprise BI requirements alongside or instead of Power BI using the new AtScale semantic layer architecture.


# Evaluation Criteria Categories

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

# Here's the full breakdown across all 20 categories additional to client requirements:
 
---
 
## 1. Data Connectivity & Integration
 
- Native connectors to structured sources (SQL Server, Oracle, Snowflake, BigQuery, Redshift, SAP HANA)
- Support for semi-structured and unstructured sources (JSON, XML, REST APIs, web scraping)
- File-based ingestion (Excel, CSV, Parquet, Avro)
- Cloud storage connectors (S3, Azure Blob, GCS)
- ERP/CRM connectors (SAP, Salesforce, Dynamics 365, ServiceNow)
- Custom connector development capability (SDK support)
- Live connection vs. import mode availability per source
- OAuth and token-based authentication support for API sources
- Support for on-premises data sources via gateway
- Connector certification and update frequency by vendor
 
---
 
## 2. Visualization & UX
 
- Library of standard chart types (bar, line, scatter, pie, waterfall, funnel, bullet)
- Advanced/specialized chart types (heatmaps, treemaps, Sankey, chord, small multiples)
- Custom visualization support (D3.js, Vega-Lite, marketplace extensions)
- Conditional formatting and dynamic visual properties
- Cross-filtering and drill-down/drill-through behavior
- Tooltip customization and rich interactivity
- Dashboard layout flexibility (pixel-perfect vs. responsive grid)
- Theming and branding consistency across reports
- Animation and transitions for storytelling
- Accessibility of visuals (screen reader compatibility, color-blind palettes)
 
---
 
## 3. Governance, Security & Compliance
 
- Role-based access control (RBAC) at report, dataset, and workspace level
- Row-level security (RLS) and column-level security (CLS)
- Single Sign-On (SSO) integration (SAML, OIDC, Azure AD, Okta)
- Data classification and sensitivity label enforcement
- Compliance certifications held by vendor (SOC 2, ISO 27001, HIPAA, FedRAMP, GDPR)
- Data residency and sovereignty controls
- Tenant-level isolation in multi-tenant deployments
- Policy enforcement for sharing (prevent external sharing, download restrictions)
- Encryption at rest and in transit
- Periodic access reviews and certification workflows
 
---
 
## 4. Performance & Scalability
 
- Query response time under concurrent user load (SLA benchmarks)
- Dataset size limits (row count, in-memory vs. DirectQuery thresholds)
- Aggregation and caching strategies (pre-aggregation, query caching, dual mode)
- Horizontal scaling capability for large deployments
- Performance profiling and query diagnostics tooling
- Handling of high-cardinality dimensions
- Scheduled refresh frequency limits and concurrency
- Impact of complex calculations on render time
- CDN support for global report distribution
- Load testing support and documented capacity planning models
 
---
 
## 5. Collaboration & Sharing
 
- Workspace or project-based collaboration with role assignments
- Report commenting and annotation features
- Sharing via link, embed, or direct user assignment
- External user sharing (guest/B2B access)
- Subscription and snapshot sharing (static vs. live)
- Co-authoring or concurrent editing support
- Notification and change alert mechanisms
- Integration with collaboration platforms (Teams, Slack, email)
- Version history and rollback on shared content
- Approval workflows for publishing reports
 
---
 
## 6. Licensing & TCO
 
- Licensing model (per user, per capacity/core, consumption-based)
- Cost at different scale points (50, 500, 5000 users)
- Distinction between author/creator vs. viewer licensing costs
- Premium or capacity-based tiers and what they unlock
- Cost of connectors, add-ons, and marketplace extensions
- On-premises vs. cloud licensing cost differential
- Contractual flexibility (annual vs. monthly, enterprise agreements)
- Hidden costs — gateway infrastructure, training, professional services
- Vendor discount structures for large enterprise commitments
- Total 3-year TCO model including infrastructure and admin overhead
 
---
 
## 7. AI/ML & Advanced Analytics
 
- Native AI visuals (anomaly detection, forecasting, key influencers)
- Natural language query interface (Q&A, Ask Data)
- Integration with ML platforms (Azure ML, SageMaker, Databricks, Vertex AI)
- Python and R script execution within the tool
- AutoML or no-code ML model building
- Explainability features for AI-generated insights
- Smart narrative and automated insight generation
- Predictive analytics and what-if scenario modeling
- Vector/embedding search or GenAI integration roadmap
- Ability to surface model outputs as first-class visuals
 
---
 
## 8. Deployment & IT Operations
 
- Deployment modes — SaaS, self-hosted, hybrid
- Cloud platform support (Azure, AWS, GCP, on-premises)
- High availability and disaster recovery architecture
- Upgrade and patch management process (vendor-managed vs. self-managed)
- Infrastructure-as-code support for provisioning
- Admin portal capabilities (usage monitoring, capacity management, user management)
- Multi-environment support (dev, staging, production)
- Backup and restore capabilities for BI content
- SLA commitments and incident response times
- Container and Kubernetes deployment support (for self-hosted options)
 
---
 
## 9. Data Modeling & Semantic Layer
 
- Support for star and snowflake schema modeling
- Calculated columns, measures, and KPI definitions (DAX, Tableau calculations)
- Reusable certified dataset / semantic model concept
- Relationships and cardinality handling (many-to-many, bi-directional)
- Hierarchy definition and drill path management
- Time intelligence functions (YTD, MTD, rolling periods)
- Centralized metric layer support (compatibility with dbt Semantic Layer, AtScale, Cube)
- Ability to govern and version the semantic model independently of reports
- Support for composite models (mixing live and imported data)
- Data type handling and implicit vs. explicit conversion behavior
 
---
 
## 10. Embedded Analytics
 
- Embedding via iFrame, JavaScript SDK, or REST API
- Row-level security propagation in embedded context
- White-labeling and full UI customization for embedded scenarios
- Token-based authentication for embedded sessions (no vendor login required)
- Licensing model for embedded usage (app-owns-data vs. user-owns-data)
- Interaction API for programmatic control of filters and visuals
- Performance of embedded reports at scale
- Cross-origin (CORS) and Content Security Policy (CSP) compliance
- Support for embedding in mobile apps (iOS/Android)
- Analytics portal pattern support (multi-tenant embedded deployments)
 
---
 
## 11. Extensibility & Developer Ecosystem
 
- REST API coverage (CRUD on reports, datasets, workspaces, users)
- Webhook and event-driven integration support
- Custom visual development framework and marketplace
- CLI tooling for automation and scripting
- SDK availability and language support (Python, .NET, JavaScript, REST)
- Third-party extension ecosystem maturity
- Programmatic report generation (templating, parameterized reports)
- Integration with orchestration tools (Azure Data Factory, Airflow, dbt)
- Community-contributed connectors and visuals quality and maintenance
- Developer documentation quality and completeness
 
---
 
## 12. Vendor Maturity & Ecosystem
 
- Gartner Magic Quadrant / Forrester Wave positioning and trajectory
- Product release cadence and public roadmap transparency
- Vendor financial stability and long-term viability
- Size and activity of community (forums, Stack Overflow, GitHub)
- Training and certification program availability and industry recognition
- Partner ecosystem for implementation and support
- User group and conference ecosystem (Tableau Conference, Microsoft Fabric Community)
- Support tier options (standard, premier, dedicated TAM)
- Responsiveness to enterprise support tickets
- History of backward compatibility and migration support during major version changes
 
---
 
## 13. Mobile & Accessibility
 
- Native mobile app availability (iOS and Android)
- Responsive layout design vs. dedicated mobile layout authoring
- Offline report access on mobile
- Touch-optimized interaction design
- Push notification support for alerts on mobile
- WCAG 2.1 AA compliance for accessibility
- Keyboard navigation support in desktop and web interfaces
- Screen reader compatibility (NVDA, JAWS, VoiceOver)
- Color contrast and color-blind safe defaults
- Accessibility audit tooling or built-in checker
 
---
 
## 14. Interoperability & Standards
 
- ODBC/JDBC connectivity for third-party tool access
- OData endpoint exposure for report data consumption
- Compatibility with enterprise metadata catalogs (Microsoft Purview, Alation, Collibra, Atlan)
- Export formats supported (PDF, Excel, CSV, PNG, PowerPoint)
- Open standard support (Apache Arrow, XMLA endpoint, ANSI SQL)
- Integration with data catalog and data dictionary platforms
- Compatibility with ETL/ELT tools (Informatica, Talend, Fivetran, dbt)
- Cross-tool report migration tooling availability
- Support for industry-specific data standards (FHIR for healthcare, XBRL for finance)
- API versioning and deprecation policy
 
---
 
## 15. Self-Service & Authoring Experience
 
- Drag-and-drop report building without SQL or coding knowledge
- Guided analytics and template-based starting points
- Natural language query for ad-hoc exploration
- Field suggestion and smart auto-complete during authoring
- In-tool data preparation and transformation (Power Query, Tableau Prep)
- Undo/redo depth and autosave behavior
- Governed self-service model — ability to expose certified datasets for user-built reports
- Sandbox or personal workspace for experimentation without impacting production
- Complexity gradient — simple reports accessible to novices, advanced features for power users
- In-product help, tutorials, and contextual guidance
 
---
 
## 16. Report Consumption & Alerting
 
- Data-driven alerts on threshold breaches (KPI alerts)
- Scheduled email subscriptions with report snapshots
- Personalized filter state persistence per user
- In-report commenting and collaborative annotation
- Print and export options for consumers (not just authors)
- Bookmark and personal view saving
- Paginated report support for operational/pixel-perfect outputs
- Report embedding in email or intranet portals
- In-app notification center for alerts and updates
- Performance of report load time for consumers on low-bandwidth connections
 
---
 
## 17. Data Lineage & Audit Trail
 
- End-to-end lineage from data source through transformation to visual
- Impact analysis — which reports are affected if a dataset changes
- Column-level lineage visibility
- Report and dataset usage analytics (who viewed, how often, last accessed)
- Integration with enterprise data catalog for lineage federation
- Audit logs for user activity (logins, report access, data exports, permission changes)
- Data freshness visibility — last refresh timestamp surfaced to consumers
- Stale report detection and notification
- Lineage graph visualization within the tool
- Retention policy for audit logs and compliance archival
 
---
 
## 18. Version Control & CI/CD for BI
 
- Native Git integration for report and dataset versioning
- Branching and merging support for parallel development
- Deployment pipeline support (dev → test → prod promotion)
- Diff and comparison tooling for BI artifact changes
- Rollback capability to previous versions
- Automated testing framework for reports and measures (data validation, regression)
- CLI or API-driven deployment for pipeline automation
- Environment variable and parameter management across environments
- Integration with CI/CD platforms (Azure DevOps, GitHub Actions, Jenkins)
- Change approval and release gating workflows
 
## 19. Real-time & Streaming Analytics
 
- Support for streaming data ingestion (Kafka, Event Hubs, Kinesis, MQTT)
- Push dataset API for real-time dashboard updates
- DirectQuery mode availability and performance across source types
- Configurable auto-refresh intervals for near-real-time use cases
- Incremental refresh support to reduce full dataset reload overhead
- Latency SLA between data event and dashboard update
- Hybrid mode support (mix of real-time and historical data in one dashboard)
- Alert triggering on streaming threshold breaches
- Scalability of real-time connections under concurrent viewer load
- Compatibility with stream processing platforms (Spark Streaming, Flink, Azure Stream Analytics)
 
20. Localization & Internationalization
 
- UI language support and number of available locale translations
- Locale-aware number, date, and currency formatting
- Right-to-left (RTL) language support (Arabic, Hebrew)
- Multi-currency display and conversion handling
- Time zone management for scheduled refreshes and report timestamps
- Translation workflow for report labels and field names
- Regional compliance support (GDPR for EU, PDPA for Thailand, LGPD for Brazil)
- Support for non-Latin character sets (CJK, Devanagari, Cyrillic)
- Locale-specific sorting and collation rules
- Regional data residency options aligned with localization needs
 


# Implementation Checkpoints

1. Confirm what are the evaluation criteria categories along with the breakdown that are actually needed for our use case considering the new architecture
2. Once the categories are confirmed, Give reasoning by creating a new column in the excel, with respect to the use case (Atscale to TableAU/PowerBI) 
3. Then start with Evalution
4. Do POCs/Add Official documentation for Proofs
5. Categorize the evalution excel based on high confidence and low confidence with the help of human
6. Research more to prove low confidence areas

