import boto3
from data_processor.setting import Settings


def getDynamo():
    """

    :return:
    """
    #Creating boto3 resource for dynamoDb
    dynamodb = boto3.resource('dynamodb', region_name=Settings.AWS_CREDENTIALS["region"])
    return dynamodb
