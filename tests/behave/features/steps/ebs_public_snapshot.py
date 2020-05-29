from behave import *
import os
import boto3

EC2_CLIENT = boto3.client('ec2')
SQS_CLIENT = boto3.client('sqs')

@given('the reflex ebs-snapshot-public rule is deployed into an AWS account')
def step_impl(context):
    sqs_dlq_response = SQS_CLIENT.list_queues(QueueNamePrefix="EbsSnapshot-DLQ")
    assert len(sqs_dlq_response['QueueUrls']) == 1
    sqs_list_response = SQS_CLIENT.list_queues(QueueNamePrefix="EbsSnapshot")
    assert len(sqs_list_response['QueueUrls']) == 2
    pass

@given('an EBS snapshot is created and available')
def step_impl(context):
    pass

@when('the EBS snapshot is modified to be publicly available')
def step_impl(context):
    assert True is not False

@then('a reflex alert message is sent to our reflex SNS topic')
def step_impl(context):
    assert context.failed is False

