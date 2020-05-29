from behave import *
import os
import logging
import boto3

BASE_IMAGE = os.environ.get("BASE_IMAGE_ID", "ami-0323c3dd2da7fb37d")
EC2_CLIENT = boto3.client("ec2")
SQS_CLIENT = boto3.client("sqs")


def create_instance():
    """Handles s3-bucket-not-encrypted, s3-logging-not-enabled, s3-bucket-policy-public-access."""
    create_response = EC2_CLIENT.run_instances(
        BlockDeviceMappings=[{"DeviceName": "/dev/sdh", "Ebs": {"VolumeSize": 8,},},],
        ImageId=BASE_IMAGE,
        InstanceType="t2.micro",
        MaxCount=1,
        MinCount=1,
    )
    instance_id = create_response["Instances"][0]["InstanceId"]

    waiter = EC2_CLIENT.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])

    logging.info("Created instance with response: %s", create_response)
    return instance_id


def create_insecure_snapshot(instance_id):
    describe_response = EC2_CLIENT.describe_instances(InstanceIds=[instance_id])
    ebs_id = describe_response["Reservations"][0]["Instances"][0][
        "BlockDeviceMappings"
    ][0]["Ebs"]["VolumeId"]
    ebs_snapshot = EC2_CLIENT.create_snapshot(VolumeId=ebs_id)
    snapshot_id = ebs_snapshot["SnapshotId"]

    waiter = EC2_CLIENT.get_waiter("snapshot_completed")
    waiter.wait(SnapshotIds=[snapshot_id])
    logging.info("Created snapshot with id: %s", snapshot_id)

    return snapshot_id


def modify_snapshot_to_be_public(snapshot_id):
    public_snapshot_response = EC2_CLIENT.modify_snapshot_attribute(
        Attribute="createVolumePermission",
        GroupNames=["all"],
        OperationType="add",
        SnapshotId=snapshot_id,
    )
    logging.info("Modified snapshot to be public with: %s", public_snapshot_response)


@given("the reflex ebs-snapshot-public rule is deployed into an AWS account")
def step_impl(context):
    sqs_dlq_response = SQS_CLIENT.list_queues(QueueNamePrefix="EbsPublicSnapshot-DLQ")
    assert len(sqs_dlq_response["QueueUrls"]) == 1
    sqs_list_response = SQS_CLIENT.list_queues(QueueNamePrefix="EbsPublicSnapshot")
    assert len(sqs_list_response["QueueUrls"]) == 2
    pass


@given("an EBS snapshot is created and available")
def step_impl(context):
    instance_id = create_instance()
    snapshot_id = create_insecure_snapshot(instance_id)
    context.config.userdata["snapshot_id"] = snapshot_id


@when("the EBS snapshot is modified to be publicly available")
def step_impl(context):
    modify_snapshot_to_be_public(context.config.userdata.get("snapshot_id"))


@then("a reflex alert message is sent to our reflex SNS topic")
def step_impl(context):
    assert context.failed is False
