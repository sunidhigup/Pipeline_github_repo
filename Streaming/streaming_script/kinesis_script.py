import datetime
import json
import time
from pyspark.sql.functions import *
from pyspark.sql.types import StructType,StructField, StringType, IntegerType, TimestampType, LongType
from pyspark.sql.session import SparkSession
from DynamoDb_connector.settings import Settings
from DynamoDb_connector.dml.write import write_to_meta
from DynamoDb_connector.dml.read import read_from_meta
from DynamoDb_connector.dml.read import get_stream_name
from DynamoDb_connector.Constant.Dynamo_constant import META_DICT
from DynamoDb_connector.Constant.Dynamo_constant import STATUS_DICT
from logger.cloudwatch.run import write_logs
from streaming_script.query_operations import write_to_s3,write_to_console,stop_stream_query
from streaming_script.schema import DataStruct
from streaming_script.rule_engine_sf import call_resource_management_sf
from streaming_script.analytics_stepfunction import call_analytics_sf
from logger.log_formatter import LogFormatter
from logger.logger import LogObject,LogTypeEnum,get_logger
from Constant.constant import kinesis_script_constant
from Streaming.env_fetcher import read_config

config = read_config("dev","depconfig","Streaming/Config/config.json")

AWS_CREDENTIALS = Settings.AWS_CREDENTIALS
Kinesis = Settings.KINESIS
Dynamo_Table = Settings.DYNAMO
time_stamp = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
stream_name = get_stream_name()
client_name= config["client_name"]
log_stream = client_name+ time_stamp
analytics_path =  config["analytics_path"]



def stream(spark,logger):
    """

    :param spark:
    :param logger:
    :return:
    """
    write_logs(kinesis_script_constant.INFO_INGESTION,kinesis_script_constant.INFO,log_stream)
    logger.info(LogObject(LogTypeEnum.STEP_SUCCESS.value,
                                         kinesis_script_constant.INFO_STREAMING_INITIATED).get_log_string())

    # Create status and meta data df
    stream_status_dict = STATUS_DICT.DICT
    stream_metadata_dict = META_DICT.DICT

    # Store dictionary in dynamo
    write_to_meta(Dynamo_Table["stream_meta_data"], stream_metadata_dict)
    write_to_meta(Dynamo_Table["stream_status"], stream_status_dict)
    logger.info(LogObject(LogTypeEnum.STEP_SUCCESS.value,
                                         kinesis_script_constant.INFO_WRITE_DYNAMODB).get_log_string())
    write_logs(kinesis_script_constant.INFO_WRITE_STATUS,kinesis_script_constant.INFO,log_stream)

    # Read from dynamo table
    meta_data = read_from_meta(Dynamo_Table["stream_meta_data"], stream_name)
    logger.info(LogObject(LogTypeEnum.STEP_SUCCESS.value,
                                         kinesis_script_constant.INFO_METADATA).get_log_string())
    write_logs(kinesis_script_constant.INFO_METADATA_READ ,kinesis_script_constant.INFO,log_stream)
    # Retrive status
    isanalytics = meta_data["Item"]["isanalytics"]
    isstorage = meta_data["Item"]["isstorage"]
    isprocessing = meta_data["Item"]["isprocessing"]


    # Read stream from Kinesis Data stream
    try:
        streamingData = spark.readStream.format(AWS_CREDENTIALS['format'])\
            .option('streamName', stream_name)\
            .option('endpointUrl', AWS_CREDENTIALS['endpointUrl'])\
            .option('region', AWS_CREDENTIALS['region'])\
            .option('awsAccessKey', AWS_CREDENTIALS['awsAccessKey'])\
            .option('awsSecretKey', AWS_CREDENTIALS['awsSecretKey'])\
            .option('startingposition', AWS_CREDENTIALS['startingposition'])\
            .load()
        logger.info(LogObject(LogTypeEnum.STEP_SUCCESS.value,
                                         kinesis_script_constant.INFO_DF ).get_log_string())
        write_logs(kinesis_script_constant.INFO_INGESTION ,kinesis_script_constant.INFO,log_stream)
    except Exception as e:
        error = LogFormatter(stream_name, client_name,
                                kinesis_script_constant.INFO_ERROR , source_rec_count='',
                                target_record_count='', reject_record_count='')
        logger.error(
                LogObject(LogTypeEnum.STEP_ERROR.value, error.create_log()).get_log_string())
        write_logs(kinesis_script_constant.INFO_STREAM_NOT_READ ,kinesis_script_constant.ERROR ,log_stream)
        stream_metadata_dict["status"] = kinesis_script_constant.STATUS_FAILED 
        write_to_meta(Dynamo_Table["stream_status"], stream_metadata_dict)
        write_logs(kinesis_script_constant.STATUS_STOPPED ,kinesis_script_constant.ERROR ,log_stream)


    source_schema = DataStruct()
    logger.info(LogObject(LogTypeEnum.STEP_SUCCESS.value,
                                         kinesis_script_constant.INFO_DYNAMIC_scheam ).get_log_string())
    write_logs(kinesis_script_constant.INFO_SCHEMA_CREATED,kinesis_script_constant.INFO,log_stream)

    streamData = streamingData.selectExpr("cast (data as STRING) jsonData")\
                                .select(from_json("jsonData", source_schema).alias("json_data"))\
                                .select("json_data.*")
                                 
    
    s3_path= config["s3_ext"] + Kinesis["bucket"]+"/" + config["input_prefix"]+ client_name+"/"+stream_name + "/"
    s3_checkpoint = config["s3_ext"] + Kinesis["bucket"]+"/" +config["checkpoint_prefix"] + time_stamp+"/"


    if isstorage==kinesis_script_constant.YES :
        query = (streamData.writeStream
                .format("csv")
                .outputMode("append")
                .option("path", s3_path)
                .option("checkpointLocation", s3_checkpoint)
                .start())
    else:
        query = write_to_console(streamData)
    logger.info(LogObject(LogTypeEnum.STEP_SUCCESS.value,
                                         kinesis_script_constant.INFO_DUMPING_DATA_PROGRESS ).get_log_string())
    write_logs(kinesis_script_constant.INFO_DUMPING_DATA ,kinesis_script_constant.INFO,log_stream)
    
    
    
    count=config["count"]
    while query.isActive:
        
        try:
            
            if query.lastProgress['numInputRows']==0:
                count=count+1
            else:
                count=config["count"]

        except:
            pass
        
        if count>config["stopping_criteria"]:
            logger.info(LogObject(LogTypeEnum.APP_DEBUG.value,
                                         kinesis_script_constant.INFO_STOPPING_QUERY ).get_log_string())
                   
            logger.info(LogObject(LogTypeEnum.APP_DEBUG.value,
                                         kinesis_script_constant.INFO_TERMINATION ).get_log_string())
            query.stop()
            break
       
        time.sleep(config["sleep_time"])
    stream_metadata_dict["status"] = kinesis_script_constant.STATUS_COMPLETED 
    write_to_meta(Dynamo_Table["stream_status"], stream_metadata_dict)
    logger.info(LogObject(LogTypeEnum.STEP_SUCCESS.value,
                                         kinesis_script_constant.INFO_STRAMING_COMPLETED ).get_log_string())
    write_logs(kinesis_script_constant.INFO_STREAM_COMPLETE ,kinesis_script_constant.INFO,log_stream)


    # Write csv file for dashboarding
    df = spark.read.option("header",True).schema(source_schema).csv(s3_path)
    df = df.withColumn("id", monotonically_increasing_id())
    df.coalesce(config["coalesce"]).write.option("header",True).csv(config["s3_ext"] + Kinesis["bucket"]+"/" + analytics_path+"/"+ time_stamp)
    return isprocessing,isanalytics



if __name__ == "__main__":

     # Create spark session
    app_name = stream_name + "_" + time_stamp
    rule_engine = True
    spark = SparkSession \
        .builder \
        .appName(app_name) \
        .getOrCreate()


 
    logger = get_logger(spark)
    
    isprocessing,isanalytics= stream(spark,logger)

    
    if isprocessing==kinesis_script_constant.YES:    #Process the data by calling rule engine
        logger.info(LogObject(LogTypeEnum.STEP_SUCCESS.value,
                                         kinesis_script_constant.INFO_STARTING_RULEENGINE ).get_log_string())
        write_logs(kinesis_script_constant.INFO_RULEENGINE_STARTED ,kinesis_script_constant.INFO,log_stream)
    

        call_resource_management_sf(rule_engine)
        logger.info(LogObject(LogTypeEnum.STEP_SUCCESS.value,
                                         kinesis_script_constant.INFO_STARTED_RE_STEPFUNCTION ).get_log_string())
    
    
    else:
        rule_engine = False
        call_resource_management_sf(rule_engine)


    if isanalytics==kinesis_script_constant.YES:
    
        segment = input(kinesis_script_constant.INPUT )
        bucket = Kinesis[kinesis_script_constant.BUCKET ]
        key = analytics_path +"/" +time_stamp
        call_analytics_sf(segment,bucket,key)

        