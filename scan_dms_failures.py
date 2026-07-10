import psycopg2

from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

import sys

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

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

#############################################################
# JDBC Properties
#############################################################

jdbc_props = {
    "user": USERNAME,
    "password": PASSWORD,
    "driver": "org.postgresql.Driver"
}

#############################################################
# STEP-1 Read Bronze
#############################################################

print("Reading Bronze table...")

bronze_df = spark.read.jdbc(
    url=BRONZE_JDBC,
    table=f'"{SOURCE_SCHEMA}"."{TABLE}"',
    properties=jdbc_props
)

print("Bronze Count :", bronze_df.count())

#############################################################
# STEP-2 Truncate Stage
#############################################################

silver_conn = psycopg2.connect(
    host=SILVER_HOST,
    port=SILVER_PORT,
    database=SILVER_DB,
    user=USERNAME,
    password=PASSWORD
)

silver_conn.autocommit = False

cursor = silver_conn.cursor()

cursor.execute(f"""
TRUNCATE TABLE "{STAGE_SCHEMA}"."{TABLE}_stage";
""")

silver_conn.commit()

print("Stage truncated.")

#############################################################
# STEP-3 Load Stage
#############################################################

bronze_df.write.jdbc(
    url=SILVER_JDBC,
    table=f'"{STAGE_SCHEMA}"."{TABLE}_stage"',
    mode="append",
    properties=jdbc_props
)

print("Loaded into Stage.")

#############################################################
# STEP-4 Merge
#############################################################

columns = bronze_df.columns

insert_cols = ",".join([f'"{c}"' for c in columns])

select_cols = ",".join([f'"{c}"' for c in columns])

conflict_cols = ",".join([f'"{c}"' for c in PRIMARY_KEYS])

update_cols = []

for c in columns:

    if c not in PRIMARY_KEYS:

        update_cols.append(
            f'''"{c}" = EXCLUDED."{c}"'''
        )

update_sql = ",\n".join(update_cols)

merge_sql = f"""
INSERT INTO "{TARGET_SCHEMA}"."{TABLE}"
({insert_cols})

SELECT
{select_cols}

FROM "{STAGE_SCHEMA}"."{TABLE}_stage"

ON CONFLICT ({conflict_cols})

DO UPDATE
SET

{update_sql};
"""

print("Running Merge...")

cursor.execute(merge_sql)

silver_conn.commit()

#############################################################
# STEP-5 Validation
#############################################################

cursor.execute(f'''
select count(*)
from "{TARGET_SCHEMA}"."{TABLE}"
''')

print("Silver Count :", cursor.fetchone()[0])

cursor.close()

silver_conn.close()

print("Completed Successfully")

job.commit()
