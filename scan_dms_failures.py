import sys

from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


#############################################################
# GLUE INITIALIZATION
#############################################################

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
BRONZE_HOST = (
    "gsapdi-pg-stg."
    "c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com"
)
BRONZE_PORT = "5432"
BRONZE_DB = "gsapdi"

BRONZE_USERNAME = "<BRONZE_USERNAME>"
BRONZE_PASSWORD = "<BRONZE_PASSWORD>"


# Silver PostgreSQL
SILVER_HOST = (
    "gsapdi-pg-mt-dm-dev."
    "c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com"
)
SILVER_PORT = "5432"
SILVER_DB = "mtdm"

SILVER_USERNAME = "<SILVER_USERNAME>"
SILVER_PASSWORD = "<SILVER_PASSWORD>"


# JDBC URLs
BRONZE_JDBC = (
    f"jdbc:postgresql://"
    f"{BRONZE_HOST}:{BRONZE_PORT}/{BRONZE_DB}"
)

SILVER_JDBC = (
    f"jdbc:postgresql://"
    f"{SILVER_HOST}:{SILVER_PORT}/{SILVER_DB}"
)


# Schema and table configuration
SOURCE_SCHEMA = "CLM"
TARGET_SCHEMA = "CLM"
STAGE_SCHEMA = "etl_stage"

TABLE = "clm_tcv"
STAGE_TABLE = f"{TABLE}_stage"

PRIMARY_KEYS = [
    "award_no",
    "order_no",
    "mod_no"
]


#############################################################
# JDBC PROPERTIES
#############################################################

bronze_jdbc_props = {
    "user": BRONZE_USERNAME,
    "password": BRONZE_PASSWORD,
    "driver": "org.postgresql.Driver"
}

silver_jdbc_props = {
    "user": SILVER_USERNAME,
    "password": SILVER_PASSWORD,
    "driver": "org.postgresql.Driver"
}


#############################################################
# HELPER TO RUN SQL ON SILVER DATABASE USING JDBC
#############################################################

def run_sql(sql):
    conn = spark._sc._gateway.jvm.java.sql.DriverManager.getConnection(
        SILVER_JDBC,
        SILVER_USERNAME,
        SILVER_PASSWORD
    )

    stmt = conn.createStatement()

    try:
        stmt.execute(sql)

    finally:
        stmt.close()
        conn.close()


#############################################################
# STEP 1 - READ BRONZE
#############################################################

print("Reading Bronze table...")

bronze_df = spark.read.jdbc(
    url=BRONZE_JDBC,
    table=f'"{SOURCE_SCHEMA}"."{TABLE}"',
    properties=bronze_jdbc_props
)

bronze_count = bronze_df.count()

print("Bronze Count:", bronze_count)


#############################################################
# STEP 2 - TRUNCATE STAGE
#############################################################

print("Truncating Stage table...")

run_sql(
    f'''
    TRUNCATE TABLE
    "{STAGE_SCHEMA}"."{STAGE_TABLE}";
    '''
)

print("Stage truncated.")


#############################################################
# STEP 3 - LOAD STAGE
#############################################################

print("Loading Bronze data into Stage...")

bronze_df.write.jdbc(
    url=SILVER_JDBC,
    table=f'"{STAGE_SCHEMA}"."{STAGE_TABLE}"',
    mode="append",
    properties=silver_jdbc_props
)

print("Loaded into Stage.")


#############################################################
# STEP 4 - MERGE STAGE INTO SILVER
#############################################################

columns = bronze_df.columns

insert_cols = ", ".join(
    [f'"{column}"' for column in columns]
)

select_cols = ", ".join(
    [f'"{column}"' for column in columns]
)

conflict_cols = ", ".join(
    [f'"{column}"' for column in PRIMARY_KEYS]
)

update_cols = []

for column in columns:

    if column not in PRIMARY_KEYS:

        update_cols.append(
            f'"{column}" = EXCLUDED."{column}"'
        )

update_sql = ",\n".join(update_cols)


merge_sql = f"""
INSERT INTO "{TARGET_SCHEMA}"."{TABLE}"
(
    {insert_cols}
)
SELECT
    {select_cols}
FROM
    "{STAGE_SCHEMA}"."{STAGE_TABLE}"
ON CONFLICT
(
    {conflict_cols}
)
DO UPDATE
SET
    {update_sql};
"""


print("Running Merge...")

run_sql(merge_sql)

print("Merge completed.")


#############################################################
# STEP 5 - VALIDATION
#############################################################

silver_count_df = spark.read.jdbc(
    url=SILVER_JDBC,
    table=f'''
    (
        SELECT COUNT(*) AS cnt
        FROM "{TARGET_SCHEMA}"."{TABLE}"
    ) x
    ''',
    properties=silver_jdbc_props
)

silver_count = silver_count_df.collect()[0]["cnt"]

print("Silver Count:", silver_count)

print("Completed Successfully.")

job.commit()
