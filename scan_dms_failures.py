WITH latest AS
(
    SELECT DISTINCT ON (source_schema, source_table)
        run_id,
        source_schema,
        source_table,
        target_schema,
        target_table,
        bronze_count,
        silver_count,
        rows_processed,
        status,
        start_datetime,
        end_datetime,
        message
    FROM etl_control.etl_load_control
    ORDER BY
        source_schema,
        source_table,
        start_datetime DESC
)
SELECT
    source_schema,
    source_table,
    target_schema,
    target_table,
    bronze_count,
    rows_processed,
    status,
    end_datetime - start_datetime AS duration,
    CASE
        WHEN message ILIKE '%SNAPSHOT_REPLACE%'
          OR message ILIKE '%complete Bronze%'
            THEN 'SNAPSHOT_REPLACE'
        WHEN message ILIKE '%INITIAL_FULL_LOAD%'
          OR message ILIKE '%target was empty%'
            THEN 'INITIAL_FULL_LOAD'
        WHEN message ILIKE '%Merged%'
            THEN 'ROLLING_WINDOW_MERGE'
        WHEN message ILIKE '%Replaced%'
          AND message ILIKE '%day%'
            THEN 'ROLLING_WINDOW_REPLACE'
        ELSE 'CHECK MESSAGE'
    END AS actual_processing,
    message
FROM latest
ORDER BY rows_processed DESC NULLS LAST;


WITH latest AS
(
    SELECT DISTINCT ON (source_schema, source_table)
        *
    FROM etl_control.etl_load_control
    ORDER BY
        source_schema,
        source_table,
        start_datetime DESC
)
SELECT
    l.source_schema,
    l.source_table,
    pg_size_pretty(
        pg_total_relation_size(
            to_regclass(format('%I.%I', l.target_schema, l.target_table))
        )
    ) AS target_size,
    l.bronze_count,
    l.rows_processed,
    l.end_datetime - l.start_datetime AS duration,
    l.message
FROM latest l
WHERE to_regclass(
          format('%I.%I', l.target_schema, l.target_table)
      ) IS NOT NULL
ORDER BY pg_total_relation_size(
             to_regclass(format('%I.%I', l.target_schema, l.target_table))
         ) DESC
LIMIT 25;

