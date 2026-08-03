Update on MTCIODAT-206 (Confirm DMS target table preparation mode).

gsapdi-schema-migration-task includes all of the schemas in scope for this ticket — CLM, CP, OS, and HRIS — plus STG and TE (6 schemas total, confirmed via the task's selection rules).

The task-level setting FullLoadSettings.TargetTablePrepMode is set to DROP_AND_CREATE. Since this is a single task-level setting, it applies uniformly to all 6 schemas listed above.

This confirms the risk the ticket was raised for: on a full load, DMS drops and recreates every target table across these schemas, which cascades into dropping any gold materialized views built on top of them (e.g. project_financials_source_vw) rather than causing a visible failure.

Flag: this task is currently in a Failed state (out-of-memory error, stopped July 10). No cascade has happened from its last run, but DROP_AND_CREATE will trigger it again the next time the task completes a successful full load.

Proposed remediation:

Change TargetTablePrepMode to TRUNCATE_BEFORE_LOAD for this task, since it feeds gold matviews, or
Add a post-load step to recreate affected matviews after each full load
Resolve the OOM issue on gsapdi-schema-migration-task before it's safe to rerun
