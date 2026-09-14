SELECT
    schemaname,
    matviewname,
    definition
FROM pg_matviews
WHERE schemaname = 'gold'
  AND matviewname = 'financials_updated_vw';
