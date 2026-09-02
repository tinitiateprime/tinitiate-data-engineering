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
