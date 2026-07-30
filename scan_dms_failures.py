WITH sequence_info AS
(
    SELECT
        s.sequence_schema,
        s.sequence_name,
        s.data_type,
        s.increment,
        s.minimum_value,
        s.maximum_value,
        s.start_value,
        s.cycle_option,

        ps.seqcache AS cache_size,

        dep_table.relname AS table_name,
        dep_column.attname AS column_name

    FROM information_schema.sequences s

    JOIN pg_class seq
      ON seq.relname = s.sequence_name
     AND seq.relkind = 'S'

    JOIN pg_namespace ns
      ON ns.oid = seq.relnamespace
     AND ns.nspname = s.sequence_schema

    JOIN pg_sequence ps
      ON ps.seqrelid = seq.oid

    LEFT JOIN pg_depend dep
      ON dep.objid = seq.oid
     AND dep.deptype IN ('a', 'i')

    LEFT JOIN pg_class dep_table
      ON dep_table.oid = dep.refobjid

    LEFT JOIN pg_attribute dep_column
      ON dep_column.attrelid = dep.refobjid
     AND dep_column.attnum = dep.refobjsubid

    WHERE s.sequence_schema = 'CLM'
)

SELECT
    sequence_schema,
    sequence_name,
    table_name,
    column_name,

    format(
        'CREATE SEQUENCE IF NOT EXISTS %I.%I
AS %s
INCREMENT BY %s
MINVALUE %s
MAXVALUE %s
START WITH %s
CACHE %s
%s;',
        sequence_schema,
        sequence_name,
        data_type,
        increment,
        minimum_value,
        maximum_value,
        start_value,
        cache_size,
        CASE
            WHEN cycle_option = 'YES' THEN 'CYCLE'
            ELSE 'NO CYCLE'
        END
    )
    ||
    CASE
        WHEN table_name IS NOT NULL
         AND column_name IS NOT NULL
        THEN format(
            E'\nALTER SEQUENCE %I.%I OWNED BY %I.%I.%I;',
            sequence_schema,
            sequence_name,
            sequence_schema,
            table_name,
            column_name
        )
        ELSE ''
    END
    ||
    CASE
        WHEN table_name IS NOT NULL
         AND column_name IS NOT NULL
        THEN format(
            E'\nALTER TABLE %I.%I ALTER COLUMN %I SET DEFAULT nextval(%L::regclass);',
            sequence_schema,
            table_name,
            column_name,
            format('%I.%I', sequence_schema, sequence_name)
        )
        ELSE ''
    END AS sequence_ddl

FROM sequence_info
ORDER BY sequence_name;

SELECT setval(
    '"CLM".contract_header_header_id_seq'::regclass,
    COALESCE(
        (SELECT MAX(header_id) FROM "CLM".contract_header),
        0
    ) + 1,
    false
);
