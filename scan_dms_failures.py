MV_QUERY = """
SELECT
    schemaname,
    matviewname,
    pg_get_viewdef(
        (
            quote_ident(schemaname)
            || '.'
            || quote_ident(matviewname)
        )::regclass,
        true
    ) AS definition
FROM pg_matviews
WHERE schemaname = %s
ORDER BY matviewname;
"""
