INSERT INTO etl_control.etl_table_config
(
    source_schema,
    source_table,
    target_schema,
    target_table,
    enabled,
    skip_reason,
    load_strategy,
    load_order
)
VALUES
    (
        'CP',
        'BILLING_DETL_HIST',
        'CP',
        'BILLING_DETL_HIST',
        false,
        'Waiting for timestamp column',
        'AUTO',
        100
    ),
    (
        'CP',
        'GL_DETL',
        'CP',
        'GL_DETL',
        false,
        'Waiting for timestamp column',
        'AUTO',
        110
    ),
    (
        'CP',
        'LAB_HS',
        'CP',
        'LAB_HS',
        false,
        'Waiting for timestamp column',
        'AUTO',
        120
    ),
    (
        'CP',
        'TS_LN_HS',
        'CP',
        'TS_LN_HS',
        false,
        'Waiting for timestamp column',
        'AUTO',
        130
    )
ON CONFLICT (source_schema, source_table)
DO UPDATE SET
    enabled = EXCLUDED.enabled,
    skip_reason = EXCLUDED.skip_reason,
    updated_datetime = CURRENT_TIMESTAMP;
