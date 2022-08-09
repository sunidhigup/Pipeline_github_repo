import json
import time
import datetime
import boto3

from constants.constant import Rule_Engine
from constants.constant import submit_spark_job_constants, common_constants
from env_fetcher.env_fetcher import read_config
from logger.helper_functions import log_initiator
from logger.func_write_log import write_logs

# Boto3 client and resource creation for EMR and Dynamo
client = boto3.client(Rule_Engine.EMR_CLIENT)
dynamodb = boto3.resource(Rule_Engine.DYNAMO_CLIENT)
table_name = Rule_Engine.TABLE_NAME


# Reading config file
# with open('config/config.json', 'r') as file:
# config = json.load(file)


def submit_jobs(event, cluster_id, job_cores, batch_id, client_name, batch_name, table_name, execution_id,
                executor_memory):
    """

    :param execution_id:
    :param batch_name:
    :param cluster_id:
    :param job_cores:
    :param batch_id:
    :param client_name:
    :param table_name:
    :param executor_memory:
    :return:
    """

    #write_logs("Info", "Inside submit Jobs")
    cluster_id = cluster_id
    cores_no = str(job_cores)
    id = "{}~{}".format(batch_id, table_name)
    #print("going to read config")
    #print(event[common_constants.PROFILE_ENV])
    #print(common_constants.Json_Config)
    #print(event[common_constants.PROFILE_ENV_BUCKET])
    config = read_config(PROFILE_ENV=event[common_constants.PROFILE_ENV],
                         BUCKETNAME=event[common_constants.PROFILE_ENV_BUCKET],
                         KEYNAME=common_constants.Json_Config)
    #print("parameters fetched")
    #print(event[common_constants.PROFILE_ENV_BUCKET])
    #print(common_constants.Json_Config)
    steps = [{
        'Name': Rule_Engine.STEP_NAME + id,
        'ActionOnFailure': Rule_Engine.ON_FAIL,
        'HadoopJarStep': {
            'Jar': Rule_Engine.JAR,
            'Args': [
                Rule_Engine.SUBMIT,
                # '--master', Rule_Engine.MASTER,
                # '--deploy-mode', Rule_Engine.MODE,
                '--executor-memory', executor_memory,
                '--num-executors', Rule_Engine.EXECUTERS,
                '--executor-cores', cores_no,
                '--jars', config["S3_DETAILS"]["JAR_PATH"],
                '--py-files', config["S3_DETAILS"]["ZIP_PATH"], config["S3_DETAILS"]["FILE_PATH"],
                client_name,
                table_name,
                batch_name,
                batch_id,
                execution_id,
                event[common_constants.PROFILE_ENV],
                event[common_constants.PROFILE_ENV_BUCKET]

            ]
        }
    }]

    action = client.add_job_flow_steps(JobFlowId=cluster_id, Steps=steps)
    StepId = action["StepIds"]

    return StepId


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
        time.sleep(60)

        # logger initiator
        log_initiator(Rule_Engine.LOG_GROUP,execution_id+Rule_Engine.SUBMIT_JOB+timestampval)

        write_logs(common_constants.INFO, "Inside Submit Job Lambda")
        event[submit_spark_job_constants.STEPS_PENDING] = True
        dynamodb = boto3.resource(Rule_Engine.DYNAMO_CLIENT)
        sqs_client = boto3.client(Rule_Engine.SQS_CLIENT)
        cluster_list = event[common_constants.AVAILABLE_CLUSTERS]

        if not cluster_list:
            event[submit_spark_job_constants.STEPS_PENDING] = False
            return event

        job_name = ""
        cores = 0

        for cluster in cluster_list:
            #print("Table name for cluster id is "+table_name)
            #print(common_constants.CLUSTER_ID)
            #print(cluster)
            cluster_metadata = dynamodb.Table(table_name).get_item(Key={common_constants.CLUSTER_ID: cluster})
            #print("Cluster detail inside for loop")
            #print(cluster_metadata)
            queue_url = cluster_metadata[common_constants.ITEM][common_constants.JOB_QUEUE]
            queue_name = cluster_metadata[common_constants.ITEM][common_constants.QUEUE_NAME]
            step_dict = {}

            while True:
                #print("Table name for cluster id is " + table_name)
                #print(common_constants.CLUSTER_ID)
                #print(cluster)
                cluster_metadata = dynamodb.Table(table_name).get_item(Key={common_constants.CLUSTER_ID: cluster})
                #print("Fretching again inside while loop")
                clusters = cluster_metadata[common_constants.ITEM]
                #print("cluster details inside while loop")
                #print(cluster_metadata)
                time.sleep(5)
                resp = sqs_client.receive_message(
                    QueueUrl=queue_url,
                    AttributeNames=[common_constants.ALL],
                    MaxNumberOfMessages=1
                )
                try:
                    msg = resp[common_constants.MESSAGES]
                    job_dict = json.loads(msg[0][common_constants.BODY])

                    rec_handle = msg[0][common_constants.RECEIPT_HANDLE]
                    batch_name = job_dict[common_constants.BATCH_NAME]
                    job_dict.pop(common_constants.BATCH_NAME)
                    batch_id = job_dict[common_constants.BATCH_ID]
                    job_dict.pop(common_constants.BATCH_ID)
                    client_name = job_dict[common_constants.CLIENT_NAME]
                    job_dict.pop(common_constants.CLIENT_NAME)
                    execution_id = job_dict[common_constants.EXECUTION_ID]
                    job_dict.pop(common_constants.EXECUTION_ID)

                except Exception as e:
                    response = sqs_client.delete_queue(QueueUrl=queue_url)
                    event[common_constants.AVAILABLE_CLUSTERS] = event[common_constants.AVAILABLE_CLUSTERS].remove(
                        cluster)
                    #print(e)
                    break

                # After removing the all required key value pair from dict assigning job name and core from dict
                for key, value in job_dict.items():
                    job_name = key
                    #print("Job name inside for loop")
                    #print(job_name)
                    cores = value
                    #print("core inside for loop")
                    #print(cores)

                # if core from SQS is negative or zero then assigning it to one
                if cores <= 0:
                    cores = 4

                if clusters[common_constants.AVAILABLE_CORES] >= cores - (0.2 * cores):
                    job_name = job_name.strip('"')
                    executor_memory = event[common_constants.EXECUTOR_MEMORY]
                    #print("Going to create stepid")
                    step_id = submit_jobs(event, cluster, cores, batch_id, client_name, batch_name, job_name,
                                          execution_id,
                                          executor_memory=executor_memory)

                    write_logs(common_constants.INFO,"Job submitted")
                    try:
                        step_dict = clusters[submit_spark_job_constants.STEP_LIST]
                    except:
                        pass
                    step_dict[step_id[0]] = cores
                    clusters[submit_spark_job_constants.STEP_LIST] = step_dict
                    clusters[common_constants.STATUS] = submit_spark_job_constants.STOPPED
                    clusters[common_constants.AVAILABLE_CORES] = clusters[
                                                                        common_constants.AVAILABLE_CORES] - cores
                    dynamodb.Table(table_name).put_item(Item=clusters)
                    test = sqs_client.delete_message(
                       QueueUrl=queue_url,
                      ReceiptHandle=rec_handle
                     )

                else:
                    break

        #cluster_metadata[common_constants.STATUS] = common_constants.STOPPED
        #dynamodb.Table(table_name).put_item(Item=cluster_metadata)

    except Exception as e:
        dynamo_resp = dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).get_item(
            Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
        job_status_dict = dynamo_resp[common_constants.ITEM]
        job_status_dict[common_constants.ERROR_DETAIL] = str(e)
        job_status_dict[common_constants.STATUS] = Rule_Engine.JOB_FAILED
        job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())

        write_logs(common_constants.ERROR, "ERROR CAUGHT - {}".format(str(e)))

        dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).put_item(Item=job_status_dict)
        cluster_metadata[common_constants.STATUS] = common_constants.STOPPED
        #cluster_metadata[common_constants.CLUSTER_ID]=event[common_constants.CLUSTER_ID]
        #dynamodb.Table(table_name).put_item(Item=cluster_metadata)
        raise e

    return event
