import json
import boto3
import datetime
from constants.constant import Data_processor,common_constants, common_constants
from boto3.dynamodb.conditions import Key, Attr
from  logger.helper_functions import log_initiator
from  logger.func_write_log import write_logs

dynamodb = boto3.resource(Data_processor.DYNAMO_CLIENT)

def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """    
    try:
        log_group = Data_processor.LOG_GROUP
        log_initiator(log_group, event[common_constants.EXECUTION_ID] + "_DataProcessor_retrievecores")
        write_logs(common_constants.INFO, "Inside Retrieve cores Lambda")
        cluster_available = event[common_constants.CLUSTER_AVAILABLE]
        cores_required = event[common_constants.CORES]
        table_name =Data_processor.TABLE_NAME
        
        #If clusters are available and cores required are available retreiving the emr cores   
        if cluster_available:
           
            
            response = dynamodb.Table(table_name).scan(FilterExpression=Attr(common_constants.STATUS).eq(common_constants.RUNNING))
            item_list = response[common_constants.ITEMS]
            
            for item in item_list:
                cores = item[common_constants.TOTAL_CORES]
                if cores > cores_required - (10* cores_required/100):
        
                    cluster_id = item[common_constants.CLUSTER_ID]
                    event[common_constants.CLUSTER_ID] = cluster_id
                    event[common_constants.CLUSTER_AVAILABLE]= True
                    break
                
                else:
                    event[common_constants.CLUSTER_AVAILABLE]= False
    
    except Exception as e:
        dynamo_resp = dynamodb.Table(Data_processor.JOB_STATUS_TABLE).get_item(Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
        job_status_dict = dynamo_resp[common_constants.ITEM]
        job_status_dict[common_constants.ERROR_DETAIL] = str(e)
        job_status_dict[common_constants.STATUS] = Data_processor.JOB_FAILED
        job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())
        
        write_logs("ERROR", "ERROR CAUGHT - {}".format(str(e)))

        dynamodb.Table(Data_processor.JOB_STATUS_TABLE).put_item(Item=job_status_dict)
        raise e
    
    return event