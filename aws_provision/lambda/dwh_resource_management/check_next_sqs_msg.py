import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import datetime
from constants.constant import Data_processor,check_next_sqs_msg_constants, common_constants,read_sqs_constants
from  logger.helper_functions import log_initiator
from  logger.func_write_log import write_logs

dynamodb = boto3.resource(Data_processor.DYNAMO_CLIENT)

def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    #Creating boto3 resource for dynamoDb

    try:
        table_name = Data_processor.TABLE_NAME
        log_group = Data_processor.LOG_GROUP
        log_initiator(log_group, event[common_constants.EXECUTION_ID] + "_DataProcessor_checknextbatch")
        write_logs(common_constants.INFO, "Inside check next msg Lambda")

        time_stamp = str(datetime.datetime.now())
       
        cluster_metadata = dynamodb.Table(table_name).get_item(Key={common_constants.CLUSTER_ID: event[common_constants.CLUSTER_ID]})
        queue_url = cluster_metadata[common_constants.ITEM][common_constants.JOB_QUEUE]
        queue_name = cluster_metadata[common_constants.ITEM][common_constants.QUEUE_NAME]
        
        #Creating boto3 resource for SQS
        sqs = boto3.resource(Data_processor.SQS_CLIENT)
        sqs_client = boto3.client(Data_processor.SQS_CLIENT)
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        dict_msg = event[common_constants.JOBS]
        job_status_dict = {}

        #Updating the queue with different parameters
        for msg in dict_msg:
            message=json.dumps(msg)
            temp = {}


            temp[message] = dict_msg[msg]
            temp[common_constants.CORES]=event[common_constants.CORES]
            temp[common_constants.BATCH_NAME] = event[common_constants.BATCH_NAME]
            temp[common_constants.BATCH_ID] = event[common_constants.BATCH_ID]
            temp[common_constants.CLIENT_NAME] = event[common_constants.CLIENT_NAME]
            temp[common_constants.CLIENT_ID]=event[common_constants.CLIENT_ID]
            temp[common_constants.EXECUTION_ID]=event[common_constants.EXECUTION_ID]
            temp[common_constants.JOB_NAME]=event[common_constants.JOB_NAME]
            temp[common_constants.JOB_ID] = event[common_constants.JOB_ID]
            message=json.dumps(temp)
            queue.send_message(MessageBody=message,MessageGroupId=check_next_sqs_msg_constants.QUEUE_FIFO)
        
        time_stamp = str(datetime.datetime.now())
       
        batch_status_table = Data_processor.BATCH_STATUS_TABLE
        batch_status_dict = {}
        
        batch_status_dict[common_constants.EXECUTION_ID] = event[common_constants.EXECUTION_ID]
        batch_status_dict[common_constants.BATCH_ID] = event[common_constants.BATCH_ID] 
        batch_status_dict[common_constants.BATCH_NAME] = event[common_constants.BATCH_NAME]
        batch_status_dict[common_constants.CLIENT_NAME] = event[common_constants.CLIENT_NAME]
        batch_status_dict[common_constants.CLIENT_ID]=event[common_constants.CLIENT_ID]
        batch_status_dict[common_constants.JOB_NAME]=event[common_constants.JOB_NAME]
        batch_status_dict[common_constants.JOB_ID] = event[common_constants.JOB_ID]
        batch_status_dict[check_next_sqs_msg_constants.BATCH_TYPE] = ''
        batch_status_dict[check_next_sqs_msg_constants.START_TIME] = time_stamp
        batch_status_dict[common_constants.STATUS] = check_next_sqs_msg_constants.STARTING
        batch_status_dict[check_next_sqs_msg_constants.PHASE] = check_next_sqs_msg_constants.PROCESSING
        
        # putting status in dynamoDb table
        dynamodb.Table(batch_status_table).put_item(Item=batch_status_dict)
        
        sqs = boto3.resource(Data_processor.SQS_CLIENT)
    
        sqs_client = boto3.client(Data_processor.SQS_CLIENT)
        
        queue = sqs.get_queue_by_name(QueueName=event[check_next_sqs_msg_constants.QUEUE_KEY])
        queue_url = queue.url
        
        resp = sqs_client.receive_message(
                QueueUrl=queue_url,
                AttributeNames=[common_constants.ALL],
                MaxNumberOfMessages=1
            )
            
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
    try:
        msg = resp[common_constants.MESSAGES]
        
        dict = json.loads(msg[0][common_constants.BODY])
        event[common_constants.CORES]=dict[common_constants.CORES]
        event[common_constants.JOBS]=dict[common_constants.JOBS]
        event[common_constants.CLIENT_NAME] = dict[common_constants.CLIENT_NAME]
        event[common_constants.BATCH_ID] = dict[common_constants.BATCH_ID]
        event[common_constants.CLIENT_ID] = dict[common_constants.CLIENT_ID]
        event[common_constants.EXECUTION_ID] = dict[common_constants.EXECUTION_ID]
        event[common_constants.BATCH_NAME] = dict[common_constants.BATCH_NAME]
        event[common_constants.JOB_ID] = dict[common_constants.JOB_ID]
        event[read_sqs_constants.DATA_PROCESSOR_SQS] = event[read_sqs_constants.DATA_PROCESSOR_SQS]
        event[common_constants.LOG_GROUP] = dict[common_constants.LOG_GROUP]
        event[common_constants.JOB_NAME]=dict[common_constants.JOB_NAME]

        test = sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=msg[0][common_constants.RECEIPT_HANDLE]
                )
        event[common_constants.MSG_EXIST]= True
        
    except:
        event[common_constants.MSG_EXIST]=False
        pass
    
    return event
