INSERT INTO etl_control.etl_table_config
(
    source_schema,
    source_table,
    target_schema,
    target_table,
    enabled,
    load_order
)
VALUES
(
    'CLM',
    'table_to_exclude',
    'CLM',
    'table_to_exclude',
    false,
    100
)
ON CONFLICT (source_schema, source_table)
DO UPDATE SET
    enabled = false,
    updated_datetime = CURRENT_TIMESTAMP;

UPDATE etl_control.etl_table_config
SET
    enabled = true,
    updated_datetime = CURRENT_TIMESTAMP
WHERE source_schema = 'CLM'
  AND source_table = 'table_to_exclude';


INSERT INTO etl_control.etl_schema_config
(
    source_schema,
    target_schema,
    enabled,
    load_order
)
VALUES
    ('CLM',  'CLM',     true, 10),
    ('SOTV', 'SOTV',    true, 20),
    ('FIN',  'FINANCE', true, 30)
ON CONFLICT (source_schema, target_schema)
DO UPDATE SET
    enabled = EXCLUDED.enabled,
    load_order = EXCLUDED.load_order,
    updated_datetime = CURRENT_TIMESTAMP;


INSERT INTO etl_control.etl_table_config
(
    source_schema,
    source_table,
    target_schema,
    target_table,
    enabled,
    primary_key_override,
    load_order
)
VALUES
(
    'SOTV',
    'employee_profile',
    'SOTV',
    'employee_profile',
    true,
    'employee_id,profile_id',
    10
);






