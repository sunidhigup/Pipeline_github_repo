import json
import boto3
from constants.constant import Data_processor,common_constants, common_constants
from boto3.dynamodb.conditions import Key, Attr
import datetime
from  logger.helper_functions import log_initiator
from  logger.func_write_log import write_logs

dynamodb = boto3.resource(Data_processor.DYNAMO_CLIENT)

def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """    
    
    #Creating boto3 resource client for dynamoDb
    try:
        table_name = Data_processor.TABLE_NAME
        log_group = Data_processor.LOG_GROUP
        log_initiator(log_group, event[common_constants.EXECUTION_ID] + "_DataProcessor_checkRunningEMR")
        write_logs(common_constants.INFO, "Inside check Running EMR status Lambda")

        response = dynamodb.Table(table_name).scan(FilterExpression=Attr(common_constants.STATUS).eq(common_constants.RUNNING))

        #Updating cluster availibility based on EMR status
        if response[common_constants.ITEMS]:
            event[common_constants.CLUSTER_AVAILABLE]= True
        
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