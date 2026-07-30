SELECT
    format(
        'SELECT setval(
    %L::regclass,
    COALESCE(
        (SELECT MAX(%I) FROM %I.%I),
        0
    ) + 1,
    false
);',
        format('%I.%I', seq_ns.nspname, seq.relname),
        col.attname,
        tbl_ns.nspname,
        tbl.relname
    ) AS setval_statement
FROM pg_class seq
JOIN pg_namespace seq_ns
    ON seq_ns.oid = seq.relnamespace
JOIN pg_depend dep
    ON dep.objid = seq.oid
   AND dep.deptype IN ('a', 'i')
JOIN pg_class tbl
    ON tbl.oid = dep.refobjid
JOIN pg_namespace tbl_ns
    ON tbl_ns.oid = tbl.relnamespace
JOIN pg_attribute col
    ON col.attrelid = tbl.oid
   AND col.attnum = dep.refobjsubid
WHERE seq.relkind = 'S'
  AND seq_ns.nspname = 'CLM'
  AND tbl_ns.nspname = 'CLM'
ORDER BY tbl.relname, col.attname;


SELECT string_agg(
    format(
        'SELECT setval(
    %L::regclass,
    COALESCE(
        (SELECT MAX(%I) FROM %I.%I),
        0
    ) + 1,
    false
);',
        format('%I.%I', seq_ns.nspname, seq.relname),
        col.attname,
        tbl_ns.nspname,
        tbl.relname
    ),
    E'\n\n'
    ORDER BY tbl.relname, col.attname
) AS complete_setval_script
FROM pg_class seq
JOIN pg_namespace seq_ns
    ON seq_ns.oid = seq.relnamespace
JOIN pg_depend dep
    ON dep.objid = seq.oid
   AND dep.deptype IN ('a', 'i')
JOIN pg_class tbl
    ON tbl.oid = dep.refobjid
JOIN pg_namespace tbl_ns
    ON tbl_ns.oid = tbl.relnamespace
JOIN pg_attribute col
    ON col.attrelid = tbl.oid
   AND col.attnum = dep.refobjsubid
WHERE seq.relkind = 'S'
  AND seq_ns.nspname = 'CLM'
  AND tbl_ns.nspname = 'CLM';
