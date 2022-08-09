import datetime

from Rule_Engine.Constant.constant import Rule_Engine_Common_Constants
from Rule_Engine.env_fetcher import read_config
from Rule_Engine.logging.cloudwatch.log_utils import write_logs
from Rule_Engine.rule_engine_jobs.constants.rule_engine_constants import DataframeConstant, \
    CharacterConstants
from Rule_Engine.rule_engine_jobs.constants.rule_engine_constants import DynamoDbStatus, JsonParamKeys
from Rule_Engine.rule_engine_jobs.constants.rule_engine_constants import profile_env_keys
from Rule_Engine.rule_engine_jobs.constants.rule_engine_constants import rule_engine_processor_constants
from Rule_Engine.rule_engine_jobs.rule_engine_udfs import column_level_validation, row_level_validation, read_dataframe
from Rule_Engine.rule_engine_jobs.utils.rule_helper import \
    get_files_in_s3
from Rule_Engine.rule_engine_jobs.utils.rule_helper import rule_json, \
    write_to_dynamodb, s3_save, audit_table_initiator, log_initiator, job_status_initiator, \
    s3_copy_and_delete, s3_file_size
from Rule_Engine.setting import Settings


class RuleEngineProcessor:
    """
        RuleEngineProcessor class will be use for validating input files based on datatype rules
    """

    @staticmethod
    def process(parameters, dataframe=None):
        """
        parameter: It contains the all the input parameters
        job_status_dict: It contains the dynamodb status table dictionary
        """
        log_initiator(parameters)
        write_logs("Info", "Inside process method rule engine")
        batch_name = parameters.get(Rule_Engine_Common_Constants.BATCH_NAME, '')
        client_name = parameters.get(Rule_Engine_Common_Constants.CLIENT_NAME, '')
        table_name = parameters.get(Rule_Engine_Common_Constants.TABLE_NAME, '')
        bucket = parameters.get(Rule_Engine_Common_Constants.BUCKET_NAME, '')
        jar_folder_path = parameters.get(rule_engine_processor_constants.JAR_FOLDER_PATH, '')
        job_status_table = parameters.get(rule_engine_processor_constants.DB_STATUS_TABLE, '')
        audit_table = parameters.get(Rule_Engine_Common_Constants.DB_AUDIT_TABLE, '')
        region_name = parameters.get(Rule_Engine_Common_Constants.REGION_NAME, '')
        extensions = parameters.get(rule_engine_processor_constants.FILE_EXTENSION, '')
        profile_env = parameters.get(Rule_Engine_Common_Constants.PROFILE_ENV, '')
        profile_env_bucket = parameters.get(Rule_Engine_Common_Constants.PROFILE_ENV_BUCKET, '')
        temp_view = parameters.get(Rule_Engine_Common_Constants.ALIAS,'')
        isRuleEngine = parameters.get(Rule_Engine_Common_Constants.CHECKFLAG,"")

       

        # Reading config from S3
        config = read_config(PROFILE_ENV=profile_env, BUCKETNAME=profile_env_bucket,
                             KEYNAME=profile_env_keys.KEYNAME)
        write_logs("Info", "Read values from parameters")

        # Audit Entry
        row_count = 0
        source_count = 0
        valid_count = 0
        invalid_count = 0
        job_status_dict = {}
        job_end_time = ""
        # Writing log to cloudwatch
        try:

            write_logs("Info", "Inside try of rule_engine_processor")
            # It fetches all the input files for processing.

            # Initiating and writing status to dynamodb
            write_logs("Info", "Initiating and writing status to dynamodb")
            job_status_dict = job_status_initiator(parameters)
            write_logs("Info", "job_status_dict created")
            audit_status_dict = audit_table_initiator(parameters, job_status_dict)
            write_logs("Info", "audit_status_dict created")

            # Updating job status in dynamodb job status table
            job_status_dict[Rule_Engine_Common_Constants.STATUS] = DynamoDbStatus.IN_PROGRESS
            write_to_dynamodb(job_status_table, region_name, job_status_dict)
            write_logs("Info", "Write to dynamo successful")
            if isRuleEngine:
                rule_items = parameters.get("ruleFile")
            else:
                rule_items = rule_json(parameters, config)
            write_logs("Info", "rule_items created")
            creation_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # check if s3 path is provided from table rule
            if "s3_path" in rule_items and len(rule_items["s3_path"]) > 0:
                source_file_path = rule_items["s3_path"]
            else:
                write_logs("Info", "S3 path is not present")
                source_file_path = JsonParamKeys.S3_EXT + bucket + CharacterConstants.SLASH + client_name + CharacterConstants.SLASH + batch_name + \
                                   CharacterConstants.SLASH + table_name + CharacterConstants.SLASH+config.get("S3_DETAILS").get("RULE_ENGINE") + \
                                   config.get("S3_DETAILS").get("input_folder_prefix")

                write_logs("Info", "Source file path without S3 input is " + str(source_file_path))
                data_file_path = client_name + CharacterConstants.SLASH + batch_name + CharacterConstants.SLASH + \
                                 table_name +CharacterConstants.SLASH+config.get("S3_DETAILS").get("RULE_ENGINE") + \
                                 config.get("S3_DETAILS").get("input_folder_prefix")
                csv_file_name = get_files_in_s3(bucket, data_file_path)
                write_logs("Info","csv file_name is "+csv_file_name)

                source_file_path = source_file_path + csv_file_name

            valid_output_file_path = JsonParamKeys.S3_EXT + bucket + CharacterConstants.SLASH + client_name + CharacterConstants.SLASH + batch_name + \
                                     CharacterConstants.SLASH + table_name + \
                                     config.get("S3_DETAILS").get("RULE_ENGINE") + \
                                     Settings.S3_DETAILS["output_valid_path"] + creation_time
            invalid_output_file_path = JsonParamKeys.S3_EXT + bucket + CharacterConstants.SLASH + client_name + CharacterConstants.SLASH + batch_name + \
                                       CharacterConstants.SLASH + table_name + \
                                       config.get("S3_DETAILS").get("RULE_ENGINE") + \
                                       Settings.S3_DETAILS["output_invalid_path"] + creation_time
            input_folder_path = client_name + CharacterConstants.SLASH + batch_name + CharacterConstants.SLASH + \
                                table_name + \
                                config.get("S3_DETAILS").get("RULE_ENGINE") + \
                                config.get("S3_DETAILS").get("input_folder_prefix")
            copy_folder_path = client_name + CharacterConstants.SLASH + batch_name + CharacterConstants.SLASH + table_name + \
                               config.get("S3_DETAILS").get("RULE_ENGINE") + Settings.S3_DETAILS[
                                   "processed_folder_prefix"] + \
                               creation_time + CharacterConstants.SLASH

            # Creating dataframe for validation
            write_logs("Info", f"[******* Starting Executing for {source_file_path} *********]")
            data_frame = read_dataframe(dataframe, source_file_path, jar_folder_path)
            # get the prefix for fetching file size of source file
            file_arr = source_file_path.replace("//", "/").split("/")
            prefix = ""
            for x in range(file_arr.index(bucket) + 1, len(file_arr)):
                prefix += file_arr[x] + "/"
            prefix = prefix.strip("/")
            file_size = s3_file_size(bucket, prefix)
            write_logs("Info", f"s3 file size is in bytes {str(file_size)}")

            # increase or decrease the parttion based on file size
            df_partition = data_frame.rdd.getNumPartitions()
            if (file_size / DataframeConstant.BLOCK_SIZE < df_partition):
                data_frame = data_frame.coalesce(int(file_size / DataframeConstant.BLOCK_SIZE) + 1)
                write_logs("Info", "dataframe partition set to" + str(data_frame.rdd.getNumPartitions()))
            if (file_size / DataframeConstant.BLOCK_SIZE > df_partition):
                write_logs("Info", "going to increase partiton")
                data_frame = data_frame.repartition(int(file_size / DataframeConstant.BLOCK_SIZE) + 1)
                write_logs("Info", "dataframe partition set to" + str(data_frame.rdd.getNumPartitions()))

            source_count += data_frame.count()

            write_logs(Rule_Engine_Common_Constants.INFO, rule_engine_processor_constants.INFO_ROW_LEVEL)
            if dataframe is None:
                data_frame, row_invalid_df = row_level_validation(data_frame, rule_items, parameters)
            write_logs(Rule_Engine_Common_Constants.INFO, rule_engine_processor_constants.INFO_COL_LEVEL)
            valid_df, col_invalid_df = column_level_validation(data_frame, rule_items)

            
            # Saving file to S3 folder
            if isRuleEngine:
                valid_df.createOrReplaceTempView(temp_view)
            else:
                s3_save(valid_df, valid_output_file_path)
                s3_save(col_invalid_df, invalid_output_file_path)
                # Moving input file to processed folder
                s3_copy_and_delete(bucket, input_folder_path, copy_folder_path, extensions)

            # Updating job status to dynamodb table

            write_logs(Rule_Engine_Common_Constants.INFO, rule_engine_processor_constants.INFO_DYNAMO_UPDATE)

            write_logs(Rule_Engine_Common_Constants.INFO, rule_engine_processor_constants.INFO_DYNAMO_UPDATE)

            job_end_time = str(datetime.datetime.now())
            job_status_dict[Rule_Engine_Common_Constants.END_TIME] = job_end_time
            job_status_dict[rule_engine_processor_constants.BATCH_NAME] = batch_name
            job_status_dict[Rule_Engine_Common_Constants.STATUS] = DynamoDbStatus.COMPLETED
            write_to_dynamodb(job_status_table, region_name, job_status_dict)

            # Updating job status to audit table
            audit_status_dict[Rule_Engine_Common_Constants.COUNT_SOURCE_LEVEL] = source_count
            audit_status_dict[Rule_Engine_Common_Constants.COUNT_ROW_LEVEL] = row_count
            audit_status_dict[Rule_Engine_Common_Constants.COUNT_VALID] = valid_count
            audit_status_dict[Rule_Engine_Common_Constants.COUNT_SOURCE_LEVEL] = invalid_count
            audit_status_dict[Rule_Engine_Common_Constants.END_TIME] = str(datetime.datetime.now())
            audit_status_dict[Rule_Engine_Common_Constants.STATUS] = DynamoDbStatus.COMPLETED
            write_to_dynamodb(audit_table, region_name, audit_status_dict)
            write_logs(rule_engine_processor_constants.INFO, rule_engine_processor_constants.INFO_PROCESS_CMPLT)



        except Exception as e:

            job_status_dict[Rule_Engine_Common_Constants.END_TIME] = job_end_time
            write_logs(Rule_Engine_Common_Constants.ERROR, str(e))
            job_status_dict[rule_engine_processor_constants.ERROR_DETAIL] = str(e)
            job_status_dict[rule_engine_processor_constants.BATCH_NAME] = batch_name
            job_status_dict[Rule_Engine_Common_Constants.END_TIME] = str(datetime.datetime.now())
            job_status_dict[Rule_Engine_Common_Constants.STATUS] = rule_engine_processor_constants.STATUS_FAILED
            write_logs(Rule_Engine_Common_Constants.ERROR, rule_engine_processor_constants.INFO_ERROR)
            write_to_dynamodb(job_status_table, region_name, job_status_dict)
            raise e
