""" Module for PublicAMIRule """

import json

import boto3

from reflex_core import AWSRule, subscription_confirmation


class EbsPublicSnapshot(AWSRule):
    """ AWS rule for ensuring non-public AMIs """

    client = boto3.client("ec2")

    def __init__(self, event):
        super().__init__(event)

    def extract_event_data(self, event):
        """ Extract required data from the CloudWatch event """
        self.raw_event = event
        self.ebs_snapshot_id = event["detail"]["requestParameters"]["snapshotId"]

    def resource_compliant(self):
        """ Determines if the EBS snapshot is public, and if so returns False and True otherwise """
        is_compliant = True
        response = self.client.describe_snapshot_attribute(
            Attribute="createVolumePermission", SnapshotId=self.ebs_snapshot_id
        )

        for permission in response["CreateVolumePermissions"]:
            try:
                if permission["Group"] == "all":
                    is_compliant = False
            except KeyError:
                continue

        return is_compliant

    def remediate(self):
        """ Makes the EBS snapshot private """
        self.client.modify_snapshot_attribute(
            Attribute="createVolumePermission",
            SnapshotId=self.ebs_snapshot_id,
            CreateVolumePermission={"Remove": [{"Group": "all"}]},
        )

    def get_remediation_message(self):
        """ Returns a message about the remediation action that occurred """
        message = f"The EBS snapshot with ID: {self.ebs_snapshot_id} was made public. "
        if self.should_remediate():
            message += "Public access has been disabled."

        return message


def lambda_handler(event, _):
    """ Handles the incoming event """
    print(event)
    if subscription_confirmation.is_subscription_confirmation(event):
        subscription_confirmation.confirm_subscription(event)
        return
    rule = EbsPublicSnapshot(json.loads(event["Records"][0]["body"]))
    rule.run_compliance_rule()
