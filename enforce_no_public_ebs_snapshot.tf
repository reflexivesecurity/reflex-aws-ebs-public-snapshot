module "enforce_no_public_ebs_snapshot" {
  source           = "git::https://github.com/cloudmitigator/reflex-engine.git//modules/cwe_lambda?ref=v0.3.0"
  rule_name        = "EnforceNoPublicEBSSnapshot"
  rule_description = "Rule to check if EBS snapshot is modified to be public"

  event_pattern = <<PATTERN
{
  "detail-type": [
    "AWS API Call via CloudTrail"
  ],
  "source": [
    "aws.ec2"
  ],
  "detail": {
    "eventSource": [
      "ec2.amazonaws.com"
    ],
    "eventName": [
      "ModifySnapshotAttribute"
    ]
  }
}
PATTERN

  function_name            = "EnforceNoPublicEBSSnapshot"
  source_code_dir          = "${path.module}/source"
  handler                  = "enforce_no_public_ebs_snapshot.lambda_handler"
  lambda_runtime           = "python3.7"
  environment_variable_map = { SNS_TOPIC = var.sns_topic_arn }
  custom_lambda_policy     = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ec2:DescribeSnapshotAttribute",
        "ec2:ModifySnapshotAttribute"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF


  queue_name    = "EnforceNoPublicEBSSnapshot"
  delay_seconds = 0

  target_id = "EnforceNoPublicEBSSnapshot"

  sns_topic_arn = var.sns_topic_arn
  sqs_kms_key_id = var.reflex_kms_key_id
}
