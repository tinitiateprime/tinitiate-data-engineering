SELECT
    'METADATA_TABLE' AS source,
    trim(table_schema) AS table_schema,
    trim(table_name) AS table_name,
    trim(column_name) AS column_name,
    trim(data_type) AS data_type,
    character_maximum_length,
    numeric_precision,
    numeric_scale,
    is_nullable
FROM "CLM"."CLM_Table_name"
WHERE lower(trim(table_schema)) = 'clm'
  AND lower(trim(table_name)) = 'clm_tcv'
  AND lower(trim(column_name)) = 'active_flag'

UNION ALL

SELECT
    'SILVER_ACTUAL' AS source,
    table_schema,
    table_name,
    column_name,
    data_type,
    character_maximum_length::varchar,
    numeric_precision::varchar,
    numeric_scale::varchar,
    is_nullable
FROM information_schema.columns
WHERE lower(table_schema) = 'clm'
  AND lower(table_name) = 'clm_tcv'
  AND lower(column_name) = 'active_flag';


  SELECT DISTINCT
    table_schema,
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE lower(table_schema) = 'clm'
  AND lower(column_name) = 'active_flag'
ORDER BY table_name;

SELECT DISTINCT
    table_schema,
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM "CLM"."CLM_Table_name"
WHERE lower(trim(table_schema)) = 'clm'
  AND lower(trim(column_name)) = 'active_flag'
ORDER BY table_name;

WITH metadata AS
(
    SELECT
        trim(table_schema) AS table_schema,
        trim(table_name) AS table_name,
        trim(column_name) AS column_name,
        lower(trim(data_type)) AS metadata_data_type,

        CASE
            WHEN character_maximum_length IS NULL
              OR upper(trim(character_maximum_length)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(character_maximum_length)::integer
        END AS metadata_length,

        CASE
            WHEN numeric_precision IS NULL
              OR upper(trim(numeric_precision)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(numeric_precision)::integer
        END AS metadata_precision,

        CASE
            WHEN numeric_scale IS NULL
              OR upper(trim(numeric_scale)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(numeric_scale)::integer
        END AS metadata_scale,

        upper(trim(is_nullable)) AS metadata_nullable

    FROM "CLM"."CLM_Table_name"
    WHERE upper(trim(table_schema)) = 'CLM'
),

actual_silver AS
(
    SELECT
        table_schema,
        table_name,
        column_name,
        lower(data_type) AS silver_data_type,
        character_maximum_length AS silver_length,
        numeric_precision AS silver_precision,
        numeric_scale AS silver_scale,
        is_nullable AS silver_nullable
    FROM information_schema.columns
    WHERE upper(table_schema) = 'CLM'
),

comparison AS
(
    SELECT
        m.table_schema,
        m.table_name,
        m.column_name,

        m.metadata_data_type,
        s.silver_data_type,

        m.metadata_length,
        s.silver_length,

        m.metadata_precision,
        s.silver_precision,

        m.metadata_scale,
        s.silver_scale,

        m.metadata_nullable,
        s.silver_nullable

    FROM metadata m
    JOIN actual_silver s
      ON lower(m.table_schema) = lower(s.table_schema)
     AND lower(m.table_name) = lower(s.table_name)
     AND lower(m.column_name) = lower(s.column_name)
)

SELECT
    table_schema,
    table_name,
    column_name,

    metadata_data_type,
    silver_data_type,

    metadata_length,
    silver_length,

    metadata_precision,
    silver_precision,

    metadata_scale,
    silver_scale,

    metadata_nullable,
    silver_nullable,

    concat_ws(
        ', ',
        CASE
            WHEN metadata_data_type IS DISTINCT FROM silver_data_type
            THEN 'DATA TYPE'
        END,
        CASE
            WHEN metadata_length IS DISTINCT FROM silver_length
            THEN 'LENGTH'
        END,
        CASE
            WHEN metadata_precision IS DISTINCT FROM silver_precision
            THEN 'PRECISION'
        END,
        CASE
            WHEN metadata_scale IS DISTINCT FROM silver_scale
            THEN 'SCALE'
        END,
        CASE
            WHEN metadata_nullable IS DISTINCT FROM silver_nullable
            THEN 'NULLABLE'
        END
    ) AS differences

FROM comparison

WHERE metadata_data_type IS DISTINCT FROM silver_data_type
   OR metadata_length IS DISTINCT FROM silver_length
   OR metadata_precision IS DISTINCT FROM silver_precision
   OR metadata_scale IS DISTINCT FROM silver_scale
   OR metadata_nullable IS DISTINCT FROM silver_nullable

ORDER BY table_name, column_name;
