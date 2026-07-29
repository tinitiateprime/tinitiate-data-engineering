WITH desired_columns AS
(
    SELECT
        trim(table_schema) AS table_schema,
        trim(table_name) AS table_name,
        trim(column_name) AS column_name,
        lower(trim(data_type)) AS data_type,

        CASE
            WHEN character_maximum_length IS NULL
                 OR upper(trim(character_maximum_length)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(character_maximum_length)::integer
        END AS character_maximum_length,

        CASE
            WHEN numeric_precision IS NULL
                 OR upper(trim(numeric_precision)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(numeric_precision)::integer
        END AS numeric_precision,

        CASE
            WHEN numeric_scale IS NULL
                 OR upper(trim(numeric_scale)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(numeric_scale)::integer
        END AS numeric_scale,

        upper(trim(is_nullable)) AS is_nullable

    FROM "CLM"."CLM_Table_name"
    WHERE trim(table_schema) = 'CLM'
),

comparison AS
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

            WHEN d.data_type IN ('character varying', 'varchar')
                 AND d.character_maximum_length IS NULL
            THEN 'varchar'

            WHEN d.data_type IN ('character', 'char')
                 AND d.character_maximum_length IS NOT NULL
            THEN format(
                'char(%s)',
                d.character_maximum_length
            )

            WHEN d.data_type IN ('character', 'char')
                 AND d.character_maximum_length IS NULL
            THEN 'char'

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
                 AND d.numeric_scale IS NULL
            THEN format(
                'numeric(%s)',
                d.numeric_precision
            )

            WHEN d.data_type IN ('timestamp without time zone', 'timestamp')
            THEN 'timestamp without time zone'

            WHEN d.data_type = 'timestamp with time zone'
            THEN 'timestamp with time zone'

            WHEN d.data_type = 'double precision'
            THEN 'double precision'

            WHEN d.data_type = 'integer'
            THEN 'integer'

            WHEN d.data_type = 'bigint'
            THEN 'bigint'

            WHEN d.data_type = 'smallint'
            THEN 'smallint'

            WHEN d.data_type = 'boolean'
            THEN 'boolean'

            WHEN d.data_type = 'date'
            THEN 'date'

            WHEN d.data_type = 'text'
            THEN 'text'

            ELSE d.data_type
        END AS desired_complete_type

    FROM desired_columns d

    JOIN information_schema.columns a
      ON a.table_schema = d.table_schema
     AND a.table_name = d.table_name
     AND a.column_name = d.column_name
),

alter_type_statements AS
(
    SELECT
        table_schema,
        table_name,
        column_name,
        1 AS statement_order,

        format(
            'ALTER TABLE %I.%I ALTER COLUMN %I TYPE %s USING %I::%s;',
            table_schema,
            table_name,
            column_name,
            desired_complete_type,
            column_name,
            desired_complete_type
        ) AS alter_statement

    FROM comparison

    WHERE
        lower(actual_data_type) IS DISTINCT FROM lower(desired_data_type)

        OR CASE
               WHEN desired_data_type IN
                    ('character varying', 'varchar', 'character', 'char')
               THEN actual_length
           END
           IS DISTINCT FROM
           CASE
               WHEN desired_data_type IN
                    ('character varying', 'varchar', 'character', 'char')
               THEN desired_length
           END

        OR CASE
               WHEN desired_data_type IN ('numeric', 'decimal')
               THEN actual_precision
           END
           IS DISTINCT FROM
           CASE
               WHEN desired_data_type IN ('numeric', 'decimal')
               THEN desired_precision
           END

        OR CASE
               WHEN desired_data_type IN ('numeric', 'decimal')
               THEN actual_scale
           END
           IS DISTINCT FROM
           CASE
               WHEN desired_data_type IN ('numeric', 'decimal')
               THEN desired_scale
           END
),

alter_nullable_statements AS
(
    SELECT
        table_schema,
        table_name,
        column_name,
        2 AS statement_order,

        CASE
            WHEN desired_nullable = 'NO'
                 AND actual_nullable = 'YES'
            THEN format(
                'ALTER TABLE %I.%I ALTER COLUMN %I SET NOT NULL;',
                table_schema,
                table_name,
                column_name
            )

            WHEN desired_nullable = 'YES'
                 AND actual_nullable = 'NO'
            THEN format(
                'ALTER TABLE %I.%I ALTER COLUMN %I DROP NOT NULL;',
                table_schema,
                table_name,
                column_name
            )
        END AS alter_statement

    FROM comparison

    WHERE desired_nullable IN ('YES', 'NO')
      AND desired_nullable IS DISTINCT FROM actual_nullable
)

SELECT
    table_schema,
    table_name,
    column_name,
    alter_statement
FROM
(
    SELECT *
    FROM alter_type_statements

    UNION ALL

    SELECT *
    FROM alter_nullable_statements
) x
WHERE alter_statement IS NOT NULL
ORDER BY
    table_schema,
    table_name,
    column_name,
    statement_order;
