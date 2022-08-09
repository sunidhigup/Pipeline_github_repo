import boto3
import json
from DynamoDb_connector.settings import Settings
from DynamoDb_connector.secret_key import get_secret
from Streaming.env_fetcher import read_config
AWS_CREDENTIALS = Settings.AWS_CREDENTIALS

def call_resource_management_sf(rule_engine):
    """

    :param rule_engine:
    """
    #Reading config file
    config_data = read_config("dev","depconfig","Streaming/Config/config.json")
    
    #Getting keys
    access_key , secret_access_key = get_secret()
    region = AWS_CREDENTIALS['region']

    #Makinf step function boto3 client
    sfn_client = boto3.client('stepfunctions',
                 aws_access_key_id=access_key,
                 aws_secret_access_key=secret_access_key,
                 region_name=region)

    state_machine_arn = config_data["resource_management"]

    response = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps({ "rule_engine": rule_engine  })
    )

