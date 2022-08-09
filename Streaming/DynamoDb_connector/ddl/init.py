import boto3
from DynamoDb_connector.settings import Settings
from DynamoDb_connector.secret_key import get_secret

AWS_CREDENTIALS = Settings.AWS_CREDENTIALS

Kinesis = Settings.KINESIS



def get_dynamodb():
  """
  Creates connection of DynamoDb using boto3

  Returns:
      client: resource service client
  """  

  access_key , secret_access_key = get_secret()
  region = AWS_CREDENTIALS['region']
  return boto3.resource('dynamodb',
                 aws_access_key_id=access_key,
                 aws_secret_access_key=secret_access_key,
                 region_name=region)

