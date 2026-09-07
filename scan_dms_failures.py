Epic: Gold Migration and API Environment Alignment
#	Jira Ticket	Scope / Deliverable	Exit Criteria
1	Validate Current API-to-Data Mapping	Document current DEV, TEST, PROD API host/database/schema mappings and current secrets/configuration.	Current-state matrix reviewed and confirmed.
2	Validate Target Environment Mapping	Confirm intended mapping: TEST → Synth, DEV → Silver, PROD → Gold. Confirm exact RDS host, DB, schema, secret, and Lambda for each.	Target-state matrix approved before changes.
3	Version Control All Gold Materialized Views	Add the generated one-file-per-MV SQL scripts under SQL Scripts/MVs, including indexes, excluding owners/permissions.	DB MV count = Git file count; all scripts committed and reviewed.
4	Validate Silver-to-Gold Object Readiness	Compare required schemas, tables, views, MVs, columns, data types, indexes, and dependencies between Silver and Gold.	No missing API dependencies in Gold.
5	Validate Silver Data Refresh / CLM Load	Confirm CLM and other required source domains are loading into Silver nightly and are current before cutover.	Latest successful load verified with counts/timestamps.
6	Gold Data Migration / Refresh	Load or refresh Gold objects from Silver and validate Gold data.	Required Gold data is current and validated.
7	Data Quality Validation for Gold	Validate source/target counts, null keys, duplicate keys, stale/no-data conditions, and critical business checks such as contract_id.	Critical DQ checks pass or have approved exceptions.
8	Configure TEST API → Synth	Update TEST API configuration/secret to point to the intended Synth data location.	TEST API connects and smoke tests pass.
9	Configure DEV API → Silver	Update DEV API configuration/secret to point to Silver mtdm.	DEV API connects and functional/API tests pass.
10	Configure PROD API → Gold	Update production Lambda/API configuration to Gold RDS/database/schema.	PROD API connects to Gold and all critical endpoints pass.
11	Production API Smoke / Regression Testing	Test critical API endpoints, filters, sorting, pagination, key lookups, response models, and record consistency after cutover.	No critical regressions.
12	Glue Job Failure Alerting	Add monitoring/notification for FAILED, TIMEOUT, STOPPED Glue runs.	Controlled failure generates expected alert.
13	Framework Data Quality Alerting	Add alerting for failed data-quality checks and no-data/stale-data situations.	DQ failure triggers notification.
14	Production Monitoring and Operational Readiness	Confirm CloudWatch/API/Lambda/Glue monitoring, DB connectivity checks, and operational ownership.	Monitoring validated and support path documented.
15	Rollback Plan and Cutover Runbook	Document previous host/secret/config values and exact rollback steps for API and Gold changes.	Rollback tested/documented before PROD cutover.
16	Post-Cutover Validation and Sign-off	Compare Silver vs Gold results, verify API responses, MV refresh status, Glue status, DQ results, and production monitoring.	Kevin/team sign-off.



    Current-state validation
        ↓
Target mapping approval
        ↓
MV version control
        ↓
Silver/CLM readiness validation
        ↓
Gold object + data validation
        ↓
TEST → Synth
        ↓
DEV → Silver
        ↓
Regression testing
        ↓
Production readiness / monitoring / rollback
        ↓
PROD → Gold
        ↓
Post-cutover validation
        ↓
Sign-off


    I have the MV definitions split into individual version-controlled SQL files now. For the Gold/API migration, I’m breaking the work into Jira tickets covering current/target environment validation, Silver and CLM readiness, Gold object/data validation, TEST/DEV alignment, production cutover, regression testing, Glue/DQ monitoring, rollback, and post-cutover sign-off. I’ll sequence the PROD API switch only after TEST and DEV are validated so we minimize disruption
