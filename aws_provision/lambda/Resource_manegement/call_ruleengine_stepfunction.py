import json
import boto3
from constants.constant import Resource_manage
from constants.constant import call_ruleengine_constants, common_constant

def lambda_handler(event, context):
    """

    Args:
        event (dictionary)
        context (dictionary)
    """    
    #Step function client creation
    sfn_client = boto3.client(Resource_manage.STEP_FUNCTION_CLIENT, region_name=Resource_manage.REGION)

    # state_machine_arn = Resource_manage.RULE_ENGINE_ARN
    state_machine_arn = ""
    #Listing all the step functions
    state_machines = sfn_client.list_state_machines()
    for machine in state_machines[call_ruleengine_constants.STATE_MACHINES]:
        if machine[common_constant.NAME] == call_ruleengine_constants.STATE_MACHINE_NAME:
            state_machine_arn = machine[common_constant.STATE_MACHINE_ARN]
            
    #Starting the step function execution
    response = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(event)
    )
