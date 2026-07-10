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

# -----------------------------------------------------------
# Bronze PostgreSQL
# -----------------------------------------------------------

BRONZE_HOST = (
    "gsapdi-pg-stg."
    "c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com"
)

BRONZE_PORT = "5432"
BRONZE_DB = "gsapdi"

BRONZE_USERNAME = "<BRONZE_USERNAME>"
BRONZE_PASSWORD = "<BRONZE_PASSWORD>"


# -----------------------------------------------------------
# Silver PostgreSQL
# -----------------------------------------------------------

SILVER_HOST = (
    "gsapdi-pg-mt-dm-dev."
    "c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com"
)

SILVER_PORT = "5432"
SILVER_DB = "mtdm"

SILVER_USERNAME = "<SILVER_USERNAME>"
SILVER_PASSWORD = "<SILVER_PASSWORD>"


# -----------------------------------------------------------
# JDBC URLs
# -----------------------------------------------------------

BRONZE_JDBC = (
    f"jdbc:postgresql://"
    f"{BRONZE_HOST}:{BRONZE_PORT}/{BRONZE_DB}"
)

SILVER_JDBC = (
    f"jdbc:postgresql://"
    f"{SILVER_HOST}:{SILVER_PORT}/{SILVER_DB}"
)


# -----------------------------------------------------------
# Table Configuration
# -----------------------------------------------------------

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
# HELPER TO RUN SQL ON SILVER USING JVM JDBC
#############################################################

def run_sql(sql):
    """
    Executes SQL against the Silver PostgreSQL database.

    Used for:
    - TRUNCATE
    - INSERT ... ON CONFLICT
    - DDL statements
    """

    conn = None
    stmt = None

    try:
        jvm = spark._sc._gateway.jvm

        jvm.java.lang.Class.forName(
            "org.postgresql.Driver"
        )

        conn = jvm.java.sql.DriverManager.getConnection(
            SILVER_JDBC,
            SILVER_USERNAME,
            SILVER_PASSWORD
        )

        conn.setAutoCommit(False)

        stmt = conn.createStatement()

        stmt.execute(sql)

        conn.commit()

    except Exception as error:

        if conn is not None:
            conn.rollback()

        print("SQL execution failed:")
        print(str(error))

        raise

    finally:

        if stmt is not None:
            stmt.close()

        if conn is not None:
            conn.close()


#############################################################
# STEP 1: READ BRONZE
#############################################################

print("Reading Bronze table...")

bronze_df = spark.read.jdbc(
    url=BRONZE_JDBC,
    table=f'"{SOURCE_SCHEMA}"."{TABLE}"',
    properties=bronze_jdbc_props
)

bronze_count = bronze_df.count()

print("Bronze Count:", bronze_count)

if bronze_count == 0:
    print("Bronze table is empty. Nothing to load.")
    job.commit()
    sys.exit(0)


#############################################################
# STEP 2: TRUNCATE STAGE
#############################################################

print("Truncating Stage table...")

truncate_sql = f"""
TRUNCATE TABLE
"{STAGE_SCHEMA}"."{STAGE_TABLE}";
"""

run_sql(truncate_sql)

print("Stage truncated.")


#############################################################
# STEP 3: LOAD BRONZE INTO SILVER STAGE
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
# STEP 4: VALIDATE STAGE COUNT
#############################################################

stage_count_df = spark.read.jdbc(
    url=SILVER_JDBC,
    table=f"""
    (
        SELECT COUNT(*) AS cnt
        FROM "{STAGE_SCHEMA}"."{STAGE_TABLE}"
    ) stage_count
    """,
    properties=silver_jdbc_props
)

stage_count = stage_count_df.collect()[0]["cnt"]

print("Stage Count:", stage_count)

if bronze_count != stage_count:
    raise RuntimeError(
        f"Bronze and Stage counts do not match. "
        f"Bronze={bronze_count}, "
        f"Stage={stage_count}"
    )


#############################################################
# STEP 5: BUILD MERGE SQL
#############################################################

columns = bronze_df.columns

missing_primary_keys = [
    key
    for key in PRIMARY_KEYS
    if key not in columns
]

if missing_primary_keys:
    raise RuntimeError(
        f"Primary key columns are missing: "
        f"{missing_primary_keys}"
    )


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


if update_cols:

    update_sql = ",\n".join(update_cols)

    conflict_action = f"""
    DO UPDATE SET
    {update_sql}
    """

else:

    conflict_action = "DO NOTHING"


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
{conflict_action};
"""


#############################################################
# STEP 6: MERGE STAGE INTO SILVER
#############################################################

print("Running Merge...")

run_sql(merge_sql)

print("Merge completed.")


#############################################################
# STEP 7: VALIDATE SILVER COUNT
#############################################################

silver_count_df = spark.read.jdbc(
    url=SILVER_JDBC,
    table=f"""
    (
        SELECT COUNT(*) AS cnt
        FROM "{TARGET_SCHEMA}"."{TABLE}"
    ) silver_count
    """,
    properties=silver_jdbc_props
)

silver_count = silver_count_df.collect()[0]["cnt"]

print("Bronze Count:", bronze_count)
print("Stage Count:", stage_count)
print("Silver Count:", silver_count)

print("Completed Successfully.")

job.commit()
