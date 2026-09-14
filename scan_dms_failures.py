{
  "Sid": "AllowEventBridgeToPublish",
  "Effect": "Allow",
  "Principal": {
    "Service": "events.amazonaws.com"
  },
  "Action": "sns:Publish",
  "Resource": "YOUR_SNS_TOPIC_ARN",
  "Condition": {
    "ArnEquals": {
      "aws:SourceArn": "YOUR_EVENTBRIDGE_RULE_ARN"
    }
  }
}
