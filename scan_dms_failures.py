**Purpose:** Allow EventBridge rule `glue-job-mt-dm-clm-failure-notify` to publish
to SNS topic `glue-job-mt-dm-glue-clm` when a Glue job run fails.

## Role name
`Amazon_EventBridge_Invoke_Sns_Glue_Alerts` (or any name — update the rule's
"Execution role" field to match once created)

## Trust policy
```json
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
```

## Permissions policy
```json
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
```
