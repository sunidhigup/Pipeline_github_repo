import boto3
import json
from boto3.dynamodb.conditions import Attr
from constants.constant import Data_processor
from constants.constant import check_clusters_status_constants,common_constants
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

    #Boto3 client creation for EMR

    try:
        client = boto3.client(Data_processor.EMR_CLIENT)
        log_group = Data_processor.LOG_GROUP
        log_initiator(log_group, event[common_constants.EXECUTION_ID] + "_DataProcessor_checkclusterstatus")
        write_logs(common_constants.INFO, "Inside Check cluster status Lambda")
        available_clusters=0
        cluster_list = []
        event[common_constants.AVAILABLE_CLUSTERS] = []
        table_name = Data_processor.TABLE_NAME
        running_clust = client.list_clusters(ClusterStates=[Data_processor.EMR_STATE_RUNNING, Data_processor.EMR_STATE_WAITING])
        response = json.dumps(running_clust, indent=4, sort_keys=True, default=str)
        clusters = running_clust[check_clusters_status_constants.CLUSTERS]
        
        #Boto3 client creation for DynamoDb
        dynamodb = boto3.resource(Data_processor.DYNAMO_CLIENT)
        response = dynamodb.Table(table_name).scan(FilterExpression=Attr(common_constants.STATUS).eq(common_constants.RUNNING))
        item_list = response[common_constants.ITEMS]
        

        #Appending in the list of available clusters
        for item in item_list:
            for cluster in clusters:
                if cluster[common_constants.ITEMS] == item[common_constants.CLUSTER_ID]:
                    cluster_list.append(cluster[check_clusters_status_constants.ID])
                    available_clusters = available_clusters+1            
        
        
        #Appedning ready state or wait state based on the cluster availability
        event[common_constants.AVAILABLE_CLUSTERS]= cluster_list
        if available_clusters == len(item_list):
            event[check_clusters_status_constants.STATE]= Data_processor.READY_STATE
        else:
            event[check_clusters_status_constants.STATE]= Data_processor.WAIT_STATE
    
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
