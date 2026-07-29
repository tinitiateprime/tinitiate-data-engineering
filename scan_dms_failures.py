WITH desired_columns AS
(
    SELECT
        trim(table_schema) AS table_schema,
        trim(table_name) AS table_name,
        trim(column_name) AS column_name
    FROM "CLM"."CLM_Table_name"
    WHERE upper(trim(table_schema)) = 'CLM'
)
SELECT
    COUNT(*) AS metadata_columns,
    COUNT(a.column_name) AS matched_silver_columns,
    COUNT(*) - COUNT(a.column_name) AS unmatched_columns
FROM desired_columns d
LEFT JOIN information_schema.columns a
    ON lower(trim(a.table_schema)) = lower(d.table_schema)
   AND lower(trim(a.table_name)) = lower(d.table_name)
   AND lower(trim(a.column_name)) = lower(d.column_name);


WITH desired_columns AS
(
    SELECT
        trim(table_schema) AS desired_schema,
        trim(table_name) AS desired_table,
        trim(column_name) AS desired_column,

        CASE lower(trim(data_type))
            WHEN 'varchar' THEN 'character varying'
            WHEN 'char' THEN 'character'
            WHEN 'decimal' THEN 'numeric'
            WHEN 'timestamp' THEN 'timestamp without time zone'
            ELSE lower(trim(data_type))
        END AS desired_data_type,

        CASE
            WHEN character_maximum_length IS NULL
              OR upper(trim(character_maximum_length)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(character_maximum_length)::integer
        END AS desired_length,

        CASE
            WHEN numeric_precision IS NULL
              OR upper(trim(numeric_precision)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(numeric_precision)::integer
        END AS desired_precision,

        CASE
            WHEN numeric_scale IS NULL
              OR upper(trim(numeric_scale)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(numeric_scale)::integer
        END AS desired_scale,

        upper(trim(is_nullable)) AS desired_nullable

    FROM "CLM"."CLM_Table_name"
    WHERE upper(trim(table_schema)) = 'CLM'
),

comparison AS
(
    SELECT
        a.table_schema,
        a.table_name,
        a.column_name,

        d.desired_data_type,
        a.data_type AS actual_data_type,

        d.desired_length,
        a.character_maximum_length AS actual_length,

        d.desired_precision,
        a.numeric_precision AS actual_precision,

        d.desired_scale,
        a.numeric_scale AS actual_scale,

        d.desired_nullable,
        a.is_nullable AS actual_nullable,

        CASE
            WHEN d.desired_data_type = 'character varying'
                 AND d.desired_length IS NOT NULL
            THEN format('varchar(%s)', d.desired_length)

            WHEN d.desired_data_type = 'character varying'
            THEN 'varchar'

            WHEN d.desired_data_type = 'character'
                 AND d.desired_length IS NOT NULL
            THEN format('char(%s)', d.desired_length)

            WHEN d.desired_data_type = 'character'
            THEN 'char'

            WHEN d.desired_data_type = 'numeric'
                 AND d.desired_precision IS NOT NULL
                 AND d.desired_scale IS NOT NULL
            THEN format(
                'numeric(%s,%s)',
                d.desired_precision,
                d.desired_scale
            )

            WHEN d.desired_data_type = 'numeric'
                 AND d.desired_precision IS NOT NULL
            THEN format('numeric(%s)', d.desired_precision)

            ELSE d.desired_data_type
        END AS desired_complete_type

    FROM desired_columns d
    JOIN information_schema.columns a
      ON lower(trim(a.table_schema)) = lower(d.desired_schema)
     AND lower(trim(a.table_name)) = lower(d.desired_table)
     AND lower(trim(a.column_name)) = lower(d.desired_column)
),

differences AS
(
    SELECT *,
        CASE
            WHEN actual_data_type IS DISTINCT FROM desired_data_type
            THEN 'DATA TYPE'

            WHEN desired_data_type IN ('character varying', 'character')
                 AND actual_length IS DISTINCT FROM desired_length
            THEN 'LENGTH'

            WHEN desired_data_type = 'numeric'
                 AND desired_precision IS NOT NULL
                 AND actual_precision IS DISTINCT FROM desired_precision
            THEN 'PRECISION'

            WHEN desired_data_type = 'numeric'
                 AND desired_scale IS NOT NULL
                 AND actual_scale IS DISTINCT FROM desired_scale
            THEN 'SCALE'

            WHEN desired_nullable IS DISTINCT FROM actual_nullable
            THEN 'NULLABLE'
        END AS difference_type

    FROM comparison

    WHERE
        actual_data_type IS DISTINCT FROM desired_data_type

        OR (
            desired_data_type IN ('character varying', 'character')
            AND actual_length IS DISTINCT FROM desired_length
        )

        OR (
            desired_data_type = 'numeric'
            AND desired_precision IS NOT NULL
            AND actual_precision IS DISTINCT FROM desired_precision
        )

        OR (
            desired_data_type = 'numeric'
            AND desired_scale IS NOT NULL
            AND actual_scale IS DISTINCT FROM desired_scale
        )

        OR desired_nullable IS DISTINCT FROM actual_nullable
)

SELECT
    table_schema,
    table_name,
    column_name,
    difference_type,

    desired_data_type,
    actual_data_type,

    desired_length,
    actual_length,

    desired_precision,
    actual_precision,

    desired_scale,
    actual_scale,

    desired_nullable,
    actual_nullable,

    CASE
        WHEN difference_type IN (
            'DATA TYPE',
            'LENGTH',
            'PRECISION',
            'SCALE'
        )
        THEN format(
            'ALTER TABLE %I.%I ALTER COLUMN %I TYPE %s USING %I::%s;',
            table_schema,
            table_name,
            column_name,
            desired_complete_type,
            column_name,
            desired_complete_type
        )

        WHEN difference_type = 'NULLABLE'
             AND desired_nullable = 'NO'
        THEN format(
            'ALTER TABLE %I.%I ALTER COLUMN %I SET NOT NULL;',
            table_schema,
            table_name,
            column_name
        )

        WHEN difference_type = 'NULLABLE'
             AND desired_nullable = 'YES'
        THEN format(
            'ALTER TABLE %I.%I ALTER COLUMN %I DROP NOT NULL;',
            table_schema,
            table_name,
            column_name
        )
    END AS alter_statement

FROM differences
ORDER BY
    table_schema,
    table_name,
    column_name;



 SELECT
    d.table_schema,
    d.table_name,
    d.column_name
FROM "CLM"."CLM_Table_name" d
LEFT JOIN information_schema.columns a
    ON lower(trim(a.table_schema)) = lower(trim(d.table_schema))
   AND lower(trim(a.table_name)) = lower(trim(d.table_name))
   AND lower(trim(a.column_name)) = lower(trim(d.column_name))
WHERE upper(trim(d.table_schema)) = 'CLM'
  AND a.column_name IS NULL
ORDER BY d.table_name, d.column_name;   
