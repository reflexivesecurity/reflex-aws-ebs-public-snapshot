terraform {
  backend "s3" {
    bucket = "reflex-state"
    key = "reflex-ebs-snapshot-acceptance-test"
  }
}

module "ebs-public-snapshot-cwe" {
  source            = "../../terraform/cwe"
}

module "ebs-public-snapshot" {
  source            = "../../terraform/sqs_lambda"
  cloudwatch_event_rule_id = module.ebs-public-snapshot-cwe.id
  cloudwatch_event_rule_arn = module.ebs-public-snapshot-cwe.arn
  sns_topic_arn     = module.central-sns-topic.arn
  reflex_kms_key_id = module.reflex-kms-key.key_id
  mode = "detect"
}

module "central-sns-topic" {
  topic_name         = "ReflexAlerts"
  stack_name         = "EmailSNSStackReflexAlerts"
  source             = "git::https://github.com/cloudmitigator/reflex-engine.git//modules/sns_email_subscription?ref=v0.6.0"
  notification_email = "richard.julian@cloudmitigator.com"
}

module "reflex-kms-key" {
  source = "git::https://github.com/cloudmitigator/reflex-engine.git//modules/reflex_kms_key?ref=v0.6.0"
}
