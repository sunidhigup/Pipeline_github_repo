import datetime
import json
import boto3
from constants.constant import Rule_Engine
from constants.constant import check_next_sqs_msg_constants, common_constants
from logger.helper_functions import log_initiator
from logger.func_write_log import write_logs


def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    dynamodb = boto3.resource(Rule_Engine.DYNAMO_CLIENT)
    table_name = Rule_Engine.TABLE_NAME
    table = dynamodb.Table(table_name)
    try:
        execution_id = event[common_constants.EXECUTION_ID]

        timeval = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        timestampval = str(datetime.datetime.strptime(timeval, "%Y-%m-%d %H:%M:%S").timestamp())

        # # logger initiator
        log_initiator(Rule_Engine.LOG_GROUP,execution_id+Rule_Engine.CBMS+timestampval)
        write_logs(common_constants.INFO, "Inside Check batch Status Messages Rule Engine  Lambda")
        job_status_dict = {}


        cluster_metadata = dynamodb.Table(table_name).get_item(
            Key={common_constants.CLUSTER_ID: event[common_constants.CLUSTER_ID]})
        queue_url = cluster_metadata[common_constants.ITEM][common_constants.JOB_QUEUE]
        queue_name = cluster_metadata[common_constants.ITEM][common_constants.QUEUE_NAME]

        # Creating boto3 resource for SQS
        sqs = boto3.resource(Rule_Engine.SQS_CLIENT)
        sqs_client = boto3.client(Rule_Engine.SQS_CLIENT)
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        dict_msg = event[common_constants.JOBS]

        # Updating the queue with different parameters
        for msg in dict_msg:
            message = json.dumps(msg)
            sqs_msg = {}
            sqs_msg[message] = dict_msg[msg]
            sqs_msg[common_constants.BATCH_NAME] = event[common_constants.BATCH_NAME]
            sqs_msg[common_constants.BATCH_ID] = event[common_constants.BATCH_ID]
            sqs_msg[common_constants.CLIENT_NAME] = event[common_constants.CLIENT_NAME]
            sqs_msg[common_constants.EXECUTION_ID] = event[common_constants.EXECUTION_ID]

        message = json.dumps(sqs_msg)
        queue.send_message(MessageBody=message, MessageGroupId="fifo")

        sqs = boto3.resource(Rule_Engine.SQS_CLIENT)

        sqs_client = boto3.client(Rule_Engine.SQS_CLIENT)

        queue = sqs.get_queue_by_name(QueueName=event[check_next_sqs_msg_constants.QUEUE_KEY])
        queue_url = queue.url
        resp = sqs_client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[common_constants.ALL],
            MaxNumberOfMessages=1
        )

    except Exception as e:
        dynamo_resp = dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).get_item(
            Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
        job_status_dict = dynamo_resp[common_constants.ITEM]
        job_status_dict[common_constants.ERROR_DETAIL] = str(e)
        job_status_dict[common_constants.STATUS] = Rule_Engine.JOB_FAILED
        job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())

        # write_logs(common_constants.ERROR, "ERROR CAUGHT - {}".format(str(e)))

        dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).put_item(Item=job_status_dict)
        cluster_metadata[common_constants.STATUS] = common_constants.STOPPED
        dynamodb.Table(table_name).put_item(Item=cluster_metadata)
        raise e
    try:
        msg = resp[common_constants.MESSAGES]

        dict = json.loads(msg[0][common_constants.BODY])
        event[common_constants.CORES] = dict[common_constants.CORES]
        event[common_constants.JOBS] = dict[common_constants.JOBS]
        event[common_constants.CLIENT_NAME] = dict[common_constants.CLIENT_NAME]
        event[common_constants.BATCH_NAME] = dict[common_constants.BATCH_NAME]
        event[common_constants.BATCH_ID] = dict[common_constants.BATCH_ID]
        event[common_constants.CLIENT_ID] = dict[common_constants.CLIENT_ID]
        event[common_constants.EXECUTION_ID] = dict[common_constants.EXECUTION_ID]

        test = sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg[0][common_constants.RECEIPT_HANDLE]
        )
        event[common_constants.MSG_EXIST] = True

    except:
        event[common_constants.MSG_EXIST] = False
        pass

    return event
