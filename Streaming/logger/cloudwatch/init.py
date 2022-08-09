
import boto3
from DynamoDb_connector.settings import Settings
from DynamoDb_connector.secret_key import get_secret

AWS_CREDENTIALS = Settings.AWS_CREDENTIALS

def get_cloudwatch():
    """

    :return:
    """
    access_key , secret_access_key = get_secret()
    region = AWS_CREDENTIALS['region']
    #Creating boto3 client for logs
    client = boto3.client('logs',
                            aws_access_key_id=access_key,
                            aws_secret_access_key=secret_access_key,
                            region_name=region)
    return client