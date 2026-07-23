INSERT INTO etl_control.etl_schema_config
(
    source_schema,
    target_schema,
    enabled,
    skip_reason,
    schema_load_order,
    default_load_strategy,
    created_datetime,
    updated_datetime
)
VALUES
(
    'CLM',
    'CLM',
    TRUE,
    NULL,
    10,
    'SNAPSHOT_REPLACE',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'CP',
    'CP',
    TRUE,
    NULL,
    20,
    'AUTO',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'HRIS',
    'HRIS',
    TRUE,
    NULL,
    30,
    'SNAPSHOT_REPLACE',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'OS',
    'OS',
    TRUE,
    NULL,
    40,
    'SNAPSHOT_REPLACE',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'TE',
    'TE',
    TRUE,
    NULL,
    50,
    'AUTO',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (source_schema, target_schema)
DO UPDATE
SET
    enabled = EXCLUDED.enabled,
    skip_reason = EXCLUDED.skip_reason,
    schema_load_order = EXCLUDED.schema_load_order,
    default_load_strategy = EXCLUDED.default_load_strategy,
    updated_datetime = CURRENT_TIMESTAMP;
