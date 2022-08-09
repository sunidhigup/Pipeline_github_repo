import boto3

from data_processor.setting import Settings


def get_cloudwatch():
    """

    :return:
    """
    client = boto3.client('logs', region_name=Settings.AWS_CREDENTIALS["region"])
    return client
