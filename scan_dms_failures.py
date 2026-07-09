import sys

from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

#############################################################
# CONFIGURATION
#############################################################

# Bronze PostgreSQL
BRONZE_HOST = "<PUT_BRONZE_HOST_HERE>"
BRONZE_PORT = "5432"
BRONZE_DB = "gsapdi"

# Silver PostgreSQL
SILVER_HOST = "gsapdi-pg-mt-dm-dev.c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com"
SILVER_PORT = "5432"
SILVER_DB = "mtdm"

USERNAME = "jayathirth.kumsiravinder"
PASSWORD = "<PASSWORD>"

BRONZE_JDBC = f"jdbc:postgresql://{BRONZE_HOST}:{BRONZE_PORT}/{BRONZE_DB}"
SILVER_JDBC = f"jdbc:postgresql://{SILVER_HOST}:{SILVER_PORT}/{SILVER_DB}"

SOURCE_SCHEMA = "CLM"
TARGET_SCHEMA = "CLM"
STAGE_SCHEMA = "etl_stage"

TABLE = "clm_tcv"

PRIMARY_KEYS = [
    "award_no",
    "order_no",
    "mod_no"
]

jdbc_props = {
    "user": USERNAME,
    "password": PASSWORD,
    "driver": "org.postgresql.Driver"
}

#############################################################
# Helper to run SQL on Silver DB using JDBC
#############################################################

def run_sql(sql):
    conn = spark._sc._gateway.jvm.java.sql.DriverManager.getConnection(
        SILVER_JDBC,
        USERNAME,
        PASSWORD
    )
    stmt = conn.createStatement()
    try:
        stmt.execute(sql)
    finally:
        stmt.close()
        conn.close()


#############################################################
# STEP 1 - Read Bronze
#############################################################

print("Reading Bronze table...")

bronze_df = spark.read.jdbc(
    url=BRONZE_JDBC,
    table=f'"{SOURCE_SCHEMA}"."{TABLE}"',
    properties=jdbc_props
)

bronze_count = bronze_df.count()
print("Bronze Count:", bronze_count)

#############################################################
# STEP 2 - Truncate Stage
#############################################################

print("Truncating Stage table...")

run_sql(f'TRUNCATE TABLE "{STAGE_SCHEMA}"."{TABLE}_stage";')

print("Stage truncated.")

#############################################################
# STEP 3 - Load Stage
#############################################################

print("Loading Bronze data into Stage...")

bronze_df.write.jdbc(
    url=SILVER_JDBC,
    table=f'"{STAGE_SCHEMA}"."{TABLE}_stage"',
    mode="append",
    properties=jdbc_props
)

print("Loaded into Stage.")

#############################################################
# STEP 4 - Merge Stage into Silver
#############################################################

columns = bronze_df.columns

insert_cols = ", ".join([f'"{c}"' for c in columns])
select_cols = ", ".join([f'"{c}"' for c in columns])
conflict_cols = ", ".join([f'"{c}"' for c in PRIMARY_KEYS])

update_cols = []

for c in columns:
    if c not in PRIMARY_KEYS:
        update_cols.append(f'"{c}" = EXCLUDED."{c}"')

update_sql = ",\n    ".join(update_cols)

merge_sql = f"""
INSERT INTO "{TARGET_SCHEMA}"."{TABLE}"
(
    {insert_cols}
)
SELECT
    {select_cols}
FROM "{STAGE_SCHEMA}"."{TABLE}_stage"
ON CONFLICT ({conflict_cols})
DO UPDATE
SET
    {update_sql};
"""

print("Running Merge...")

run_sql(merge_sql)

print("Merge completed.")

#############################################################
# STEP 5 - Validation
#############################################################

silver_count_df = spark.read.jdbc(
    url=SILVER_JDBC,
    table=f'(SELECT COUNT(*) AS cnt FROM "{TARGET_SCHEMA}"."{TABLE}") x',
    properties=jdbc_props
)

silver_count = silver_count_df.collect()[0]["cnt"]

print("Silver Count:", silver_count)

print("Completed Successfully.")

job.commit()
