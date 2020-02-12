""" Module for PublicAMIRule """

import json

import boto3

from reflex_core import AWSRule


class PublicEBSSnapshotRule(AWSRule):
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
            Attribute="createVolumePermission", ImageId=self.ebs_snapshot_id
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
            ImageId=self.ebs_snapshot_id,
            CreateVolumePermission={"Remove": [{"Group": "all"}]},
        )

    def get_remediation_message(self):
        """ Returns a message about the remediation action that occurred """
        return f"The EBS snapshot with ID: {self.ebs_snapshot_id} was made public. Public access has been disabled."


def lambda_handler(event, _):
    """ Handles the incoming event """
    print(event)
    rule = PublicEBSSnapshotRule(json.loads(event["Records"][0]["body"]))
    rule.run_compliance_rule()
