SELECT DISTINCT
    n2.nspname AS source_schema,
    c2.relname AS source_object
FROM pg_rewrite r
JOIN pg_class c1
    ON r.ev_class = c1.oid
JOIN pg_namespace n1
    ON c1.relnamespace = n1.oid
JOIN pg_depend d
    ON d.objid = r.oid
JOIN pg_class c2
    ON d.refobjid = c2.oid
JOIN pg_namespace n2
    ON c2.relnamespace = n2.oid
WHERE n1.nspname = 'gold'
  AND c1.relname = 'financials_updated_vw'
  AND c2.relkind IN ('r','v','m','f')
ORDER BY source_schema, source_object;
