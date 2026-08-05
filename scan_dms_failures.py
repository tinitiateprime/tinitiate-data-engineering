CREATE OR REPLACE FUNCTION gold.get_project_forecasts(
    p_scenario text DEFAULT 'Forecast2026M8'
)
RETURNS TABLE (
    row_id                   bigint,
    proj_id                  text,
    lvl_no                   integer,
    cust_name                text,
    proj_name                text,
    proj_type_dc             text,
    s_proj_rpt_dc            text,
    prime_contr_id           text,
    org_id                   text,
    active_fl                text,
    proj_mgr_name            text,
    proj_start_dt            date,
    proj_end_dt              date,
    value_total_amount       numeric,
    project_value_cost       numeric,
    project_value_fee        numeric,
    proj_f_tot_amt           numeric,
    cost_funded              numeric,
    fee_funded               numeric,
    total_billed             numeric,
    billed_cost              numeric,
    billed_fee               numeric,
    open_billing_detail_amt  numeric,
    open_commit_amt          numeric,
    eac                      numeric,
    etc                      numeric,
    date_75_expended         date,
    date_100_expended        date,
    forecast_by_period       jsonb
)
LANGUAGE sql
STABLE
AS $$
    WITH forecast_curve AS (
        SELECT f.proj_id,
               jsonb_object_agg(
                   to_char(cal.pd_end_dt::timestamp with time zone, 'YYYY-MM'::text),
                   f.amt
               ) AS forecast_by_period
        FROM (
            SELECT r.proj_id,
                   r.fy,
                   r.pd,
                   sum(r.amount) AS amt
            FROM (
                SELECT "FORECAST".proj_id,
                       "FORECAST".fy,
                       "FORECAST".pd,
                       "FORECAST".amount,
                       "FORECAST".actuals_flag,
                       bool_or("FORECAST".actuals_flag::text = 'Y'::text)
                           OVER (PARTITION BY "FORECAST".proj_id, "FORECAST".fy, "FORECAST".pd)
                           AS has_actual
                FROM "OS"."FORECAST"
                WHERE "FORECAST".scenario::text = p_scenario
                  AND "FORECAST".amount_type::text = 'Revenue'::text
            ) r
            WHERE (r.has_actual AND r.actuals_flag::text = 'Y'::text)
               OR (NOT r.has_actual AND r.actuals_flag::text = 'N'::text)
            GROUP BY r.proj_id, r.fy, r.pd
        ) f
        JOIN "CP"."ACCTING_PD" cal
            ON cal.fy_cd::text = f.fy::text
           AND cal.pd_no::text = f.pd::text
        GROUP BY f.proj_id
    ),
    eac_etc AS (
        SELECT "OS_EST"."PROJ_ID" AS proj_id,
               sum("OS_EST"."EAC_AMT") AS eac,
               sum("OS_EST"."ETC_AMT") AS etc
        FROM "OS"."OS_EST"
        GROUP BY "OS_EST"."PROJ_ID"
    )
    SELECT row_number() OVER (ORDER BY p.proj_id, p.lvl_no) AS row_id,
           p.proj_id,
           p.lvl_no,
           p.cust_name,
           p.proj_name,
           p.proj_type_dc,
           p.s_proj_rpt_dc,
           p.prime_contr_id,
           p.org_id,
           p.active_fl,
           p.proj_mgr_name,
           p.proj_start_dt,
           p.proj_end_dt,
           p.value_total_amount,
           p.project_value_cost,
           p.project_value_fee,
           p.proj_f_tot_amt,
           p.cost_funded,
           p.fee_funded,
           p.total_billed,
           p.billed_cost,
           p.billed_fee,
           p.open_billing_detail_amt,
           p.open_commit_amt,
           ee.eac,
           ee.etc,
           NULL::date AS date_75_expended,
           NULL::date AS date_100_expended,
           fc.forecast_by_period
    FROM gold.project_financials_source_vw p
    LEFT JOIN forecast_curve fc ON fc.proj_id::text = p.proj_id::text
    LEFT JOIN eac_etc ee ON ee.proj_id::text = p.proj_id::text;
$$;
