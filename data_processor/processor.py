import datetime
import json
import sys
import uuid

import boto3
import data_processor.logging.cloudwatch.write_logs as write_logger
import data_processor.logging.log_formatter as log_formatter
from data_processor import injector
from data_processor.constants import Constants
from data_processor.constants import processor_constants
from data_processor.dto.step_param import StepParam
from data_processor.dynamo_audit import dynamo_utils
from data_processor.logging.cloudwatch.log_utils import write_logs
from data_processor.logging.cloudwatch.write_logs import create_log_stream
from data_processor.setting import Settings
from data_processor.validate_json import validateJson
from injector import inject
from pyspark.sql import SparkSession


def create_spark_session(app_name):
    """

    :param app_name:
    :return:
    """
    # spark = SparkSession.builder.enableHiveSupport().appName(app_name).getOrCreate()
    spark = SparkSession.builder.getOrCreate()
    return spark


class DataProcessor:
    """

    """

    @inject
    def __init__(self):
        self.JDBC_jar_path = Settings.JDBC_jar_path
        self.spark = None

    def process(self, client_name, job_bucket, job_file_prefix, job_status_dict):
        """

        :param client_name:
        :param job_name:
        :param job_bucket:
        :param job_file_prefix:
        :param job_status_dict:
        """
        write_logs(processor_constants.INFO, "CDEP- Inside Process")

        app_name = "{}-{}".format(client_name, datetime.datetime.now())
        self.spark = create_spark_session(app_name)
        write_logs(processor_constants.INFO, "CDEP- Initialize Boto")
        s3 = boto3.resource('s3')
        write_logs(processor_constants.INFO,
                   "CDEP- Reading Json from job_bucket - {} and job_file_prefix - {}".format(job_bucket,
                                                                                             job_file_prefix))
        content_object = s3.Object(job_bucket, job_file_prefix)
        write_logs(processor_constants.INFO, "CDEP- content_object - {}".format(content_object))
        write_logs(processor_constants.INFO, "CDEP- Reading JSON Body")
        file_content = content_object.get()['Body'].read().decode('utf-8')
        write_logs(processor_constants.INFO, "CDEP- file_content - {}".format(file_content))
        write_logs(processor_constants.INFO, "CDEP- Storing JSON to process_config")
        process_config = json.loads(file_content)
        write_logs(processor_constants.INFO, "process_config value - {}".format(process_config))

        isValid = validateJson(process_config, Constants.SCHEMA)
        if isValid:
            write_logs(processor_constants.INFO, "JSON data Validated")
        else:
            write_logs(processor_constants.INFO, "JSON data is Invalid")
            sys.exit("Create new json for data processing")

        step_param = StepParam(self.spark, process_config)
        step_param.job_dict = job_status_dict
        step_param.batch_id = batch_id
        step_param.dynamoDb = dynamodb
        write_logs(processor_constants.INFO, "CDEP- Looping Steps")
        for step in process_config[processor_constants.STEPS]:
            method_name = step[processor_constants.METHOD_NAME]
            step_param.step_config = step
            if method_name == 'JoinTable' or method_name == 'MultiTableJoin' or method_name == 'Write':
                step_param.step_number = step[processor_constants.STEP_NUMBER]
                step_param.step_name = step[processor_constants.STEP_NAME]
            write_logs(processor_constants.INFO, "CDEP- Executing - {}".format(method_name))
            # try:
            injector.get(method_name).execute(step_param)
            # except:
            #     job_status_dict["status"] = "Failed"
            #     job_status_dict["end_time"] = str(datetime.datetime.now())
            #     dynamodb.Table(batch_table_name).put_item(Item=job_status_dict)


if __name__ == "__main__":
    batch_name = sys.argv[1]
    log_group = sys.argv[2]
    bucket = sys.argv[3]
    prefix = sys.argv[4]
    batch_id = sys.argv[5]
    client_name = sys.argv[6]
    job_name = sys.argv[7]
    client_id = sys.argv[8]
    execution_id = sys.argv[9]
    job_id = sys.argv[10]
    # profile_env = sys.args[6]
    prefix_name = prefix.split("/")[-1]
    prefix_name = prefix_name.split(".")[0]
    # Use Arg config parser
    data_processor = injector.get(DataProcessor)
    dynamodb = dynamo_utils.getDynamo()
    batch_table_name = Constants.batch_table_name
    job_table = Constants.job_table
    job_step_status_dict = Constants.Job_Step_Table
    batch_status_dict = Constants.Batch_Table
    job_status_dict = Constants.Job_Status_Table
    job_status_table = Constants.job_status_table_name
    uniqueId = batch_id + "_" + job_name
    dynamo_batch_status_response = dynamodb.Table(batch_table_name). \
        get_item(Key={processor_constants.EXECUTION_ID: execution_id})
    client_name = dynamo_batch_status_response[processor_constants.ITEM][processor_constants.CLIENT_NAME]
    batch_name = dynamo_batch_status_response[processor_constants.ITEM][processor_constants.BATCH_NAME]
    batch_type = dynamo_batch_status_response[processor_constants.ITEM][processor_constants.BATCH_TYPE]
    status = dynamo_batch_status_response[processor_constants.ITEM][processor_constants.STATUS]
    phase = dynamo_batch_status_response[processor_constants.ITEM][processor_constants.PHASE]
    start_time = dynamo_batch_status_response[processor_constants.ITEM][processor_constants.START_TIME]
    # job_name = client_name

    batch_status_dict[processor_constants.BATCH_ID] = batch_id
    batch_status_dict[processor_constants.CLIENT_NAME] = client_name
    batch_status_dict[processor_constants.BATCH_NAME] = batch_name
    batch_status_dict[processor_constants.BATCH_TYPE] = batch_type
    batch_status_dict[processor_constants.START_TIME] = start_time
    batch_status_dict[processor_constants.STATUS] = status
    batch_status_dict[processor_constants.PHASE] = phase
    batch_status_dict[processor_constants.EXECUTION_ID] = execution_id

    write_logger.log_group = log_group
    # write_logger.log_stream_name = "{}~{}".format(batch_id.replace(':', '-'),
    #                                             str(datetime.datetime.now()).replace(':', '-'))
    write_logger.log_stream_name = execution_id + str(uuid.uuid4())
    create_log_stream()
    log_formatter.batch_id = batch_id
    log_formatter.job_name = prefix_name
    log_formatter.batch_type = batch_type
    log_formatter.client_name = client_name
    log_formatter.status = status

    job_step_status_dict[processor_constants.EXECUTION_ID] = execution_id
    job_step_status_dict[processor_constants.BATCH_TYPE] = batch_type
    job_step_status_dict[processor_constants.PHASE] = phase

    job_status_dict[processor_constants.BATCH_TYPE] = batch_type
    job_status_dict[processor_constants.PHASE] = phase
    job_status_dict[processor_constants.EXECUTION_ID] = execution_id

    write_logs("Info", "Status is ---------------------------------" + status)
    write_logs("Info", "Format status is --------------------------------".format(status))

    # need to check on this logic
    write_logs(processor_constants.INFO, "Response from Dynamo - Status - {}".format(status))

    # Create 1 more Job Status Table
    # implement this in Lambda , use Sleep  for 10 mins
    # if status != "Running":
    batch_status_dict[processor_constants.STATUS] = processor_constants.RUNNING_STATUS
    dynamodb.Table(batch_table_name).put_item(Item=batch_status_dict)

    job_step_status_dict[processor_constants.PHASE] = phase
    # dynamo_job_response = dynamodb.Table(job_table).get_item(
    #     Key={processor_constants.CLIENT: client_name})
    dynamo_job_response = dynamodb.Table(job_table).get_item(Key={processor_constants.UNIQUE_ID: uniqueId})
    # ##TODO hardcoding removed
    # job_bucket = "dep-develop"
    job_bucket = dynamo_job_response[processor_constants.ITEM][processor_constants.BUCKET]
    write_logs(processor_constants.INFO, "job_bucket - {}".format(job_bucket))
    write_logs(processor_constants.INFO, "job_file_prefixs - {}".format(
        dynamo_job_response[processor_constants.ITEM][processor_constants.EXTRACT]))

    dynamo_response = dynamodb.Table(job_status_table).get_item(Key={processor_constants.EXECUTION_ID: execution_id})
    # dynamo_response = dynamodb.Table(job_status_table).scan(FilterExpression=Attr('client_batch_id').eq(batch_id))

    job_status_dict = dynamo_response[processor_constants.ITEM]

    try:

        write_logs(processor_constants.INFO, "Prefix - {}".format(prefix))

        # dynamo_response["batch_id"] = "{}-{}".format(batch_id,dynamo_response['Item']["start_time"])
        job_status_dict[processor_constants.START_TIME] = str(datetime.datetime.now())
        job_status_dict[processor_constants.STATUS] = processor_constants.RUNNING_STATUS
        job_status_dict[processor_constants.EXTRACT] = prefix

        dynamodb.Table(job_status_table).put_item(Item=job_status_dict)

        job_step_status_dict[processor_constants.EXTRACT] = prefix

        data_processor.process(client_name, job_bucket, prefix, job_step_status_dict)

        # Update job status
        job_status_dict[processor_constants.STATUS] = processor_constants.COMPLETED_STATUS
        job_status_dict[processor_constants.END_TIME] = str(datetime.datetime.now())
        dynamodb.Table(job_status_table).put_item(Item=job_status_dict)

        batch_status_dict[processor_constants.STATUS] = processor_constants.COMPLETED_STATUS
        batch_status_dict[processor_constants.END_TIME] = str(datetime.datetime.now())
        dynamodb.Table(batch_table_name).put_item(Item=batch_status_dict)
    except Exception as e:
        write_logs(processor_constants.ERROR, "ERROR CAUGHT - {}".format(str(e)))

        job_status_dict[processor_constants.ERROR_DETAIL] = str(e)
        job_status_dict[processor_constants.END_TIME] = str(datetime.datetime.now())
        job_status_dict[processor_constants.STATUS] = processor_constants.FAILED_STATUS
        dynamodb.Table(job_status_table).put_item(Item=job_status_dict)

        batch_status_dict[processor_constants.ERROR_DETAIL] = str(e)
        batch_status_dict[processor_constants.STATUS] = processor_constants.FAILED_STATUS
        batch_status_dict[processor_constants.END_TIME] = str(datetime.datetime.now())
        dynamodb.Table(batch_table_name).put_item(Item=batch_status_dict)
