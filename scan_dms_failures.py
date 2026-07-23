INSERT INTO etl_control.etl_table_config
(
    source_schema,
    source_table,
    target_schema,
    target_table,
    enabled,
    load_strategy,
    timestamp_column,
    created_datetime,
    updated_datetime
)
SELECT DISTINCT
    source_schema,
    source_table,
    target_schema,
    target_table,
    TRUE,

    CASE
        WHEN source_schema IN ('CP','TE')
            THEN 'CURRENT_DAY_MERGE'

        WHEN source_schema IN ('CLM','HRIS','OS')
            THEN 'SNAPSHOT_REPLACE'

        ELSE 'SNAPSHOT_REPLACE'
    END AS load_strategy,

    CASE
        WHEN source_schema IN ('CP','TE')
            THEN 'TIME_STAMP'

        ELSE NULL
    END AS timestamp_column,

    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP

FROM etl_control.etl_load_control
WHERE source_schema IN
(
    'CP',
    'CLM',
    'HRIS',
    'OS',
    'TE'
)
AND NOT EXISTS
(
    SELECT 1
    FROM etl_control.etl_table_config cfg
    WHERE cfg.source_schema = etl_load_control.source_schema
      AND cfg.source_table  = etl_load_control.source_table
);
