import json

from aws_cdk import aws_logs as logs
from aws_cdk.core import RemovalPolicy

def create_logs(self, path):
    """creation of cloudwatch log group

    Args:
        path (string): path to config file for log
    """

    # Read config file
    config = log_config(path)

    # Set up log group
    for log in config["log_groups"]:
        logs.LogGroup(self, log["log_name"], log_group_name=log["log_name"], removal_policy=RemovalPolicy.DESTROY)


def log_config(path):
    """Reading config file for log_group

    Args:
        path (string): path for config

    Returns:
        dictionary: config for log group
    """

    # Reading config file
    with open(path, 'r') as f:
        log_config = json.load(f)

    return log_config
