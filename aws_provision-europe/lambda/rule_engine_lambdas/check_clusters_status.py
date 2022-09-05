import json
from boto3.dynamodb.conditions import Attr
from constants.constant import Rule_Engine
from constants.constant import check_clusters_status_constants, common_constants
import boto3
import datetime
from logger.helper_functions import log_initiator
from logger.func_write_log import write_logs

dynamodb = boto3.resource(Rule_Engine.DYNAMO_CLIENT)


def lambda_handler(event, context):
    """_summary_

    Args:
        event (dictionary)
        context (dictionary)

    Returns:
        dictionary: event
    """
    try:

        execution_id = event[common_constants.EXECUTION_ID]

        timeval = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        timestampval = str(datetime.datetime.strptime(timeval, "%Y-%m-%d %H:%M:%S").timestamp())

        # logger initiator

        log_initiator(Rule_Engine.LOG_GROUP,execution_id+Rule_Engine.CHECK_CLUSTER_STATE+timestampval)

        write_logs(common_constants.INFO, "Inside Check Cluster State  Rule Engine  Lambda")

        # Boto3 client for EMR
        client = boto3.client(Rule_Engine.EMR_CLIENT)
        available_clusters = 0
        cluster_list = []
        event[common_constants.AVAILABLE_CLUSTERS] = []
        table_name = Rule_Engine.TABLE_NAME
        running_clust = client.list_clusters(
            ClusterStates=[Rule_Engine.EMR_STATE_RUNNING, Rule_Engine.EMR_STATE_WAITING])
        response = json.dumps(running_clust, indent=4, sort_keys=True, default=str)
        clusters = running_clust[check_clusters_status_constants.CLUSTERS]

        # Boto3 client creation for DynamoDb
        response = dynamodb.Table(table_name).scan(
            FilterExpression=Attr(common_constants.STATUS).eq(Rule_Engine.EMR_STATE_RUNNING))
        item_list = response[common_constants.ITEMS]

        # Appending in the list of available clusters
        for item in item_list:
            for cluster in clusters:
                if cluster[check_clusters_status_constants.ID] == item[common_constants.CLUSTER_ID]:
                    cluster_list.append(cluster[check_clusters_status_constants.ID])
                    available_clusters = available_clusters + 1

        # Appedning ready state or wait state based on the cluster availability
        event[common_constants.AVAILABLE_CLUSTERS] = cluster_list
        if available_clusters == len(item_list):
            event[check_clusters_status_constants.STATE] = Rule_Engine.READY_STATE
        else:
            event[check_clusters_status_constants.STATE] = Rule_Engine.WAIT_STATE

    except Exception as e:
        dynamo_resp = dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).get_item(
            Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
        job_status_dict = dynamo_resp[common_constants.ITEM]
        job_status_dict[common_constants.ERROR_DETAIL] = str(e)
        job_status_dict[common_constants.STATUS] = Rule_Engine.JOB_FAILED
        job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())

        write_logs(common_constants.ERROR, "ERROR CAUGHT - {}".format(str(e)))

        dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).put_item(Item=job_status_dict)
        raise e

    return event

