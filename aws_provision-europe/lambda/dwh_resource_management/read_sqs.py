import json
import boto3
from constants.constant import Data_processor,read_sqs_constants, common_constants
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
    #Boto3 client and resource creation for SQS

    try:
        log_group = Data_processor.LOG_GROUP
        log_initiator(log_group, event[common_constants.EXECUTION_ID] + "_DataProcessor_readSQS")
        write_logs(common_constants.INFO, "Inside Read SQS Lambda")
        sqs = boto3.resource(Data_processor.SQS_CLIENT)
        sqs_client = boto3.client(Data_processor.SQS_CLIENT)
        queue_name = event[read_sqs_constants.DATA_PROCESSOR_SQS]
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
        dynamo_resp = dynamodb.Table(Data_processor.JOB_STATUS_TABLE).get_item(Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
        job_status_dict = dynamo_resp[common_constants.ITEM]
        job_status_dict[common_constants.ERROR_DETAIL] = str(e)
        job_status_dict[common_constants.STATUS] = Data_processor.JOB_FAILED
        job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())
        
        write_logs("ERROR", "ERROR CAUGHT - {}".format(str(e)))

        dynamodb.Table(Data_processor.JOB_STATUS_TABLE).put_item(Item=job_status_dict)
        raise e
    #Reading SQS Messages
    try:
        if event[common_constants.MSG_EXIST]:
            return event

    except:
        
        dict = json.loads(msg[0][common_constants.BODY])

        config[common_constants.CORES] = dict[common_constants.CORES]
        config[common_constants.JOBS] = dict[common_constants.JOBS]
        config[common_constants.CLIENT_NAME] = dict[common_constants.CLIENT_NAME]
        config[common_constants.BATCH_ID] = dict[common_constants.BATCH_ID]
        config[common_constants.CLIENT_ID] = dict[common_constants.CLIENT_ID]
        config[common_constants.EXECUTION_ID] = dict[common_constants.EXECUTION_ID]
        config[common_constants.BATCH_NAME] = dict[common_constants.BATCH_NAME]
        config[common_constants.JOB_ID] = dict[common_constants.JOB_ID]
        config[read_sqs_constants.DATA_PROCESSOR_SQS] = event[read_sqs_constants.DATA_PROCESSOR_SQS]
        config[common_constants.LOG_GROUP] = dict[common_constants.LOG_GROUP]
        config[common_constants.JOB_NAME]=dict[common_constants.JOB_NAME]

        test = sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg[0][common_constants.RECEIPT_HANDLE]
        )

    sqs_client.delete_queue(QueueUrl=queue_url)
    return config
