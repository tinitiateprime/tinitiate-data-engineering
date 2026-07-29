BEGIN;

CREATE SEQUENCE IF NOT EXISTS "CLM".contract_header_header_id_seq;

ALTER SEQUENCE "CLM".contract_header_header_id_seq
OWNED BY "CLM".contract_header.header_id;

ALTER TABLE "CLM".contract_header
ALTER COLUMN header_id
SET DEFAULT nextval(
    '"CLM".contract_header_header_id_seq'::regclass
);

SELECT setval(
    '"CLM".contract_header_header_id_seq'::regclass,
    COALESCE(
        (SELECT MAX(header_id) FROM "CLM".contract_header),
        0
    ) + 1,
    false
);

COMMIT;
