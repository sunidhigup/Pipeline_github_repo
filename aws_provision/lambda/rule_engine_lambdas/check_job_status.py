import json
import datetime
from boto3.dynamodb.conditions import Key, Attr
import boto3
from constants.constant import Rule_Engine
from constants.constant import check_job_status_constants, common_constants
from logger.helper_functions import log_initiator
from logger.func_write_log import write_logs


def check_job_status(cluster_id, step_list):
    """checks the status of the job given out of the COMPLETE, FAILED or CANCELLED

    Args:
        cluster_id (string)
        step_list (list)

    Returns:
        list: list of running steps, completed steps and cancelled steps
    """
    cluster_id = cluster_id
    step_list = step_list
    running_steps = []
    completed_steps = []
    cancelled_steps = []
    failed_steps = {}
    client = boto3.client(Rule_Engine.EMR_CLIENT)

    # Checking the list which steps are running/completed or cancelled and segrating them
    for step_id in step_list:
        list = []
        list.append(step_id)
        response = client.list_steps(ClusterId=cluster_id, StepIds=list)
        steps = response[check_job_status_constants.STEPS][0][common_constants.STATUS][check_job_status_constants.STATE]

        if steps == Rule_Engine.JOB_COMPLETE:
            completed_steps.append(step_id)

        elif steps == Rule_Engine.JOB_FAILED or steps == Rule_Engine.JOB_CANCELLED:

            cancelled_steps.append(step_id)
        else:
            running_steps.append(step_id)

    return running_steps, completed_steps, cancelled_steps


def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    try:

        execution_id = event[common_constants.EXECUTION_ID]

        timeval = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        timestampval = str(datetime.datetime.strptime(timeval, "%Y-%m-%d %H:%M:%S").timestamp())

        # logger initiator
        log_initiator(Rule_Engine.LOG_GROUP,execution_id+Rule_Engine.CHECK_JOB_STATUS+timestampval)
        write_logs(common_constants.INFO, "Inside  Check Job Status Rule Engine  Lambda")

        cluster_list = event[common_constants.AVAILABLE_CLUSTERS]
        table_name = Rule_Engine.TABLE_NAME
        dynamodb = boto3.resource(Rule_Engine.DYNAMO_CLIENT)
        table = dynamodb.Table(table_name)
        if not cluster_list:
            return event
        for cluster in cluster_list:
            cluster_metadata = dynamodb.Table(table_name).get_item(Key={common_constants.CLUSTER_ID: cluster})
            clusters = cluster_metadata[common_constants.ITEM]

            running_steps = clusters[check_job_status_constants.STEP_LIST]
            running_steps, completed_steps, cancelled_steps = check_job_status(cluster, running_steps)

            # Checking which steps are completed and updating available cores
            for steps in completed_steps:
                step_cores = clusters[check_job_status_constants.STEP_LIST]
                free_cores = step_cores[steps]
                clusters[common_constants.AVAILABLE_CORES] = clusters[common_constants.AVAILABLE_CORES] + free_cores
                dynamodb.Table(table_name).put_item(Item=clusters)
            # Checking which steps are cancelled and updating available cores
            for steps in cancelled_steps:
                step_cores = clusters[check_job_status_constants.STEP_LIST]
                free_cores = step_cores[steps]
                clusters[common_constants.AVAILABLE_CORES] = clusters[common_constants.AVAILABLE_CORES] + free_cores
                dynamodb.Table(table_name).put_item(Item=clusters)

    except Exception as e:
        dynamo_resp = dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).get_item(
            Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
        job_status_dict = dynamo_resp[common_constants.ITEM]
        job_status_dict[common_constants.ERROR_DETAIL] = str(e)
        job_status_dict[common_constants.STATUS] = Rule_Engine.JOB_FAILED
        job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())
        write_logs(common_constants.ERROR, "ERROR CAUGHT - {}".format(str(e)))

        dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).put_item(Item=job_status_dict)

        cluster_metadata[common_constants.STATUS] = common_constants.STOPPED
        print(e)
        # dynamodb.Table(table_name).put_item(Item=cluster_metadata)
        raise e

    return event
