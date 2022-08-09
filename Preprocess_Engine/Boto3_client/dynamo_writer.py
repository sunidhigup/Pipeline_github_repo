import boto3
import os 


def get_dynamodb():
    """
    Creates connection of DynamoDb using boto3

    Returns:
        client: resource service client
    """  
    #Creating resource for boto3
    client = boto3.resource('dynamodb',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                          aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
                          region_name=os.getenv('AWS_REGION'))
    return client

def write_to_meta(table_name, dict):
    """Write to Dynamodb

    Args:
        table_name (string): name of table
        dict (dictionary): data to write on table
    """    
    # dict["timestamp"]=ts
    dynamodb= get_dynamodb()
    #Writing to dynamoDb
    dynamodb.Table(table_name).put_item(Item=dict) 