SELECT
    config_id,
    source_schema,
    source_table,
    target_schema,
    target_table,
    pg_size_pretty(
        pg_total_relation_size(
            to_regclass(
                format('%I.%I', target_schema, target_table)
            )
        )
    ) AS total_size,
    pg_size_pretty(
        pg_relation_size(
            to_regclass(
                format('%I.%I', target_schema, target_table)
            )
        )
    ) AS table_size,
    pg_size_pretty(
        pg_indexes_size(
            to_regclass(
                format('%I.%I', target_schema, target_table)
            )
        )
    ) AS index_size
FROM etl_control.etl_table_config
WHERE enabled = true
  AND load_strategy = 'SNAPSHOT_REPLACE'
  AND to_regclass(
        format('%I.%I', target_schema, target_table)
      ) IS NOT NULL
ORDER BY pg_total_relation_size(
             to_regclass(
                 format('%I.%I', target_schema, target_table)
             )
         ) DESC;



SELECT
    schemaname,
    relname AS table_name,
    n_live_tup,
    n_dead_tup,
    last_autovacuum,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE (schemaname, relname) IN (
    SELECT target_schema, target_table
    FROM etl_control.etl_table_config
    WHERE enabled = true
      AND load_strategy = 'SNAPSHOT_REPLACE'
)
ORDER BY n_dead_tup DESC;
