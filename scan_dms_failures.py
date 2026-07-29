
SELECT
    table_schema,
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    numeric_precision,
    numeric_scale,
    is_nullable
FROM information_schema.columns
WHERE table_schema='CLM'
ORDER BY table_name, ordinal_position;

Find Missing Columns

SELECT
    b.table_name,
    b.column_name
FROM bronze_columns b
LEFT JOIN silver_columns s
ON b.table_name = s.table_name
AND b.column_name = s.column_name
WHERE s.column_name IS NULL;

Compare Data Types

SELECT
    b.table_name,
    b.column_name,
    b.data_type AS bronze_type,
    s.data_type AS silver_type
FROM bronze_columns b
JOIN silver_columns s
ON b.table_name=s.table_name
AND b.column_name=s.column_name
WHERE b.data_type <> s.data_type;

Compare Primary Keys

SELECT
    tc.table_name,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
ON tc.constraint_name=kcu.constraint_name
WHERE tc.constraint_type='PRIMARY KEY'
AND tc.table_schema='CLM'
ORDER BY tc.table_name;


Compare Unique Constraints

SELECT
    tc.table_name,
    tc.constraint_name,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
ON tc.constraint_name=kcu.constraint_name
WHERE tc.constraint_type='UNIQUE'
AND tc.table_schema='CLM'
ORDER BY tc.table_name;

Compare Foreign Keys

SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
ON tc.constraint_name=kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
ON ccu.constraint_name=tc.constraint_name
WHERE tc.constraint_type='FOREIGN KEY'
AND tc.table_schema='CLM';

Compare Indexes

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname='CLM'
ORDER BY tablename;


Compare Check Constraints

SELECT
    conrelid::regclass AS table_name,
    conname,
    pg_get_constraintdef(oid)
FROM pg_constraint
WHERE contype='c';


Get ALL Constraints

SELECT
    tc.table_name,
    tc.constraint_type,
    tc.constraint_name,
    string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) AS columns
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu
ON tc.constraint_name=kcu.constraint_name
AND tc.table_schema=kcu.table_schema
WHERE tc.table_schema='CLM'
GROUP BY
    tc.table_name,
    tc.constraint_type,
    tc.constraint_name
ORDER BY
    tc.table_name,
    tc.constraint_type;

