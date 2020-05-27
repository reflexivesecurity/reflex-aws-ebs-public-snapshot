
Feature: This behavior tests the detective mechanism for when an EBS snapshot is made public
  Scenario: An existing EBS snapshot is modified to be public
    Given the reflex ebs-snapshot-public rule is deployed into an AWS account
    And an EBS snapshot is created and available
    When the EBS snapshot is modified to be publicly available
    Then a reflex alert message is sent to our reflex SNS topic
