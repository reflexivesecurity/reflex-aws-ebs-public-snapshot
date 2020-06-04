from behave import *
import os
import logging
import boto3
from reflex_acceptance_common import ReflexAcceptance

BASE_IMAGE = os.environ.get("BASE_IMAGE_ID", "ami-0323c3dd2da7fb37d")
EC2_CLIENT = boto3.client("ec2")
SQS_CLIENT = boto3.client("sqs")
acceptance_client = ReflexAcceptance("ebs-public-snapshot")


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


def delete_snapshot(snapshot_id, instance_id):
    delete_response = EC2_CLIENT.delete_snapshot(SnapshotId=snapshot_id)
    logging.info("Deleted snapshot with: %s", delete_response)
    snapshot_list = EC2_CLIENT.describe_snapshots()
    for snapshot in snapshot_list["Snapshots"]:
        if instance_id in snapshot["Description"]:
            delete_response = EC2_CLIENT.delete_snapshot(
                SnapshotId=snapshot["SnapshotId"]
            )


def get_message_from_queue(queue_url):
    message = SQS_CLIENT.receive_message(QueueUrl=queue_url, WaitTimeSeconds=20)
    message_body = message["Messages"][0]["Body"]
    return message_body


@given("the reflex ebs-snapshot-public rule is deployed into an AWS account")
def step_impl(context):
    assert acceptance_client.get_queue_url_count("EbsPublicSnapshot-DLQ") == 1
    assert acceptance_client.get_queue_url_count("EbsPublicSnapshot") == 2
    assert acceptance_client.get_queue_url_count("test-queue") == 1
    sqs_test_response = SQS_CLIENT.list_queues(QueueNamePrefix="test-queue")
    context.config.userdata["test_queue_url"] = sqs_test_response["QueueUrls"][0]


@given("an EBS snapshot is created and available")
def step_impl(context):
    instance_id = create_instance()
    snapshot_id = create_insecure_snapshot(instance_id)
    context.config.userdata["instance_id"] = instance_id
    context.config.userdata["snapshot_id"] = snapshot_id


@when("the EBS snapshot is modified to be publicly available")
def step_impl(context):
    modify_snapshot_to_be_public(context.config.userdata.get("snapshot_id"))


@then("a reflex alert message is sent to our reflex SNS topic")
def step_impl(context):
    message = get_message_from_queue(context.config.userdata["test_queue_url"])
    print(message)
    assert "Snapshot" in message
    assert "Reflex" in message
    delete_snapshot(
        context.config.userdata["snapshot_id"], context.config.userdata["instance_id"]
    )
