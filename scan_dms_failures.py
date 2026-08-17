CREATE MATERIALIZED VIEW irc_census_report_mv AS
SELECT
    my_id,
    last_first_name,
    rpir_name,
    s_empl_status_cd,
    hire_dt,
    reh_dt,
    term_dt,
    seniority_dt,
    term_reason_cd,
    taxable_entity_id,
    locator_cd,
    empl_class_cd,
    pto_accrl_cd,
    bu_name,
    dept_num,
    detl_job_cd,
    title_desc,
    mgr_name,
    bronze_record_active_flg
FROM irc_census_report
WITH DATA;
