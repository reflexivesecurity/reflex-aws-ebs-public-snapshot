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

    public_snapshot_response = EC2_CLIENT.modify_snapshot_attribute(
        Attribute="createVolumePermission",
        GroupNames=["all"],
        OperationType="add",
        SnapshotId=snapshot_id,
    )
    logging.info("Modified snapshot to be public with: %s", public_snapshot_response)

    return snapshot_id


def delete_snapshot(snapshot_id, instance_id):
    delete_response = EC2_CLIENT.delete_snapshot(SnapshotId=snapshot_id)
    logging.info("Deleted snapshot with: %s", delete_response)
    snapshot_list = EC2_CLIENT.describe_snapshots()
    for snapshot in snapshot_list["Snapshots"]:
        if instance_id in snapshot["Description"]:
            delete_response = EC2_CLIENT.delete_snapshot(
                SnapshotId=snapshot["SnapshotId"]
            )


