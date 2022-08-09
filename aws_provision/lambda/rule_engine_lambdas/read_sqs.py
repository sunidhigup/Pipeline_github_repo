import json
import boto3
import datetime
from constants.constant import Rule_Engine
from constants.constant import read_sqs_constants, common_constants
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
        log_initiator(Rule_Engine.LOG_GROUP,execution_id+Rule_Engine.READ_SQS_MESSAGE+timestampval)

        write_logs(common_constants.INFO, "Inside Read SQS Message Rule Engine  Lambda")

        # Boto3 client and resource creation for SQS
        sqs = boto3.resource(Rule_Engine.SQS_CLIENT)
        sqs_client = boto3.client(Rule_Engine.SQS_CLIENT)
        queue_name = event[read_sqs_constants.RULE_ENGINE_SQS]
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        queue_url = queue.url
        config = {}
        resp = sqs_client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[common_constants.ALL],
            MaxNumberOfMessages=1
        )
        msg = resp[common_constants.MESSAGES]
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

    # Reading SQS Messages
    try:
        if event[common_constants.MSG_EXIST]:
            return event

    except:

        job_dict = json.loads(msg[0][common_constants.BODY])

        config[common_constants.CORES] = job_dict[common_constants.CORES]
        config[common_constants.JOBS] = job_dict[common_constants.JOBS]
        config[common_constants.CLIENT_NAME] = job_dict[common_constants.CLIENT_NAME]
        config[common_constants.BATCH_ID] = job_dict[common_constants.BATCH_ID]
        config[common_constants.CLIENT_ID] = job_dict[common_constants.CLIENT_ID]
        config[common_constants.EXECUTION_ID] = job_dict[common_constants.EXECUTION_ID]
        config[common_constants.BATCH_NAME] = job_dict[common_constants.BATCH_NAME]
        config[read_sqs_constants.RULE_ENGINE_SQS] = event[read_sqs_constants.RULE_ENGINE_SQS]
        config[common_constants.PROFILE_ENV] = event[common_constants.PROFILE_ENV]
        config[common_constants.PROFILE_ENV_BUCKET] = event[common_constants.PROFILE_ENV_BUCKET]

        test = sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg[0][common_constants.RECEIPTHANDLE]
        )

    return config
