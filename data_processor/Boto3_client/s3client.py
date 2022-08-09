import boto3
import os, zipfile

def get_s3_client():
    client = boto3.client('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                          aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
                          region_name=os.getenv('AWS_REGION'))
    
    return client
    
def get_s3():
    """
    Creates connection of DynamoDb using boto3

    Returns:
        client: resource service client
    """  
    client = boto3.resource('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                          aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
                          region_name=os.getenv('AWS_REGION'))
    return client