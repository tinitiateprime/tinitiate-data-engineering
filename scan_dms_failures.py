SELECT DISTINCT
    dependent_ns.nspname AS materialized_view_schema,
    dependent_view.relname AS materialized_view_name,
    source_ns.nspname AS source_schema,
    source_object.relname AS source_object_name,
    CASE source_object.relkind
        WHEN 'r' THEN 'table'
        WHEN 'v' THEN 'view'
        WHEN 'm' THEN 'materialized view'
        WHEN 'p' THEN 'partitioned table'
        WHEN 'f' THEN 'foreign table'
        ELSE source_object.relkind::text
    END AS source_object_type
FROM pg_depend d
JOIN pg_rewrite rw
    ON d.objid = rw.oid
JOIN pg_class dependent_view
    ON rw.ev_class = dependent_view.oid
JOIN pg_namespace dependent_ns
    ON dependent_view.relnamespace = dependent_ns.oid
JOIN pg_class source_object
    ON d.refobjid = source_object.oid
JOIN pg_namespace source_ns
    ON source_object.relnamespace = source_ns.oid
WHERE dependent_view.relkind = 'm'
  AND dependent_ns.nspname = 'your_schema'
  AND dependent_view.relname = 'your_materialized_view'
  AND source_object.oid <> dependent_view.oid
ORDER BY
    source_schema,
    source_object_name;
