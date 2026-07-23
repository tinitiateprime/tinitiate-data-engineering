INSERT INTO etl_control.etl_table_config
(
    source_schema,
    source_table,
    target_schema,
    target_table,
    enabled,
    skip_reason,
    primary_key_override,
    timestamp_column,
    load_strategy,
    load_order,
    created_datetime,
    updated_datetime
)
SELECT DISTINCT
    source_schema,
    source_table,
    target_schema,
    target_table,
    TRUE AS enabled,
    NULL AS skip_reason,
    NULL AS primary_key_override,

    CASE
        WHEN UPPER(source_schema) IN ('CP', 'TE')
            THEN 'TIME_STAMP'
        ELSE NULL
    END AS timestamp_column,

    CASE
        WHEN UPPER(source_schema) IN ('CP', 'TE')
            THEN 'AUTO'
        WHEN UPPER(source_schema) IN ('CLM', 'HRIS', 'OS')
            THEN 'SNAPSHOT_REPLACE'
        ELSE 'SNAPSHOT_REPLACE'
    END AS load_strategy,

    100 AS load_order,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP

FROM etl_control.etl_load_control

WHERE source_schema IN
(
    'CLM',
    'CP',
    'HRIS',
    'OS',
    'TE'
)

ON CONFLICT (source_schema, source_table)
DO UPDATE
SET
    target_schema = EXCLUDED.target_schema,
    target_table = EXCLUDED.target_table,
    enabled = EXCLUDED.enabled,
    timestamp_column = EXCLUDED.timestamp_column,
    load_strategy = EXCLUDED.load_strategy,
    updated_datetime = CURRENT_TIMESTAMP;
