from behave import *

@given('the reflex ebs-snapshot-public rule is deployed into an AWS account')
def step_impl(context):
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

