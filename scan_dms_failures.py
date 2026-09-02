Hi [admin], I'm hitting an iam:PassRole permission error trying to attach mt-dm-glue-role to an EventBridge rule (mt-dm-clm-failure-notify). Rather than granting me PassRole on the Glue execution role, could you create a small dedicated role for this instead? I sent the exact trust policy + permissions policy JSON earlier (Amazon_EventBridge_Invoke_Sns_Glue_Alerts) — that avoids reusing the Glue job role for something unrelated, and avoids me needing broad IAM permissions on my own account. Once it exists, I'll select it directly and won't need any additional grants.

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

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "events.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws-us-gov:sns:us-gov-west-1:514899973745:glue-job-mt-dm-glue-clm"
    }
  ]
}


"Glue job <jobName> ended with state <state> (run <jobRunId>). Message: <message>"
