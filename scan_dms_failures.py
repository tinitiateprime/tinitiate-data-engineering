SELECT DISTINCT
    dep_ns.nspname AS dependent_schema,
    dep_cls.relname AS dependent_object,
    CASE dep_cls.relkind
        WHEN 'v' THEN 'VIEW'
        WHEN 'm' THEN 'MATERIALIZED VIEW'
    END AS dependent_type
FROM pg_depend d
JOIN pg_rewrite r
    ON r.oid = d.objid
JOIN pg_class dep_cls
    ON dep_cls.oid = r.ev_class
JOIN pg_namespace dep_ns
    ON dep_ns.oid = dep_cls.relnamespace
JOIN pg_class src_cls
    ON src_cls.oid = d.refobjid
JOIN pg_namespace src_ns
    ON src_ns.oid = src_cls.relnamespace
WHERE src_ns.nspname = 'CP'
  AND src_cls.relname = 'PROJ'
  AND dep_cls.relkind IN ('v','m')
ORDER BY dependent_schema, dependent_object;
