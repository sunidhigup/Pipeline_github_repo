import boto3
from Rule_Engine.setting import Settings


def get_cloudwatch():
    """

    :return:
    """
    client = boto3.client('logs', region_name=Settings.AWS_CREDENTIALS["region_name"])
    
    return client
