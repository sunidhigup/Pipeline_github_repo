import json
from math import ceil
from boto3.dynamodb.conditions import Key, Attr
import boto3
from datetime import datetime
import datetime
from constants.constant import Data_processor
from constants.constant import create_emr_constants, common_constants
from  logger.helper_functions import log_initiator
from  logger.func_write_log import write_logs

client = boto3.client(Data_processor.EMR_CLIENT)
dynamodb = boto3.resource(Data_processor.DYNAMO_CLIENT)
emr_config = {}
clusters = {}

#Reading config file
with open('config/config.json', 'r') as file:
    config = json.load(file)



def determine_emr_size(cores):
    """"Determining the size of EMR 

    Args:
        cores (int): number of cores
    """    

    cores = int(max(cores, 4))
    # cores_map_table_response = dynamodb.Table(Rule_Engine.INSTANCE_MAP_TABLE).scan(FilterExpression=Attr('max_cores').gte(cores) & Attr('min_cores').lte(cores))
    cores_map_table_response = dynamodb.Table(Data_processor.INSTANCE_MAP_TABLE).scan()

    for item in cores_map_table_response[common_constants.ITEMS]:
        if int(item[create_emr_constants.MAX_CORES]) >= cores >= int(item[create_emr_constants.MIN_CORES]):
            instance_name = item[create_emr_constants.INSTANCE_NAME]
            driver = item[create_emr_constants.DRIVER]
            max_cores = item[create_emr_constants.MAX_CORES]
            no_of_instances = item[common_constants.NO_OF_INSTANCE]
            executor_memory = item[common_constants.EXECUTOR_MEMORY]
    emr_config[create_emr_constants.INSTANCE_NAME] = instance_name
    emr_config[create_emr_constants.DRIVER] = driver
    emr_config[common_constants.CORES] = cores
    emr_config[create_emr_constants.MAX_CORES] = max_cores
    emr_config[common_constants.NO_OF_INSTANCES] = no_of_instances
    emr_config[common_constants.EXECUTOR_MEMORY] = executor_memory
    
    return emr_config

def create_emr_cluster(emr_config):
    """EMR creation  based on input 

    Args:
        emr_config (Dictionary): emr configuration dictionary

    Returns:
        string: cluster id of EMR Cluster
    """    
    #boto3 client creation for EMR
    
    client = boto3.client(Data_processor.EMR_CLIENT)

    #EMR creation based on emr_config dictionary
    response = client.run_job_flow(
        Name= emr_config[common_constants.BATCH_ID],
        LogUri= Data_processor.LOGS_URI,
        ReleaseLabel= Data_processor.RELEASE,
        Instances={
            'InstanceGroups': [
                {
                    'Name': Data_processor.MASTER_NODE,
                    'Market': Data_processor.MARKET,
                    'InstanceRole': Data_processor.MASTER_ROLE,
                    'InstanceType': str(emr_config[create_emr_constants.DRIVER]),
                    'InstanceCount': Data_processor.INSTANCES
                },
                {
                    'Name': Data_processor.CORE_NODE,
                    'Market': Data_processor.MARKET,
                    'InstanceRole': Data_processor.CORE_ROLE,
                    'InstanceType': str(emr_config[create_emr_constants.INSTANCE_NAME]),
                    'InstanceCount': int(emr_config[create_emr_constants.NUMBER_OF_INSTANCES])
                }
            ],
            'KeepJobFlowAliveWhenNoSteps': Data_processor.KEEP_ALIVE,
            'TerminationProtected': Data_processor.TERMINATE_PROTECT
        },
        Applications = [ {'Name': 'Spark'} ],
        BootstrapActions = [
        {
            'Name': Data_processor.BOOTSTRAP_NAME,
            'ScriptBootstrapAction': {
                'Path': Data_processor.BOOTSTRAP_PATH
            }
        }
        ],  
        Configurations = [ 
            { 'Classification': 'spark-hive-site',
              'Properties': { 
                  'hive.metastore.client.factory.class': 'com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory'}
            }
        ],
        VisibleToAllUsers=True,
        JobFlowRole = Data_processor.JOB_FLOW_ROLE,
        ServiceRole = Data_processor.SERVICE_ROLE
    )
    
    cluster_id = response[create_emr_constants.JOB_FLOW_ID]
    
    time_out = Data_processor.TIMEOUT
    resp = client.put_auto_termination_policy(ClusterId=cluster_id, AutoTerminationPolicy= { 'IdleTimeout': time_out })
    
    return cluster_id

def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    #Checking number of cores

    try:
        log_group = Data_processor.LOG_GROUP
        log_initiator(log_group, event[common_constants.EXECUTION_ID] + "_DataProcessor_createEMR")
        write_logs(common_constants.INFO, "Inside Create EMR Lambda")
        cores = event[common_constants.CORES]

        if cores <=0:
            cores=4
        
        #Determining EMR Cluster size
        emr_config_params = determine_emr_size(cores)

        table_name = Data_processor.TABLE_NAME
        client_name = event[common_constants.CLIENT_NAME]
        batch_id = event[common_constants.BATCH_ID]
        client_id = event[common_constants.CLIENT_ID]
        execution_id = event[common_constants.EXECUTION_ID]
        batch_name = event[common_constants.BATCH_NAME]
        time_stamp = str(datetime.datetime.now())
        sqs = boto3.resource(Data_processor.SQS_CLIENT, region_name=config[common_constants.REIGON_NAME])

        # Create the queue. This returns an SQS.Queue instance
        queue_name = client_name.replace(" ","") + batch_name.replace(" ","") + "_" + str(cores) + Data_processor.FIFO_SUFFIX_CREATE_EMR
        queue = sqs.create_queue(QueueName= queue_name, Attributes={'FifoQueue': Data_processor.FIFO, 'ContentBasedDeduplication':Data_processor.DUPLICATION,'VisibilityTimeout':Data_processor.VISIBLE_TIMEOUT})
        
        clusters[common_constants.QUEUE_NAME] = queue_name
        clusters[create_emr_constants.QUEUE_JOB] = queue.url

        emr_config[common_constants.BATCH_ID] = batch_id
        emr_config[common_constants.CLIENT_ID] = client_id
        emr_config[common_constants.EXECUTION_ID] = execution_id
        emr_config[common_constants.CLIENT_NAME] = client_name
        emr_config[common_constants.BATCH_NAME] = batch_name
        emr_config[create_emr_constants.NUMBER_OF_INSTANCES] = emr_config_params[create_emr_constants.NUMBER_OF_INSTANCES]
        #EMR cluster creation. This returns the cluster id of EMR
        cluster_id,event[common_constants.EXECUTOR_MEMORY] = create_emr_cluster(emr_config)

        clusters[common_constants.CLUSTER_ID]=cluster_id
        clusters[common_constants.TOTAL_CORES]=cores
        clusters[common_constants.AVAILABLE_CORES]= cores
        clusters[common_constants.STATUS]= common_constants.RUNNING

        #Updating dynamoDb table
        dynamodb.Table(table_name).put_item(Item=clusters)
        event[common_constants.CLUSTER_ID]= cluster_id
    
    except Exception as e:
        dynamo_resp = dynamodb.Table(Data_processor.JOB_STATUS_TABLE).get_item(Key={common_constants.EXECUTION_ID: event[common_constants.EXECUTION_ID]})
        job_status_dict = dynamo_resp[common_constants.ITEM]
        job_status_dict[common_constants.ERROR_DETAIL] = str(e)
        job_status_dict[common_constants.STATUS] = Data_processor.JOB_FAILED
        job_status_dict[common_constants.END_TIME] = str(datetime.datetime.now())
        
        write_logs("ERROR", "ERROR CAUGHT - {}".format(str(e)))

        dynamodb.Table(Data_processor.JOB_STATUS_TABLE).put_item(Item=job_status_dict)

        
        raise e

    return event
