{
  "account": "$.account",
  "eventTime": "$.time",
  "jobName": "$.detail.jobName",
  "jobRunId": "$.detail.jobRunId",
  "message": "$.detail.message",
  "region": "$.region",
  "severity": "$.detail.severity",
  "state": "$.detail.state"
}

"AWS GLUE JOB FAILURE ALERT\n\nJob Name: <jobName>\nStatus: <state>\nSeverity: <severity>\nRegion: <region>\nAWS Account: <account>\nJob Run ID: <jobRunId>\nFailure Time (UTC): <eventTime>\n\nError Details:\n<message>\n\nAction Required:\nReview the AWS Glue job run and CloudWatch logs for additional details."
