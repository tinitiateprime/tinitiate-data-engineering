WITH source_metadata AS
(
    SELECT
        trim(table_schema) AS table_schema,
        trim(table_name) AS table_name,
        trim(column_name) AS column_name,
        lower(trim(data_type)) AS source_data_type,

        CASE
            WHEN character_maximum_length IS NULL
              OR upper(trim(character_maximum_length)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(character_maximum_length)::integer
        END AS source_length,

        CASE
            WHEN numeric_precision IS NULL
              OR upper(trim(numeric_precision)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(numeric_precision)::integer
        END AS source_precision,

        CASE
            WHEN numeric_scale IS NULL
              OR upper(trim(numeric_scale)) IN ('', 'NULL')
            THEN NULL
            ELSE trim(numeric_scale)::integer
        END AS source_scale,

        upper(trim(is_nullable)) AS source_nullable

    FROM "CLM"."CLM_Table_name"
    WHERE upper(trim(table_schema)) = 'CLM'
)

SELECT
    s.table_schema,
    s.table_name,
    s.column_name,

    s.source_data_type,
    lower(trim(a.data_type)) AS silver_data_type,

    s.source_length,
    a.character_maximum_length AS silver_length,

    s.source_precision,
    a.numeric_precision AS silver_precision,

    s.source_scale,
    a.numeric_scale AS silver_scale,

    s.source_nullable,
    a.is_nullable AS silver_nullable,

    concat_ws(
        ', ',
        CASE
            WHEN s.source_data_type
                 IS DISTINCT FROM lower(trim(a.data_type))
            THEN 'DATA TYPE'
        END,

        CASE
            WHEN s.source_length
                 IS DISTINCT FROM a.character_maximum_length
            THEN 'LENGTH'
        END,

        CASE
            WHEN s.source_precision
                 IS DISTINCT FROM a.numeric_precision
            THEN 'PRECISION'
        END,

        CASE
            WHEN s.source_scale
                 IS DISTINCT FROM a.numeric_scale
            THEN 'SCALE'
        END,

        CASE
            WHEN s.source_nullable
                 IS DISTINCT FROM a.is_nullable
            THEN 'NULLABLE'
        END
    ) AS difference_type

FROM source_metadata s

JOIN information_schema.columns a
  ON lower(trim(a.table_schema)) = lower(s.table_schema)
 AND lower(trim(a.table_name)) = lower(s.table_name)
 AND lower(trim(a.column_name)) = lower(s.column_name)

WHERE
       s.source_data_type
           IS DISTINCT FROM lower(trim(a.data_type))

    OR s.source_length
           IS DISTINCT FROM a.character_maximum_length

    OR s.source_precision
           IS DISTINCT FROM a.numeric_precision

    OR s.source_scale
           IS DISTINCT FROM a.numeric_scale

    OR s.source_nullable
           IS DISTINCT FROM a.is_nullable

ORDER BY
    s.table_name,
    s.column_name;



AND lower(s.table_name) = 'clm_tcv'
AND lower(s.column_name) = 'active_flag'


SELECT
    m.table_name,
    m.column_name,
    m.data_type AS metadata_data_type,
    c.data_type AS silver_data_type,
    m.character_maximum_length AS metadata_length,
    c.character_maximum_length AS silver_length,
    m.is_nullable AS metadata_nullable,
    c.is_nullable AS silver_nullable
FROM "CLM"."CLM_Table_name" m
JOIN information_schema.columns c
  ON lower(trim(c.table_schema)) = lower(trim(m.table_schema))
 AND lower(trim(c.table_name)) = lower(trim(m.table_name))
 AND lower(trim(c.column_name)) = lower(trim(m.column_name))
WHERE lower(trim(m.table_name)) = 'clm_tcv'
  AND lower(trim(m.column_name)) = 'active_flag';

