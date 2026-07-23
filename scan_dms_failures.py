INSERT INTO etl_control.etl_table_config
(
    source_schema,
    source_table,
    target_schema,
    target_table,
    enabled,
    load_strategy,
    timestamp_column,
    created_datetime
)
SELECT DISTINCT
    source_schema,
    source_table,
    source_schema,
    source_table,
    TRUE,

    CASE
        WHEN source_schema IN ('CP','TE')
            THEN 'CURRENT_DAY_MERGE'
        ELSE 'SNAPSHOT_REPLACE'
    END,

    CASE
        WHEN source_schema IN ('CP','TE')
            THEN 'TIME_STAMP'
        ELSE NULL
    END,

    CURRENT_TIMESTAMP
FROM etl_control.etl_load_control
WHERE NOT EXISTS
(
    SELECT 1
    FROM etl_control.etl_table_config c
    WHERE c.source_schema = etl_load_control.source_schema
      AND c.source_table  = etl_load_control.source_table
);
