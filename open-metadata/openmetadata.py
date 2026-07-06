import psycopg2
import requests


OM_BASE_URL = "http://localhost:8585/api/v1"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImFkbWluIiwicm9sZXMiOlsiQWRtaW4iXSwiZW1haWwiOiJhZG1pbkBvcGVuLW1ldGFkYXRhLm9yZyIsImlzQm90IjpmYWxzZSwidG9rZW5UeXBlIjoiUEVSU09OQUxfQUNDRVNTIiwidXNlcm5hbWUiOiJhZG1pbiIsInByZWZlcnJlZF91c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNzgzMjg5MzQwLCJleHAiOjE3OTEwNjUzNDB9.VgL9q1ogNdkltvkSAsVBd-T5Zu9xwI_uq82UkiQzuIqB_Pt-iSqETL1Bmnc2TRhYNWYwA-ixh0N6v5yZy_8zrZRiXf_mlLckYg8u89CRw2NRSnSZ3Q2PrqSl7pLkk_VmDWhj-6rjGDYoMAFwsbHdQbMsCV0M6H9Xmq00RNPvYD813WsOjYIX1WFgXEC_RmF7ftNHBCtoW8CcfCslYy2F400k3C1_TeOPUZfQ_CDc0wDQYDV0xJOlDTBE7Jjm_UGiw5rE2Et0bl-L7WKsQBtuwiKENPmrvD2oGY9G8XObpavfc_Gy8T4yPmnkBtkLsCzRnzg0ADjl0h9PhAqHQchsOg"

SERVICE_NAME = "Postgres DB"
DATABASE_NAME = "tinitiateai"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "tinitiateai",
    "user": "ti_dbuser",
    "password": "tiuser!23456",
}

HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json",
}


def get_table_names(schema_name: str) -> set[str]:
    sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (schema_name,))
            return {row[0] for row in cur.fetchall()}


def build_bronze_to_silver_edges():
    bronze_tables = get_table_names("bronze_layer")
    silver_tables = get_table_names("silver_layer")

    common_tables = bronze_tables.intersection(silver_tables)

    edges = []

    for table_name in sorted(common_tables):
        from_fqn = f"{SERVICE_NAME}.{DATABASE_NAME}.bronze_layer.{table_name}"
        to_fqn = f"{SERVICE_NAME}.{DATABASE_NAME}.silver_layer.{table_name}"
        edges.append((from_fqn, to_fqn))

    return edges


def get_table_by_fqn(fqn: str) -> dict:
    url = f"{OM_BASE_URL}/tables/name/{fqn}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 404:
        print(f"Not found in OpenMetadata: {fqn}")
        return None

    response.raise_for_status()
    return response.json()


def add_table_lineage(from_fqn: str, to_fqn: str):
    from_table = get_table_by_fqn(from_fqn)
    to_table = get_table_by_fqn(to_fqn)

    if not from_table or not to_table:
        return

    payload = {
        "edge": {
            "fromEntity": {
                "id": from_table["id"],
                "type": "table",
            },
            "toEntity": {
                "id": to_table["id"],
                "type": "table",
            },
            "description": "Auto-generated bronze to silver lineage",
        }
    }

    url = f"{OM_BASE_URL}/lineage"
    response = requests.put(url, json=payload, headers=HEADERS)

    if response.status_code in (200, 201):
        print(f"Added lineage: {from_fqn} -> {to_fqn}")
    else:
        print(f"Failed: {from_fqn} -> {to_fqn}")
        print(response.status_code, response.text)


def main():
    lineage_edges = build_bronze_to_silver_edges()

    print(f"Found {len(lineage_edges)} bronze → silver lineage edges")

    for source, target in lineage_edges:
        add_table_lineage(source, target)


if __name__ == "__main__":
    main()