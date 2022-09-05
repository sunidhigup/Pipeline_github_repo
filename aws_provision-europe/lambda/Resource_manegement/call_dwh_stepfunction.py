from asyncio import constants
from http.client import CONFLICT
import boto3
import json
from constants.constant import Resource_manage
from constants.constant import call_dwh_constants, common_constant

def lambda_handler(event, context):
    """

    Args:
        event (dictionary)
        context (dictionary)   
    """    
    #Step function client creation
    sfn_client = boto3.client(Resource_manage.STEP_FUNCTION_CLIENT,region_name=Resource_manage.REGION)
    state_machine_arn = ""

    #Listing the step functions
    state_machines = sfn_client.list_state_machines()
    # state_machine_arn = Resource_manage.DWH_ARN
    for machine in state_machines:
        if machine[common_constant.NAME] == call_dwh_constants.STATE_MACHINE_NAME:
            state_machine_arn = machine[common_constant.STATE_MACHINE_ARN]

    #Starting stpe function
    response = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(event)
    )