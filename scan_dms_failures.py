SELECT DISTINCT
    n.nspname AS dependent_schema,
    c.relname AS dependent_object,
    CASE c.relkind
        WHEN 'v' THEN 'VIEW'
        WHEN 'm' THEN 'MATERIALIZED VIEW'
        ELSE c.relkind::text
    END AS object_type
FROM pg_depend d
JOIN pg_rewrite r
    ON r.oid = d.objid
JOIN pg_class c
    ON c.oid = r.ev_class
JOIN pg_namespace n
    ON n.oid = c.relnamespace
WHERE d.refobjid = 'your_schema.your_materialized_view'::regclass
  AND c.oid <> d.refobjid
ORDER BY dependent_schema, dependent_object;



-- Also check objects that depend on the materialized view's columns
SELECT DISTINCT
    n.nspname AS dependent_schema,
    c.relname AS dependent_object,
    CASE c.relkind
        WHEN 'v' THEN 'VIEW'
        WHEN 'm' THEN 'MATERIALIZED VIEW'
        ELSE c.relkind::text
    END AS object_type
FROM pg_depend d
JOIN pg_rewrite r
    ON r.oid = d.objid
JOIN pg_class c
    ON c.oid = r.ev_class
JOIN pg_namespace n
    ON n.oid = c.relnamespace
WHERE d.refobjid = 'your_schema.your_materialized_view'::regclass
ORDER BY dependent_schema, dependent_object;
