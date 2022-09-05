import json
from boto3.dynamodb.conditions import Key, Attr
import boto3
import time
import datetime
from constants.constant import Data_processor,check_job_status_constants, common_constants
from  logger.helper_functions import log_initiator
from  logger.func_write_log import write_logs

dynamodb = boto3.resource(Data_processor.DYNAMO_CLIENT)

def check_job_status(cluster_id,step_list):
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
    client = boto3.client(Data_processor.EMR_CLIENT)
    
    #Checking the list which steps are running/completed or cancelled and segrating them
    for step_id in step_list:
        list = []
        list.append(step_id)
        response = client.list_steps(ClusterId=cluster_id,StepIds=list)
        steps = response[check_job_status_constants.STEPS][0][check_job_status_constants.STATUS][check_job_status_constants.STATE]
        
        if steps == Data_processor.JOB_COMPLETE:
            completed_steps.append(step_id)
            
        elif steps == Data_processor.JOB_FAILED or steps == Data_processor.JOB_CANCELLED:

            cancelled_steps.append(step_id)
        else:
            running_steps.append(step_id)
    
    return running_steps,completed_steps,cancelled_steps

def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """

    try:
        cluster_list = event[common_constants.AVAILABLE_CLUSTERS]
        table_name = Data_processor.TABLE_NAME
       
        log_group = Data_processor.LOG_GROUP
        log_initiator(log_group, event[common_constants.EXECUTION_ID] + "_DataProcessor_checkJobStatus")
        write_logs(common_constants.INFO, "Inside check Job status Lambda")
       
        if not cluster_list:
            return event
        for cluster in cluster_list:
            cluster_metadata = dynamodb.Table(table_name).get_item(Key={common_constants.CLUSTER_ID: cluster})
            clusters= cluster_metadata[common_constants.ITEM]

            running_steps = clusters[check_job_status_constants.STEP_LIST]
            running_steps,completed_steps,cancelled_steps=check_job_status(cluster,running_steps)
            
        #Checking which steps are completed and updating available cores
            for steps in completed_steps:
                step_cores = clusters[check_job_status_constants.STEP_LIST]
                free_cores = step_cores[steps]
                clusters[common_constants.AVAILABLE_CORES]=clusters[common_constants.AVAILABLE_CORES]+ free_cores
                clusters[common_constants.STATUS] = Data_processor.STOPPED
                dynamodb.Table(table_name).put_item(Item=clusters)
                
            
        #Checking which steps are cancelled and updating available cores
            for steps in cancelled_steps:
                step_cores = clusters[check_job_status_constants.STEP_LIST]
                free_cores = step_cores[steps]
                clusters[common_constants.AVAILABLE_CORES]=clusters[common_constants.AVAILABLE_CORES]+ free_cores
                clusters[common_constants.STATUS] = Data_processor.STOPPED
                dynamodb.Table(table_name).put_item(Item=clusters)
                
                dynamo_input_response_meta = dynamodb.Table(Data_processor.JOB_STATUS_TABLE).get_item(Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
                job_status_dict = dynamo_input_response_meta[common_constants.ITEM]
                job_status_dict[common_constants.STATUS] = Data_processor.JOB_FAILED
                job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())
                dynamodb.Table(Data_processor.JOB_STATUS_TABLE).put_item(Item=job_status_dict)

    except Exception as e:
        dynamo_resp = dynamodb.Table(Data_processor.JOB_STATUS_TABLE).get_item(Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
        job_status_dict = dynamo_resp[common_constants.ITEM]
        job_status_dict[common_constants.ERROR_DETAIL] = str(e)
        job_status_dict[common_constants.STATUS] = Data_processor.JOB_FAILED
        job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())
        write_logs("ERROR", "ERROR CAUGHT - {}".format(str(e)))

        dynamodb.Table(Data_processor.JOB_STATUS_TABLE).put_item(Item=job_status_dict)
        cluster_metadata[common_constants.STATUS] = common_constants.STOPPED
        dynamodb.Table(table_name).put_item(Item=cluster_metadata)
        raise e
            
    return event