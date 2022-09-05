import json
import math
import datetime
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from constants.constant import Resource_manage,write_sqs_constants,character_constants

from logger.helper_functions import log_initiator
from logger.func_write_log import write_logs

# Boto3 client creation for EMR
client = boto3.client(Resource_manage.EMR_CLIENT)
# Boto3 resource creation for S3
s3 = boto3.resource(Resource_manage.S3_CLIENT)
# Boto3 resource creation for DynamoDb
dynamodb = boto3.resource(Resource_manage.DYNAMO_CLIENT)
# Boto3 resource creation for SQS
sqs = boto3.resource(Resource_manage.SQS_CLIENT)
file_size_multiplier = Resource_manage.FILE_SIZE_CONST
emr_config = {}


def s3_size_calc(bucket, prefix, extns):
    """S3 size calculator

    Args:
        bucket (_type_): _description_
        prefix (_type_): _description_
        extns (_type_): _description_

    Returns:
        int: size of bucket
    """
    my_bucket = s3.Bucket(bucket)
    file_names = my_bucket.objects.filter(Prefix=prefix)
    extensions = extns
    total_size = 0
    for object_summary in file_names:
        f = object_summary.key
        if f.split('.')[-1] in extensions:
            total_size = total_size + object_summary.size

    total_size = ((
                          total_size / Resource_manage.UNIT_CONVERT) / Resource_manage.UNIT_CONVERT) / Resource_manage.UNIT_CONVERT

    return total_size


def lambda_handler(event, context):
    client_name = event[write_sqs_constants.CLIENT_NAME]
    batch_name = event[write_sqs_constants.BATCH_NAME]
    execution_id = event[write_sqs_constants.EXECUTION_ID]

    time_stamp = str(datetime.datetime.now())


    job_status_dict = {}

    job_level_trigger = False

    # write_batch()

    try:
        if event["table_name"] or event["job_name"]:
            table_name = event["table_name"]
            job_level_trigger = True
    except:
        pass
    if event["rule_engine"]:

        try:
            timeval = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            timestampval = str(datetime.datetime.strptime(timeval, "%Y-%m-%d %H:%M:%S").timestamp())
            log_initiator(Resource_manage.RULE_ENGINE_LOG_GROUP,execution_id+timestampval)
            write_logs("Info", "Inside write to SQS Resource management Lambda")

            job_status_dict["client_name"] = event["client_name"]
            job_status_dict["batch_name"] = event["batch_name"]
            job_status_dict["client_id"] = event["client_id"]
            job_status_dict["batch_id"] = event["batch_id"]
            job_status_dict["execution_id"] = event["execution_id"]
            job_status_dict["start_time"] = time_stamp
            job_status_dict["status"] = 'Running'

            dynamodb.Table(Resource_manage.RULE_JOB_STATUS_TABLE).put_item(Item=job_status_dict)

            # Create SQS Queue at batch level for Rule Engine
            if event["table_name"]:
                queue_name = client_name.replace(" ","") + batch_name.replace(" ","") + table_name.replace(" ","")+ write_sqs_constants.FIFO_SUFFIX_RULE_ENGINE
            else:
                queue_name = client_name.replace(" ","") + batch_name.replace(" ","")+ write_sqs_constants.FIFO_SUFFIX_RULE_ENGINE


            event["rule_engine_sqs"] = queue_name


            queue = sqs.create_queue(QueueName=queue_name, Attributes={'FifoQueue': Resource_manage.FIFO,
                                                                    'ContentBasedDeduplication': Resource_manage.DUPLICATION,
                                                                    'VisibilityTimeout': Resource_manage.VISIBLE_TIMEOUT})

            write_logs("Info", "Queue created successfully in  write to SQS Resource management Lambda")
            dynamo_meta_response = dynamodb.Table(Resource_manage.RULE_METADATA).scan()
            # dynamo_meta_responses = dynamodb.Table(Resource_manage.RULE_METADATA).get_item(
            #     Key={'id': event["client_name"] + "_" + event["batch_name"] + "_" + event["table_name"]})



            for item in dynamo_meta_response['Items']:
                msg = {}
                job_dict = {}
                job_name = item["table_name"]
                client_name = item["client_name"]
                batch_id = event["batch_id"]
                client_id = event["client_id"]
                execution_id = event["execution_id"]
                params = json.loads(item['params'])
                bucket = params['bucket_name']
                batch_name_dtable = params['batch_name']

                prefix = Resource_manage.DEP_CONST \
                        + "/" \
                        + Resource_manage.DATASET_CONST \
                        + "/" \
                        + params['batch_name'] \
                        + " / " \
                        + Resource_manage.INPUT_CONST \
                        + " / " \
                        + params['table_name']

                extensions = Resource_manage.EXT

                if job_level_trigger:
                    if (batch_name == batch_name_dtable) and event["table_name"] == job_name:
                        data_size = s3_size_calc(bucket, prefix, extensions)
                        cores = max(int(math.ceil(file_size_multiplier * data_size)) - (
                                .2 * int(math.ceil(file_size_multiplier * data_size))), write_sqs_constants.DEFAULT_CORES)
                        cores = cores if (cores % 2 == 0) else (cores + 1)
                        job_dict[job_name] = cores
                        msg["cores"] = cores
                        msg["client_name"] = client_name
                        msg["batch_id"] = batch_id
                        msg["client_id"] = client_id
                        msg["execution_id"] = execution_id
                        msg['batch_name'] = batch_name
                        msg["jobs"] = job_dict

                        message = json.dumps(msg)
                        queue.send_message(MessageBody=message, MessageGroupId="fifo")
                else:
                    if batch_name == batch_name_dtable:
                        job_status_dict["table_name"] = job_name
                        dynamodb.Table(Resource_manage.RULE_JOB_STATUS_TABLE).put_item(Item=job_status_dict)
                        data_size = s3_size_calc(bucket, prefix, extensions)
                        print(data_size)
                        total_data_size += data_size
                        input_count += 1
                        cores = int(math.ceil(file_size_multiplier * data_size))
                        temp_dict[job_name] = cores
                        print("inside batch")
                        avg_cores = int(int(math.ceil(file_size_multiplier * total_data_size)) / int(input_count))

                        msg["cores"] = max(avg_cores, 4)
                        msg["client_name"] = client_name
                        msg["batch_id"] = batch_id
                        msg["client_id"] = client_id
                        msg["execution_id"] = execution_id
                        msg['batch_name'] = batch_name
                        msg["jobs"] = temp_dict

                        message = json.dumps(msg)
                        queue.send_message(MessageBody=message, MessageGroupId="fifo")

        except Exception as e:
            job_status_dict["error_detail"] = str(e)
            job_status_dict["status"] = "Failed"
            job_status_dict["end_time"] = str(datetime.datetime.now())
            write_logs("ERROR", "ERROR CAUGHT - {}".format(str(e)))
            dynamodb.Table(Resource_manage.RULE_JOB_STATUS_TABLE).put_item(Item=job_status_dict)
            raise e

    else:
        # Create SQS Queue at batch level for Data Processor

        try:
            # Create SQS Queue at batch level for Data Processor
            timeval = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            timestampval = str(datetime.datetime.strptime(timeval, "%Y-%m-%d %H:%M:%S").timestamp())
            log_initiator(Resource_manage.DATA_PROCESSOR_LOG_GROUP,
                          execution_id + "_DataProcessor_writesqs" + timestampval)
            write_logs("Info", "Starting Data Processor")
            if write_sqs_constants.TABLE_NAME in event:
                write_logs("Info", "Table Name is present")
                queue_name = client_name.replace(" ", "") + character_constants.UNDERSCORE + batch_name.replace(" ",
                                                                                                                "") + character_constants.UNDERSCORE + \
                             event[write_sqs_constants.TABLE_NAME].replace(" ",
                                                                           "") + write_sqs_constants.EXTENSION_QUEUE
            else:
                write_logs("Info", "Table Name is not present")
                queue_name = client_name.replace(" ", "") + character_constants.UNDERSCORE + batch_name.replace(" ",
                                                                                                                "") + write_sqs_constants.EXTENSION_QUEUE
            event[write_sqs_constants.SQS_DATA_PROCESSOR] = queue_name
            queue = sqs.create_queue(QueueName=queue_name, Attributes={'FifoQueue': Resource_manage.FIFO,
                                                                       'ContentBasedDeduplication': Resource_manage.DUPLICATION,
                                                                       'VisibilityTimeout': Resource_manage.VISIBLE_TIMEOUT})
            write_logs("Info", "Queue created with name : " + queue_name)
            # queue = sqs.get_queue_by_name(QueueName=Resource_manage.DWH_QUEUE)
            dynamo_meta_response = dynamodb.Table(Resource_manage.DWH_METADATA).scan(
                FilterExpression=Attr(Resource_manage.IS_ACTIVE).eq(Resource_manage.TRUE))

            for item in dynamo_meta_response[write_sqs_constants.ITEMS]:
                data_size = 0
                total_data_size = 0
                input_count = 0
                msg = {}
                temp_dict = {}
                client_name = event[write_sqs_constants.CLIENT_NAME]
                write_logs("Info", "Client name is  : " + client_name)
                batch_id = event[write_sqs_constants.BATCH_ID]
                write_logs("Info", "Batch Id  is  : " + batch_id)
                batch_name = event[write_sqs_constants.BATCH_NAME]
                write_logs("Info", "Batch Name  is  : " + batch_name)
                log_group = item[write_sqs_constants.LOG_GROUP]
                write_logs("Info", "Log Group is " + log_group)
                batch_name_dtable = item[write_sqs_constants.BATCH_NAME]
                write_logs("Info", "Batch Name from meta table is  " + batch_name_dtable)
                job_id = event[write_sqs_constants.JOB_ID]
                write_logs("Info", "Job Id is  " + job_id)
                client_id = event[write_sqs_constants.CLIENT_ID]
                write_logs("Info", "Client Id is  " + client_id)
                execution_id = event[write_sqs_constants.EXECUTION_ID]
                write_logs("Info", "Execution Id is  " + execution_id)
                job_name = event[write_sqs_constants.JOB_NAME]
                write_logs("Info", "Job Name is  " + job_name)

                # check if batch name from event matches batch name from table
                if batch_name_dtable == batch_name:
                    dynamo_job_response = dynamodb.Table(Resource_manage.JOB_TABLE).get_item(
                        Key={write_sqs_constants.JOB_ID: job_id})
                    extracts = dynamo_job_response[write_sqs_constants.ITEM][write_sqs_constants.EXTRACTS].split(
                        character_constants.COMMA)
                    write_logs("Info", "extracts = {}".format(extracts))

                    if job_level_trigger:

                        dynamo_input_response = dynamodb.Table(Resource_manage.JOB_INPUT_TABLE).get_item(
                            Key={write_sqs_constants.UNIQUE_ID: batch_id + event[write_sqs_constants.JOB_NAME]})
                        write_logs("Info", "dynamo_input_response = {}".format(dynamo_input_response))
                        bucket = dynamo_input_response[write_sqs_constants.ITEM][write_sqs_constants.BUCKET]
                        prefix = dynamo_input_response[write_sqs_constants.ITEM][write_sqs_constants.PREFIX]
                        extensions = dynamo_input_response[write_sqs_constants.ITEM][
                            write_sqs_constants.EXTENSIONS].split(',')

                        data_size = s3_size_calc(bucket, prefix, extensions)
                        total_data_size += data_size
                        input_count += 1
                        cores = int(math.ceil(file_size_multiplier * data_size))
                        temp_dict[event[write_sqs_constants.JOB_NAME]] = cores

                    else:
                        for extract in extracts:
                            write_logs("Info", "extract = {}".format(extract))
                            input_ref_key = extract.split("/")[-1].split(".")[0]
                            write_logs("Info", "input_ref_key = {}".format(input_ref_key))

                            dynamo_input_response = dynamodb.Table(Resource_manage.JOB_INPUT_TABLE).get_item(
                                Key={write_sqs_constants.UNIQUE_ID: batch_id + character_constants.UNDERSCORE + event[
                                    write_sqs_constants.JOB_NAME]})
                            bucket = dynamo_input_response[write_sqs_constants.ITEM][write_sqs_constants.BUCKET]
                            prefix = dynamo_input_response[write_sqs_constants.ITEM][write_sqs_constants.PREFIX]
                            extensions = dynamo_input_response[write_sqs_constants.ITEM][
                                write_sqs_constants.EXTENSIONS].split(',')

                            data_size = s3_size_calc(bucket, prefix, extensions)
                            total_data_size += data_size
                            input_count += 1
                            cores = int(math.ceil(file_size_multiplier * data_size))
                            temp_dict[input_ref_key] = cores

                    avg_cores = int(int(math.ceil(file_size_multiplier * total_data_size)) / int(input_count))
                    msg[write_sqs_constants.CORES] = avg_cores
                    msg[write_sqs_constants.CLIENT_NAME] = client_name
                    msg[write_sqs_constants.BATCH_ID] = batch_id
                    msg[write_sqs_constants.JOBS] = temp_dict
                    msg[write_sqs_constants.CLIENT_ID] = client_id
                    msg[write_sqs_constants.EXECUTION_ID] = execution_id
                    msg[write_sqs_constants.BATCH_NAME] = batch_name
                    msg[write_sqs_constants.JOB_ID] = job_id
                    msg[write_sqs_constants.LOG_GROUP] = log_group
                    write_logs("Info", "Mesage for log group written in queue with name " + log_group)
                    msg[write_sqs_constants.JOB_NAME] = job_name
                    message = json.dumps(msg)
                    # write_logs("Info", "Message sent in " + queue_name + " is " + str(message))
                    write_logs("Info", "Message " + message + " written in queue," + queue_name)
                    queue.send_message(MessageBody=message, MessageGroupId=write_sqs_constants.FIFO_QUEUE)

        except Exception as e:
            job_status_dict["error_detail"] = str(e)
            job_status_dict["status"] = "Failed"
            job_status_dict["end_time"] = str(datetime.datetime.now())
            write_logs("ERROR", "ERROR CAUGHT - {}".format(str(e)))
            dynamodb.Table(Resource_manage.DWH_STATUS_TABLE).put_item(Item=job_status_dict)
            raise e


    return event


def write_batch():
    """
    Fills an Amazon DynamoDB table with the specified data, using the Boto3
    Table.batch_writer() function to put the items in the table.
    Inside the context manager, Table.batch_writer builds a list of
    requests. On exiting the context manager, Table.batch_writer starts sending
    batches of write requests to Amazon DynamoDB and automatically
    handles chunking, buffering, and retrying.
    :param movies: The data to put in the table. Each item must contain at least
                   the keys required by the schema that was specified when the
                   table was created.
    """
    try:
        path = 'instance_mapping.json'
        with open(path, 'r') as file:
            file_data = json.load(file)
    except FileNotFoundError:
        write_logs("Error",f"File {path} not found")
        raise
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('dep_instance_mapping')
    try:
        with table.batch_writer() as writer:
            for data in file_data:
                writer.put_item(Item=data)
    except ClientError as err:
        write_logs("Error",
            "Couldn't load data into table %s. Here's why: %s: %s", table.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
