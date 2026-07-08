import boto3
import os

sns = boto3.client("sns")
ec2 = boto3.client("ec2")

TOPIC = os.environ["SNS_TOPIC"]

ALLOWED_TYPES = [
    "t3.micro",
    "t3.small"
]

REQUIRED_TAGS = [
    "Owner",
    "Environment",
    "Project"
]

def lambda_handler(event, context):

    print(event)

    detail = event["detail"]

    instance = detail["responseElements"]["instancesSet"]["items"][0]["instanceId"]

    response = ec2.describe_instances(
        InstanceIds=[instance]
    )

    instance_data = response["Reservations"][0]["Instances"][0]

    instance_type = instance_data["InstanceType"]

    tags = {}

    for tag in instance_data.get("Tags", []):

        tags[tag["Key"]] = tag["Value"]

    violations = []

    if instance_type not in ALLOWED_TYPES:

        violations.append(
            f"Unapproved instance type: {instance_type}"
        )

    for tag in REQUIRED_TAGS:

        if tag not in tags:

            violations.append(
                f"Missing tag: {tag}"
            )

    if violations:

        sns.publish(

            TopicArn=TOPIC,

            Subject="Governance Violation",

            Message="\n".join(violations)

        )

    return {
        "statusCode":200
    }
