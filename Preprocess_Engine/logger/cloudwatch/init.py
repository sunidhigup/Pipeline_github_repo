import boto3
import datetime
import os

def get_cloudwatch():
    """

    :return:
    """
    #client = boto3.client('logs', region_name="us-east-1")
    client = boto3.client('logs',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                          aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
                          region_name=os.getenv('AWS_REGION'))
    return client

