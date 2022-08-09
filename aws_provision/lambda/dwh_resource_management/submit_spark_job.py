import datetime
import json
import time
import boto3
from constants.constant import Data_processor
from constants.constant import submit_spark_job_constants, common_constants
from  logger.helper_functions import log_initiator
from  logger.func_write_log import write_logs

# Boto3 client and resource creation for EMR and Dynamo
client = boto3.client(Data_processor.EMR_CLIENT)
dynamodb = boto3.resource(Data_processor.DYNAMO_CLIENT)

# Reading config file
with open('config/config.json', 'r') as file:
    config = json.load(file)


def submit_jobs(cluster_id, job_cores, job_name, log_group, bucket, prefix, batch_id, client_name, batch_name,
                client_id, execution_id, job_id, executor_memory):
    cluster_id = cluster_id
    cores_no = str(job_cores)
    batch_name = batch_name

    # Steps for Sprak submit
    steps = [{
        'Name': Data_processor.STEP_NAME + batch_name,
        'ActionOnFailure': Data_processor.ON_FAIL,
        'HadoopJarStep': {
            'Jar': Data_processor.JAR,
            'Args': [
                Data_processor.SUBMIT,
                '--master', Data_processor.MASTER,
                '--deploy-mode', Data_processor.MODE,
                '--executor-memory', executor_memory,
                '--num-executors', Data_processor.EXECUTERS,
                '--executor-cores', cores_no,
                '--py-files', config["ZIP_PATH"], config["FILE_PATH"],
                batch_name,
                log_group,
                bucket,
                prefix,
                batch_id,
                client_name,
                job_name,
                client_id,
                execution_id,
                job_id
            ]
        }
    }]

    # Submitting spark job
    action = client.add_job_flow_steps(JobFlowId=cluster_id, Steps=steps)

    StepId = action[submit_spark_job_constants.STEPS_IDS]

    return StepId


def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """

    try:

        batch_status_table = Data_processor.BATCH_STATUS_TABLE
        step_id = None
        table_name = Data_processor.TABLE_NAME
        log_group = Data_processor.LOG_GROUP
        log_initiator(log_group, event[common_constants.EXECUTION_ID] + "_DataProcessor_sparksubmit")
        write_logs(common_constants.INFO, "Inside Submit Job Lambda")
        event[submit_spark_job_constants.STEPS_PENDING] = True
        dynamodb = boto3.resource(Data_processor.DYNAMO_CLIENT)
        sqs = boto3.resource(Data_processor.SQS_CLIENT)
        sqs_client = boto3.client(Data_processor.SQS_CLIENT)
        table = dynamodb.Table(table_name)
        cluster_list = event[common_constants.AVAILABLE_CLUSTERS]

        if not cluster_list:

            event[submit_spark_job_constants.STEPS_PENDING] = False
            # time_stamp = str(datetime.datetime.now())
            # table = dynamodb.Table(batch_status_table)
            # response = table.scan()
            # item_list = response[common_constants.ITEMS]
            # for item in item_list:
            #     item[submit_spark_job_constants.END_TIME] = time_stamp
            #     dynamodb.Table(batch_status_table).put_item(Item=item)
            return event

        for cluster in cluster_list:
            cluster_metadata = dynamodb.Table(table_name).get_item(Key={common_constants.CLUSTER_ID: cluster})
            queue_url = cluster_metadata[common_constants.ITEM][common_constants.JOB_QUEUE]

            queue_name = cluster_metadata[common_constants.ITEM][common_constants.QUEUE_NAME]
            clusters = cluster_metadata[common_constants.ITEM]
            step_dict = {}
            job_status = {}
            job_names = []

            queue = sqs.get_queue_by_name(QueueName=queue_name)
            # temp= {}
            # temp[common_constants.BATCH_ID] = "-1"
            # message=json.dumps(temp)
            # queue.send_message(MessageBody= message, MessageGroupId="fifo")
            while (True):

                cluster_metadata = dynamodb.Table(table_name).get_item(Key={common_constants.CLUSTER_ID: cluster})
                clusters = cluster_metadata[common_constants.ITEM]
                time.sleep(5)
                resp = sqs_client.receive_message(
                    QueueUrl=queue_url,
                    AttributeNames=[common_constants.ALL],
                    MaxNumberOfMessages=1
                )
                try:
                    msg = resp[common_constants.MESSAGES]
                    dict = json.loads(msg[0][common_constants.BODY])
                    job_dict_bkp = dict
                    rec_handle = msg[0][common_constants.RECEIPT_HANDLE]
                    batch_id = dict[common_constants.BATCH_ID]
                    write_logs(common_constants.INFO, "Batch Id is "+batch_id)
                    batch_name = dict[common_constants.BATCH_NAME]
                    write_logs(common_constants.INFO, "Batch Name is "+batch_name)
                    client_name = dict[common_constants.CLIENT_NAME]
                    write_logs(common_constants.INFO,"Client Name is "+client_name)
                    execution_id = dict[common_constants.EXECUTION_ID]
                    client_id = dict[common_constants.CLIENT_ID]
                    write_logs(common_constants.INFO, "Client Id is "+ client_id)
                    job_id = dict[common_constants.JOB_ID]
                    write_logs(common_constants.INFO,"Job Id is "+ job_id)
                    job_name = dict[common_constants.JOB_NAME]
                    write_logs(common_constants.INFO, "Job Name is "+job_name)
                    log_group = Data_processor.LOG_GROUP
                    write_logs(common_constants.INFO, "Log group is "+log_group)
                    cores = dict["cores"]
                    write_logs(common_constants.INFO,"Number of cores are "+cores)
                except KeyError:
                    response = sqs_client.delete_queue(QueueUrl=queue_url)
                    event[common_constants.AVAILABLE_CLUSTERS] = event[common_constants.AVAILABLE_CLUSTERS].remove(
                        cluster)
                    raise
       
                if cores <= 0:
                    cores = 4

                if clusters[common_constants.AVAILABLE_CORES] >= cores - 0.2 * cores:
                    job_name = job_name.strip('"')
                    write_logs(common_constants.INFO, "Job Name is "+job_name)
                  
                    dynamo_input_response = dynamodb.Table(Data_processor.JOB_INPUT_TABLE).get_item(
                        Key={common_constants.UNIQUE_ID: batch_id + "_" + job_name})
                    bucket = dynamo_input_response[common_constants.ITEM][submit_spark_job_constants.BUCKET]
                    write_logs(common_constants.INFO, "BUCKET IS "+bucket)
                    prefix = dynamo_input_response[common_constants.ITEM][submit_spark_job_constants.EXTRACT]
                    write_logs(common_constants.INFO,"Prefix is "+prefix)

                    executor_memory = event[common_constants.EXECUTOR_MEMORY]
                    write_logs(common_constants.INFO,"Executor memory is " + executor_memory)
                    step_id = submit_jobs(cluster, cores, job_name, log_group, bucket, prefix, batch_id,
                                          client_name,
                                          batch_name, client_id, execution_id, job_id,
                                          executor_memory=executor_memory)

                    try:
                        step_dict = clusters[submit_spark_job_constants.STEP_LIST]
                        job_names = clusters[submit_spark_job_constants.JOB_NAMES]
                    except:
                        pass
                    step_dict[step_id[0]] = cores
                    # job_names[job_name] = step_id[0]
                    batch_job_name = job_name + "," + batch_name
                    job_names.append(batch_job_name)
                    clusters[submit_spark_job_constants.JOB_NAMES] = job_names
                    clusters[submit_spark_job_constants.STEP_LIST] = step_dict
                    clusters[common_constants.STATUS] = submit_spark_job_constants.STOPPED
                    clusters[common_constants.AVAILABLE_CORES] = clusters[common_constants.AVAILABLE_CORES] - cores
                    dynamodb.Table(table_name).put_item(Item=clusters)
                    write_logs(common_constants.INFO,"Item saved in "+table_name)

                  

                    test = sqs_client.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=rec_handle
                    )

                else:
                    break
                    # test = sqs_client.delete_message(
                    #     QueueUrl=queue_url,
                    #     ReceiptHandle=rec_handle
                    # )
                    # queue = sqs_client.get_queue_by_name(QueueName=queue_name)
                    # message = json.dumps(job_dict_bkp)
                    # queue.send_message(MessageBody= message, MessageGroupId="fifo")

        cluster_metadata[common_constants.STATUS] = common_constants.STOPPED
        dynamodb.Table(table_name).put_item(Item=cluster_metadata)
                
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

    return event
