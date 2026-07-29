WITH desired_columns AS
(
    SELECT
        table_schema,
        table_name,
        column_name,
        lower(data_type) AS data_type,
        NULLIF(character_maximum_length, '')::integer
            AS character_maximum_length,
        NULLIF(numeric_precision, '')::integer
            AS numeric_precision,
        NULLIF(numeric_scale, '')::integer
            AS numeric_scale,
        upper(is_nullable) AS is_nullable
    FROM "CLM"."CLM_Table_name"
    WHERE table_schema = 'CLM'
),
column_comparison AS
(
    SELECT
        d.table_schema,
        d.table_name,
        d.column_name,

        d.data_type AS desired_data_type,
        a.data_type AS actual_data_type,

        d.character_maximum_length AS desired_length,
        a.character_maximum_length AS actual_length,

        d.numeric_precision AS desired_precision,
        a.numeric_precision AS actual_precision,

        d.numeric_scale AS desired_scale,
        a.numeric_scale AS actual_scale,

        d.is_nullable AS desired_nullable,
        a.is_nullable AS actual_nullable,

        CASE
            WHEN d.data_type IN ('character varying', 'varchar')
                 AND d.character_maximum_length IS NOT NULL
            THEN format(
                'varchar(%s)',
                d.character_maximum_length
            )

            WHEN d.data_type IN ('character', 'char')
                 AND d.character_maximum_length IS NOT NULL
            THEN format(
                'char(%s)',
                d.character_maximum_length
            )

            WHEN d.data_type IN ('numeric', 'decimal')
                 AND d.numeric_precision IS NOT NULL
                 AND d.numeric_scale IS NOT NULL
            THEN format(
                'numeric(%s,%s)',
                d.numeric_precision,
                d.numeric_scale
            )

            WHEN d.data_type IN ('numeric', 'decimal')
                 AND d.numeric_precision IS NOT NULL
            THEN format(
                'numeric(%s)',
                d.numeric_precision
            )

            ELSE d.data_type
        END AS desired_complete_type
    FROM desired_columns d
    JOIN information_schema.columns a
      ON a.table_schema = d.table_schema
     AND a.table_name = d.table_name
     AND a.column_name = d.column_name
)
SELECT
    format(
        'ALTER TABLE %I.%I ALTER COLUMN %I TYPE %s USING %I::%s;',
        table_schema,
        table_name,
        column_name,
        desired_complete_type,
        column_name,
        desired_complete_type
    ) AS alter_statement
FROM column_comparison
WHERE actual_data_type IS DISTINCT FROM desired_data_type
   OR actual_length IS DISTINCT FROM desired_length
   OR actual_precision IS DISTINCT FROM desired_precision
   OR actual_scale IS DISTINCT FROM desired_scale
ORDER BY table_name, column_name;


Generate nullable/not-null changes

WITH desired_columns AS
(
    SELECT
        table_schema,
        table_name,
        column_name,
        upper(is_nullable) AS desired_nullable
    FROM "CLM"."CLM_Table_name"
    WHERE table_schema = 'CLM'
)
SELECT
    CASE
        WHEN d.desired_nullable = 'NO'
             AND a.is_nullable = 'YES'
        THEN format(
            'ALTER TABLE %I.%I ALTER COLUMN %I SET NOT NULL;',
            d.table_schema,
            d.table_name,
            d.column_name
        )

        WHEN d.desired_nullable = 'YES'
             AND a.is_nullable = 'NO'
        THEN format(
            'ALTER TABLE %I.%I ALTER COLUMN %I DROP NOT NULL;',
            d.table_schema,
            d.table_name,
            d.column_name
        )
    END AS alter_statement
FROM desired_columns d
JOIN information_schema.columns a
  ON a.table_schema = d.table_schema
 AND a.table_name = d.table_name
 AND a.column_name = d.column_name
WHERE d.desired_nullable IS DISTINCT FROM a.is_nullable
ORDER BY d.table_name, d.column_name;
    
