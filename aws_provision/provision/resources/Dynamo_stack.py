import json

from aws_cdk import (
    core,
    aws_dynamodb
)
from botocore.exceptions import ClientError


def create_dynamo(self, path):
    """
    create dynamo tables
        Args:
            path (str): path of config
    """

    #Reading config file
    config = dynamo_config(path)

    #Making dynamo tables
    for table in config["tables"]:
        demo_table = aws_dynamodb.Table(
            self, table["logical_id"],
            table_name=table["table_name"],
            partition_key=aws_dynamodb.Attribute(
                name=table["part_key"],
                type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=core.RemovalPolicy.DESTROY
        )


def dynamo_config(path):
    """ Fetches config for dynamoDB

    Returns:
        dict : config for dynamoDB
    """
    #Readinf config file
    with open(path, 'r') as f:
        dynamo_config = json.load(f)

    return dynamo_config