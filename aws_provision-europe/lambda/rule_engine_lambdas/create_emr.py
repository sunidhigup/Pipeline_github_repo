import datetime
# from datetime import datetime
import boto3
from constants.constant import Rule_Engine
from constants.constant import create_emr_constants, common_constants
from logger.helper_functions import log_initiator
from logger.func_write_log import write_logs

client = boto3.client(Rule_Engine.EMR_CLIENT)
dynamodb = boto3.resource(Rule_Engine.DYNAMO_CLIENT)
emr_config = {}
clusters = {}


def determine_emr_size(cores):
    """"Determining the size of EMR

    Args:
        cores (int): number of cores
    """
    cores = int(max(cores, 4))
    # cores_map_table_response = dynamodb.Table(Rule_Engine.INSTANCE_MAP_TABLE).scan(FilterExpression=Attr('max_cores').gte(cores) & Attr('min_cores').lte(cores))
    cores_map_table_response = dynamodb.Table(Rule_Engine.INSTANCE_MAP_TABLE).scan()
    print(cores_map_table_response)

    for item in cores_map_table_response[common_constants.ITEMS]:
        if int(item[create_emr_constants.MAX_CORES]) >= cores >= int(item[create_emr_constants.MIN_CORES]):
            instance_name = item[create_emr_constants.INSTANCE_NAME]
            print("Instance Name is " + instance_name)
            driver = item[create_emr_constants.DRIVER]
            max_cores = item[create_emr_constants.MAX_CORES]
            no_of_instances = item[create_emr_constants.NUMBER_OF_INSTANCE]
            executor_memory = item[create_emr_constants.EXECUTOR_MEMORY]
    emr_config[create_emr_constants.INSTANCE_NAME] = instance_name
    emr_config[create_emr_constants.DRIVER] = driver
    emr_config[common_constants.CORES] = cores
    emr_config[create_emr_constants.MAX_CORES] = max_cores
    emr_config[create_emr_constants.NUMBER_OF_INSTANCE] = no_of_instances
    emr_config[create_emr_constants.EXECUTOR_MEMORY] = executor_memory

    return emr_config


def create_emr_cluster(emr_config):
    """EMR creation  based on input

    Args:
        emr_config (Dictionary): emr configuration dictionary

    Returns:
        string: cluster id of EMR Cluster
    """
    # boto3 client creation for EMR
    client = boto3.client(Rule_Engine.EMR_CLIENT)

    # EMR creation based on emr_config dictionary
    response = client.run_job_flow(
        Name=emr_config[common_constants.BATCH_ID],
        LogUri=Rule_Engine.LOGS_URI,
        ReleaseLabel=Rule_Engine.RELEASE,
        Instances={
            'InstanceGroups': [
                {
                    'Name': Rule_Engine.MASTER_NODE,
                    'Market': Rule_Engine.MARKET,
                    'InstanceRole': Rule_Engine.MASTER_ROLE,
                    'InstanceType': str(emr_config[create_emr_constants.DRIVER]),
                    'InstanceCount': Rule_Engine.INSTANCES
                },
                {
                    'Name': Rule_Engine.CORE_NODE,
                    'Market': Rule_Engine.MARKET,
                    'InstanceRole': Rule_Engine.CORE_ROLE,
                    'InstanceType': str(emr_config[create_emr_constants.INSTANCE_NAME]),
                    'InstanceCount': int(emr_config[create_emr_constants.NUMBER_OF_INSTANCE])
                }
            ],
            'KeepJobFlowAliveWhenNoSteps': Rule_Engine.KEEP_ALIVE,
            'TerminationProtected': Rule_Engine.TERMINATE_PROTECT
        },
        Applications=[{'Name': 'Spark'}],
        BootstrapActions=[
            {
                'Name': Rule_Engine.BOOTSTRAP_NAME,
                'ScriptBootstrapAction': {
                    'Path': Rule_Engine.BOOTSTRAP_PATH
                }
            }
        ],
        Configurations=[
            {'Classification': 'spark-hive-site',
             'Properties': {
                 'hive.metastore.client.factory.class': 'com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory'}
             }
        ],
        VisibleToAllUsers=True,
        JobFlowRole=Rule_Engine.JOB_FLOW_ROLE,
        ServiceRole=Rule_Engine.SERVICE_ROLE
    )

    cluster_id = response[create_emr_constants.JOB_FLOW_ID]

    time_out = Rule_Engine.TIMEOUT
    client.put_auto_termination_policy(ClusterId=cluster_id, AutoTerminationPolicy={'IdleTimeout': time_out})

    return cluster_id, emr_config[create_emr_constants.EXECUTOR_MEMORY]


def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    try:

        execution_id = event[common_constants.EXECUTION_ID]

        # timeval=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # timestampval=str(datetime.datetime.strptime(timeval, "%Y-%m-%d %H:%M:%S").timestamp())

        # logger initiator
        # log_initiator(Rule_Engine.LOG_GROUP,execution_id+Rule_Engine.CREATE_CLUSTER+timestampval)
        # write_logs(common_constants.INFO, "Inside Create Cluster Rule Engine  Lambda")

        cores = event[common_constants.CORES]
        if cores <= 0:
            cores = 4
        emr_config_params = determine_emr_size(cores)

        table_name = Rule_Engine.TABLE_NAME
        client_name = event[common_constants.CLIENT_NAME]
        batch_id = event[common_constants.BATCH_ID]
        client_id = event[common_constants.CLIENT_ID]
        execution_id = event[common_constants.EXECUTION_ID]
        batch_name = event[common_constants.BATCH_NAME]
        time_stamp = str(datetime.datetime.now())

        sqs = boto3.resource(Rule_Engine.SQS_CLIENT, region_name=Rule_Engine.REGION)

        # Create the queue. This returns an SQS.Queue instance
        queue_name = client_name.replace(" ", "") + batch_name.replace(" ", "") + "_" + str(
            cores) + Rule_Engine.FIFO_SUFFIX_CREATE_EMR
        queue = sqs.create_queue(QueueName=queue_name,
                                 Attributes={'FifoQueue': 'true', 'ContentBasedDeduplication': 'true',
                                             'VisibilityTimeout': '5'})

        clusters[common_constants.QUEUE_NAME] = queue_name
        clusters[common_constants.JOB_QUEUE] = queue.url

        emr_config[common_constants.BATCH_ID] = batch_id
        emr_config[common_constants.CLUSTER_ID] = client_id
        emr_config[common_constants.EXECUTION_ID] = execution_id
        emr_config[common_constants.CLIENT_NAME] = client_name
        emr_config[common_constants.BATCH_NAME] = batch_name
        emr_config[common_constants.BATCH_ID] = batch_id
        # EMR cluster creation. This returns the cluster id of EMR
        emr_config[create_emr_constants.NUMBER_OF_INSTANCE] = emr_config_params[create_emr_constants.NUMBER_OF_INSTANCE]
        cluster_id, event[create_emr_constants.EXECUTOR_MEMORY] = create_emr_cluster(emr_config)

        clusters[common_constants.CLUSTER_ID] = cluster_id
        clusters[common_constants.TOTAL_CORES] = cores
        clusters[common_constants.AVAILABLE_CORES] = cores
        clusters[common_constants.STATUS] = common_constants.RUNNING

        # Updating dynamoDb table
        dynamodb.Table(table_name).put_item(Item=clusters)
        event[common_constants.CLUSTER_ID] = cluster_id

    except Exception as e:
        dynamo_resp = dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).get_item(
            Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
        job_status_dict = dynamo_resp[common_constants.ITEM]
        job_status_dict[common_constants.ERROR_DETAIL] = str(e)
        job_status_dict[common_constants.STATUS] = Rule_Engine.JOB_FAILED
        job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())

        # write_logs(common_constants.ERROR, "ERROR CAUGHT - {}".format(str(e)))

        dynamodb.Table(Rule_Engine.JOB_STATUS_TABLE).put_item(Item=job_status_dict)

        raise e

    return event
