from DynamoDb_connector.ddl.init import get_dynamodb
from DynamoDb_connector.settings import Settings
import boto3
import json


AWS_CREDENTIALS = Settings.AWS_CREDENTIALS
Kinesis = Settings.KINESIS

def read_from_meta(table_name,key):
    """ Read from DynamoDb

    Args:
        table_name (string): name of table
        key (string): key to filter results

    Returns:
        dict : dictionary containing one row
    """   
    #Making dynamoDb instance
    dynamodb= get_dynamodb()

    #Reading meta data from dynamoDb
    response = dynamodb.Table(table_name).get_item(
            Key={'stream_name': key})
   
    return response

def get_stream_name():
    """ Reads json from s3 and returns stream name

    Returns:
        string: nam of kinesis stream
    """    
    BUCKET = Kinesis["bucket"]
    FILE_TO_READ = Kinesis["path"]
    access_key = AWS_CREDENTIALS['awsAccessKey']
    secret_key = AWS_CREDENTIALS['awsSecretKey']
    region = AWS_CREDENTIALS['region']
    client = boto3.client('s3',
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        region_name=region
                        )
    result = client.get_object(Bucket=BUCKET, Key=FILE_TO_READ) 
    text = result["Body"].read().decode('utf-8')
    json_obj = json.loads(text)
    return json_obj["stream_name"]