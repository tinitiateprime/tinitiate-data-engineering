CREATE TEMP TABLE row_counts (table_name text, row_count bigint);

DO $$
DECLARE
    r RECORD;
    cnt BIGINT;
BEGIN
    FOR r IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'your_schema_name'
    LOOP
        EXECUTE format('SELECT count(*) FROM %I.%I', 'your_schema_name', r.tablename) INTO cnt;
        INSERT INTO row_counts VALUES (r.tablename, cnt);
    END LOOP;
END $$;

SELECT * FROM row_counts ORDER BY row_count DESC;
