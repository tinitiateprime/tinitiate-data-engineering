import boto3

client = boto3.client("dms", region_name="us-gov-west-1")

response = client.describe_table_statistics(
    ReplicationTaskArn="YOUR_TASK_ARN"
)

for table in response["TableStatistics"]:
    if table["TableState"] == "Table error":
        print(
            table["SchemaName"],
            table["TableName"],
            table["TableState"]
        )
