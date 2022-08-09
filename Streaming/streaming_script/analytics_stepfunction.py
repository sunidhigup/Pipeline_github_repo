import boto3
import json
from DynamoDb_connector.settings import Settings
from DynamoDb_connector.secret_key import get_secret
from Streaming.env_fetcher import read_config
AWS_CREDENTIALS = Settings.AWS_CREDENTIALS

def call_analytics_sf(segment,bucket,key):
    """

    :param segment:
    :param bucket:
    :param key:
    """
    config_data = read_config("dev","depconfig","Streaming/Config/config.json")
    
    access_key , secret_access_key = get_secret()
    region = AWS_CREDENTIALS['region']
    sfn_client = boto3.client('stepfunctions',
                 aws_access_key_id=access_key,
                 aws_secret_access_key=secret_access_key,
                 region_name=region)

    state_machine_arn = config_data["customer_360"]

    response = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps({ 
            "segment": segment,
            "bucket": bucket,
            "key": key
         })
    )

