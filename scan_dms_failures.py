SELECT pg_get_constraintdef(c.oid)
FROM pg_constraint c
JOIN pg_class t
  ON c.conrelid = t.oid
JOIN pg_namespace n
  ON t.relnamespace = n.oid
WHERE c.contype = 'f'
  AND n.nspname = 'CLM';

SELECT
    'ALTER TABLE "' || n.nspname || '"."' || t.relname || '" ADD CONSTRAINT "' ||
    c.conname || '" ' || pg_get_constraintdef(c.oid) || ';' AS ddl
FROM pg_constraint c
JOIN pg_class t
    ON c.conrelid = t.oid
JOIN pg_namespace n
    ON t.relnamespace = n.oid
WHERE c.contype = 'f'
  AND n.nspname = 'CLM'
ORDER BY t.relname;
