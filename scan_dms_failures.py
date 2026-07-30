1. Generate sequence creation DDL

SELECT
    format(
        'CREATE SEQUENCE IF NOT EXISTS %I.%I
         AS %s
         INCREMENT BY %s
         MINVALUE %s
         MAXVALUE %s
         START WITH %s
         CACHE %s
         %s;',
        s.schemaname,
        s.sequencename,
        s.data_type,
        s.increment_by,
        s.min_value,
        s.max_value,
        s.start_value,
        s.cache_size,
        CASE
            WHEN s.cycle THEN 'CYCLE'
            ELSE 'NO CYCLE'
        END
    ) AS ddl
FROM pg_sequences s
WHERE s.schemaname = 'CLM'
ORDER BY s.sequencename;

2. Generate sequence ownership and default DDL

SELECT
    format(
        'ALTER SEQUENCE %I.%I OWNED BY %I.%I.%I;',
        seq_ns.nspname,
        seq.relname,
        tbl_ns.nspname,
        tbl.relname,
        col.attname
    )
    || E'\n'
    ||
    format(
        'ALTER TABLE %I.%I ALTER COLUMN %I SET DEFAULT nextval(%L::regclass);',
        tbl_ns.nspname,
        tbl.relname,
        col.attname,
        format('%I.%I', seq_ns.nspname, seq.relname)
    ) AS ddl
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
ORDER BY tbl.relname, col.attname;

3. Generate primary key DDL

SELECT
    format(
        'ALTER TABLE %I.%I ADD CONSTRAINT %I %s;',
        n.nspname,
        t.relname,
        c.conname,
        pg_get_constraintdef(c.oid)
    ) AS ddl
FROM pg_constraint c
JOIN pg_class t
    ON t.oid = c.conrelid
JOIN pg_namespace n
    ON n.oid = t.relnamespace
WHERE c.contype = 'p'
  AND n.nspname = 'CLM'
ORDER BY t.relname, c.conname;


SELECT
    format(
        'ALTER TABLE %I.%I DROP CONSTRAINT IF EXISTS %I;
ALTER TABLE %I.%I ADD CONSTRAINT %I %s;',
        n.nspname,
        t.relname,
        c.conname,
        n.nspname,
        t.relname,
        c.conname,
        pg_get_constraintdef(c.oid)
    ) AS ddl
FROM pg_constraint c
JOIN pg_class t
    ON t.oid = c.conrelid
JOIN pg_namespace n
    ON n.oid = t.relnamespace
WHERE c.contype = 'p'
  AND n.nspname = 'CLM'
ORDER BY t.relname, c.conname;


4. Generate unique constraint DDL

SELECT
    format(
        'ALTER TABLE %I.%I ADD CONSTRAINT %I %s;',
        n.nspname,
        t.relname,
        c.conname,
        pg_get_constraintdef(c.oid)
    ) AS ddl
FROM pg_constraint c
JOIN pg_class t
    ON t.oid = c.conrelid
JOIN pg_namespace n
    ON n.oid = t.relnamespace
WHERE c.contype = 'u'
  AND n.nspname = 'CLM'
ORDER BY t.relname, c.conname;


5. Generate foreign key DDL

SELECT
    format(
        'ALTER TABLE %I.%I ADD CONSTRAINT %I %s;',
        n.nspname,
        t.relname,
        c.conname,
        pg_get_constraintdef(c.oid)
    ) AS ddl
FROM pg_constraint c
JOIN pg_class t
    ON t.oid = c.conrelid
JOIN pg_namespace n
    ON n.oid = t.relnamespace
WHERE c.contype = 'f'
  AND n.nspname = 'CLM'
ORDER BY t.relname, c.conname;


SELECT
    format(
        'ALTER TABLE %I.%I ADD CONSTRAINT %I %s NOT VALID;',
        n.nspname,
        t.relname,
        c.conname,
        pg_get_constraintdef(c.oid)
    ) AS ddl
FROM pg_constraint c
JOIN pg_class t
    ON t.oid = c.conrelid
JOIN pg_namespace n
    ON n.oid = t.relnamespace
WHERE c.contype = 'f'
  AND n.nspname = 'CLM'
ORDER BY t.relname, c.conname;


6. Generate check constraints

SELECT
    format(
        'ALTER TABLE %I.%I ADD CONSTRAINT %I %s;',
        n.nspname,
        t.relname,
        c.conname,
        pg_get_constraintdef(c.oid)
    ) AS ddl
FROM pg_constraint c
JOIN pg_class t
    ON t.oid = c.conrelid
JOIN pg_namespace n
    ON n.oid = t.relnamespace
WHERE c.contype = 'c'
  AND n.nspname = 'CLM'
ORDER BY t.relname, c.conname;


7. Generate indexes not created by constraints

SELECT
    pg_get_indexdef(i.indexrelid) || ';' AS ddl
FROM pg_index i
JOIN pg_class idx
    ON idx.oid = i.indexrelid
JOIN pg_class tbl
    ON tbl.oid = i.indrelid
JOIN pg_namespace n
    ON n.oid = tbl.relnamespace
LEFT JOIN pg_constraint c
    ON c.conindid = i.indexrelid
WHERE n.nspname = 'CLM'
  AND c.oid IS NULL
  AND NOT i.indisprimary
ORDER BY tbl.relname, idx.relname;

8. Generate column defaults not related to sequences

DEFAULT 'Y'
DEFAULT CURRENT_TIMESTAMP
DEFAULT false

SELECT
    format(
        'ALTER TABLE %I.%I ALTER COLUMN %I SET DEFAULT %s;',
        table_schema,
        table_name,
        column_name,
        column_default
    ) AS ddl
FROM information_schema.columns
WHERE table_schema = 'CLM'
  AND column_default IS NOT NULL
  AND column_default NOT LIKE 'nextval(%'
ORDER BY table_name, ordinal_position;


9. Synchronize sequences in Silver

SELECT
    format(
        'SELECT setval(
            %L::regclass,
            COALESCE((SELECT MAX(%I) FROM %I.%I), 0) + 1,
            false
        );',
        format('%I.%I', seq_ns.nspname, seq.relname),
        col.attname,
        tbl_ns.nspname,
        tbl.relname
    ) AS ddl
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
ORDER BY tbl.relname, col.attname;

10. Check for orphan records before adding foreign keys



