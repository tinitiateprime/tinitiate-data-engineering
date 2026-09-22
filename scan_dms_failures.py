{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEventBridgeToPublish",
      "Effect": "Allow",
      "Principal": {
        "Service": "events.amazonaws.com"
      },
      "Action": "sns:Publish",
      "Resource": "arn:aws-us-gov:sns:us-gov-west-1:514899973745:glue-job-mt-dm-glue-clm",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "arn:aws-us-gov:events:us-gov-west-1:514899973745:rule/mt-dm-clm-failure-notify"
        }
      }
    }
  ]
}
