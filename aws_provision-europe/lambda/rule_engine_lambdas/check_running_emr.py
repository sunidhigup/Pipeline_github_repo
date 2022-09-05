import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from constants.constant import Rule_Engine
from constants.constant import common_constants, common_constants
import datetime
from logger.helper_functions import log_initiator
from logger.func_write_log import write_logs

dynamodb = boto3.resource(Rule_Engine.DYNAMO_CLIENT)


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
        log_initiator(Rule_Engine.LOG_GROUP,execution_id+Rule_Engine.CHECK_CLUSTER_AVAILABLE+timestampval)
        write_logs(common_constants.INFO, "Inside Check Available Cluster Rule Engine Lambda")

        # Creating boto3 resource client for dynamoDb
        table_name = Rule_Engine.TABLE_NAME

        table = dynamodb.Table(table_name)
        response = dynamodb.Table(table_name).scan(
            FilterExpression=Attr(common_constants.STATUS).eq(common_constants.RUNNING_STATUS))

        # Updating cluster availibility based on EMR status
        if response[common_constants.ITEMS]:
            event[common_constants.CLUSTER_AVAILABLE] = True

        else:
            event[common_constants.CLUSTER_AVAILABLE] = False

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