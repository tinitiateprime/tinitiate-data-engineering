{
  "source": ["aws.glue"],
  "detail-type": ["Glue Job State Change"],
  "detail": {
    "state": ["FAILED", "TIMEOUT", "ERROR"]
  }
}


{
  "jobName": "$.detail.jobName",
  "state": "$.detail.state",
  "jobRunId": "$.detail.jobRunId",
  "message": "$.detail.message"
}
