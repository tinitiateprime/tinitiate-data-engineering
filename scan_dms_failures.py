import sys
import psycopg2

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

BRONZE_USERNAME = "bronze_username"
BRONZE_PASSWORD = "<BRONZE_PASSWORD>"

# Silver PostgreSQL
SILVER_HOST = (
    "gsapdi-pg-mt-dm-dev."
    "c8jnpcht8n8j.us-gov-west-1.rds.amazonaws.com"
)
SILVER_PORT = "5432"
SILVER_DB = "mtdm"

SILVER_USERNAME = "jayathirth.kumsiravinder"
SILVER_PASSWORD = "<SILVER_PASSWORD>"

BRONZE_JDBC = (
    f"jdbc:postgresql://"
    f"{BRONZE_HOST}:{BRONZE_PORT}/{BRONZE_DB}"
)

SILVER_JDBC = (
    f"jdbc:postgresql://"
    f"{SILVER_HOST}:{SILVER_PORT}/{SILVER_DB}"
)

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

silver_conn = None
cursor = None

try:

    #########################################################
    # STEP 1: READ BRONZE
    #########################################################

    print("Reading Bronze table...")

    bronze_df = spark.read.jdbc(
        url=BRONZE_JDBC,
        table=f'"{SOURCE_SCHEMA}"."{TABLE}"',
        properties=bronze_jdbc_props
    )

    bronze_count = bronze_df.count()

    print(f"Bronze Count: {bronze_count}")

    if bronze_count == 0:
        print("Bronze table is empty. Nothing to load.")
        job.commit()
        sys.exit(0)

    #########################################################
    # STEP 2: CONNECT TO SILVER
    #########################################################

    silver_conn = psycopg2.connect(
        host=SILVER_HOST,
        port=SILVER_PORT,
        database=SILVER_DB,
        user=SILVER_USERNAME,
        password=SILVER_PASSWORD
    )

    silver_conn.autocommit = False
    cursor = silver_conn.cursor()

    #########################################################
    # STEP 3: TRUNCATE STAGE
    #########################################################

    truncate_sql = f'''
        TRUNCATE TABLE
        "{STAGE_SCHEMA}"."{STAGE_TABLE}";
    '''

    cursor.execute(truncate_sql)
    silver_conn.commit()

    print("Stage table truncated.")

    #########################################################
    # STEP 4: LOAD BRONZE INTO SILVER STAGE
    #########################################################

    bronze_df.write.jdbc(
        url=SILVER_JDBC,
        table=f'"{STAGE_SCHEMA}"."{STAGE_TABLE}"',
        mode="append",
        properties=silver_jdbc_props
    )

    print("Bronze data loaded into Silver stage table.")

    #########################################################
    # STEP 5: VALIDATE STAGE COUNT
    #########################################################

    cursor.execute(
        f'''
        SELECT COUNT(*)
        FROM "{STAGE_SCHEMA}"."{STAGE_TABLE}";
        '''
    )

    stage_count = cursor.fetchone()[0]

    print(f"Stage Count: {stage_count}")

    if stage_count != bronze_count:
        raise RuntimeError(
            f"Count mismatch. "
            f"Bronze={bronze_count}, Stage={stage_count}"
        )

    #########################################################
    # STEP 6: BUILD MERGE SQL
    #########################################################

    columns = bronze_df.columns

    missing_keys = [
        key
        for key in PRIMARY_KEYS
        if key not in columns
    ]

    if missing_keys:
        raise RuntimeError(
            f"Primary key columns missing from Bronze: "
            f"{missing_keys}"
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

    update_columns = [
        column
        for column in columns
        if column not in PRIMARY_KEYS
    ]

    if not update_columns:
        conflict_action = "DO NOTHING"
    else:
        update_sql = ",\n".join(
            [
                f'"{column}" = EXCLUDED."{column}"'
                for column in update_columns
            ]
        )

        conflict_action = f"""
        DO UPDATE SET
        {update_sql}
        """

    merge_sql = f"""
        INSERT INTO "{TARGET_SCHEMA}"."{TABLE}"
        ({insert_cols})

        SELECT
        {select_cols}
        FROM "{STAGE_SCHEMA}"."{STAGE_TABLE}"

        ON CONFLICT ({conflict_cols})
        {conflict_action};
    """

    #########################################################
    # STEP 7: MERGE INTO SILVER
    #########################################################

    print("Running merge...")

    cursor.execute(merge_sql)

    merged_row_count = cursor.rowcount

    silver_conn.commit()

    print(
        "Merge completed. "
        f"PostgreSQL affected rows: {merged_row_count}"
    )

    #########################################################
    # STEP 8: VALIDATION
    #########################################################

    cursor.execute(
        f'''
        SELECT COUNT(*)
        FROM "{TARGET_SCHEMA}"."{TABLE}";
        '''
    )

    silver_count = cursor.fetchone()[0]

    print(f"Final Silver Count: {silver_count}")
    print("Completed successfully.")

    job.commit()

except Exception as error:

    print(f"Job failed: {str(error)}")

    if silver_conn is not None:
        silver_conn.rollback()

    raise

finally:

    if cursor is not None:
        cursor.close()

    if silver_conn is not None:
        silver_conn.close()
