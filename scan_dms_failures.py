get the list of materialized views:

SELECT
    schemaname,
    matviewname
FROM pg_matviews
WHERE schemaname = 'mtdm'
ORDER BY matviewname;

get the SQL definition for all of them:

SELECT
    schemaname,
    matviewname,
    pg_get_viewdef(
        format('%I.%I', schemaname, matviewname)::regclass,
        true
    ) AS mv_definition
FROM pg_matviews
WHERE schemaname = 'mtdm'
ORDER BY matviewname;

For each MV, create a file like:
SQL Scripts/
└── MVs/
    ├── contract.sql
    ├── project_financial.sql
    ├── project_status.sql
    └── ...

put this structure in each file:

CREATE MATERIALIZED VIEW mtdm.<mv_name> AS

<definition returned by pg_get_viewdef>

WITH DATA;

MVs version-controlled properly, so also get their indexes:
SELECT
    schemaname,
    matviewname,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'mtdm'
  AND tablename IN (
      SELECT matviewname
      FROM pg_matviews
      WHERE schemaname = 'mtdm'
  )
ORDER BY matviewname, indexname;


generate the CREATE statements automatically

SELECT
    '-- =============================================' || E'\n' ||
    '-- Materialized View: ' || schemaname || '.' || matviewname || E'\n' ||
    '-- =============================================' || E'\n\n' ||
    'CREATE MATERIALIZED VIEW ' ||
    quote_ident(schemaname) || '.' || quote_ident(matviewname) ||
    ' AS' || E'\n\n' ||
    pg_get_viewdef(
        format('%I.%I', schemaname, matviewname)::regclass,
        true
    ) ||
    E'\n\nWITH DATA;' AS ddl
FROM pg_matviews
WHERE schemaname = 'mtdm'
ORDER BY matviewname;


generate one complete CREATE script per materialized view, including all indexes belonging to that MV.  


SELECT
    mv.schemaname,
    mv.matviewname,

    '-- =====================================================' || E'\n' ||
    '-- Materialized View: ' ||
    quote_ident(mv.schemaname) || '.' ||
    quote_ident(mv.matviewname) || E'\n' ||
    '-- =====================================================' || E'\n\n' ||

    'CREATE MATERIALIZED VIEW ' ||
    quote_ident(mv.schemaname) || '.' ||
    quote_ident(mv.matviewname) ||
    ' AS' || E'\n\n' ||

    pg_get_viewdef(
        format('%I.%I', mv.schemaname, mv.matviewname)::regclass,
        true
    ) ||

    E'\n\nWITH DATA;' ||

    E'\n\n-- =====================================================' ||
    E'\n-- Indexes' ||
    E'\n-- =====================================================' ||
    E'\n\n' ||

    COALESCE(
        (
            SELECT string_agg(
                idx.indexdef || ';',
                E'\n\n'
                ORDER BY idx.indexname
            )
            FROM pg_indexes idx
            WHERE idx.schemaname = mv.schemaname
              AND idx.tablename = mv.matviewname
        ),
        '-- No indexes defined for this materialized view'
    ) ||

    E'\n' AS complete_ddl

FROM pg_matviews mv
WHERE mv.schemaname = 'mtdm'
ORDER BY mv.matviewname;
