import traceback

import boto3
from Rule_Engine.logging.cloudwatch.log_utils import write_logs
from Rule_Engine.rule_engine_jobs.utils.rule_helper import remove_linebreak, \
     remove_columnshift, add_column, drop_column, swap_df_columns
from Rule_Engine.rule_shared_jobs.src.shared.constant.constants import JsonParams
from pyspark import StorageLevel

# Making boto3 resource for dynamoDb
dynamodb = boto3.resource('dynamodb')
import boto3
from Rule_Engine.rule_engine_jobs.constants.rule_engine_constants import JsonParamKeys,columnconstant
from Rule_Engine.rule_engine_jobs.utils.rule_helper import skip_blanklines, skip_headers, date_numeric_validation, \
    add_review_column, filter_record_after_numeric, single_to_multicolumn, read_input_file,clean_controlchar
from pyspark.sql import SparkSession
from pyspark.sql.types import BooleanType, StringType, StructType, StructField

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def read_dataframe(df, source_file_path, jar_folder_path,spark=None):
    """
    Read dataframe from given path

    :param df: dataframe
    :param source_file_path: path of file
    :param jar_folder_path: path of jar
    :return: dataframe
    """
    # Creating Spark session
    if spark is None:
        spark = SparkSession.builder \
            .config("spark.driver.extraClassPath", jar_folder_path) \
            .getOrCreate()
    
    validate_date_schema = StructType([
        StructField(JsonParamKeys.OUTPUT_VAL, StringType(), True),
        StructField(JsonParamKeys.INPUT_VAL, StringType(), True),
        StructField(JsonParamKeys.IS_DEFAULT, BooleanType(), True),
        StructField(JsonParamKeys.IS_ERROR, BooleanType(), True),
        StructField(JsonParamKeys.ERROR_MESSAGE, StringType(), True)
    ])

    spark.udf.registerJavaFunction("generic_udf", "udf.generic_udf", validate_date_schema)
    spark.udf.registerJavaFunction("generic_udf_date", "udf.generic_udf_date", validate_date_schema)
    

    if df is None:
        df = read_input_file(source_file_path, spark)
        
    return df


def row_level_validation(data_frame, rule_items, parameters):
    """
    Enforce row level validation on dataframe

    :param data_frame: input df
    :param rule_items: validations to be applied
    :param parameters: parameters
    :return: output dataframe
     """

    if rule_items.get(JsonParams.SKIPHEADERS, False):
        data_frame = skip_headers(data_frame, rule_items)
    if rule_items.get(JsonParams.IGNOREBLANKLINES, False):
        data_frame = skip_blanklines(data_frame)
    if rule_items.get(JsonParams.CONTROLCHAR, False):
        data_frame = clean_controlchar(data_frame, rule_items)
    if rule_items.get(JsonParams.LINEBREAK, False):
        data_frame = remove_linebreak(data_frame, rule_items)
    if rule_items.get(JsonParams.COLUMNSHIFT, False):
        data_frame, row_invalid_df = remove_columnshift(data_frame, rule_items, parameters)
        row_invalid_df.persist(StorageLevel.MEMORY_AND_DISK)
        write_logs("Info", "After  Row level validation Invalid dataframe  count:" + str(row_invalid_df.count()))

    data_frame = single_to_multicolumn(data_frame, rule_items, parameters)
    data_frame.persist(StorageLevel.MEMORY_AND_DISK)

    #write_logs("Info", "After  Row level validation valid dataframe  count:" + str(data_frame.count()))

    return data_frame, row_invalid_df


def column_level_validation(data_frame, rule_items):
    """
    Enforce column level validations
    :param data_frame: input df
    :param rule_items: actions to be performed on columns
    :return: output df
    """

    try:
        # Performing date and numeric validation on dataframe
        data_frame = date_numeric_validation(data_frame, rule_items)

        # add new column in dataframe
        if columnconstant.COLUMN_ADD in rule_items and len(rule_items[columnconstant.COLUMN_ADD]) > 0:
            write_logs("Info", "going to add new columns in dataframe")
            write_logs("Info", "Before adding record count:" + str(data_frame.count()))
            col_dict_list = rule_items[columnconstant.COLUMN_ADD]
            # sort the index to be added in dataframe
            sorted_dict = sorted(col_dict_list, key=lambda x: x[columnconstant.POSITION])
            data_frame = add_column(data_frame, sorted_dict)
            # write_logs("Info","Columns added successfully")
            data_frame.unpersist()
            data_frame.persist(StorageLevel.MEMORY_AND_DISK)
            write_logs("Info", "After adding record count:" + str(data_frame.count()))

            # swap dataframe columns
        if columnconstant.SWAP_FIELD in rule_items and len(rule_items[columnconstant.SWAP_FIELD]) > 0:
            write_logs("Info", "going to swap columns in dataframe")
            write_logs("Info", "Before swap record count:" + str(data_frame.count()))
            swap_col_var = rule_items[columnconstant.SWAP_FIELD]
            swap_col_dict = {}
            for x in swap_col_var:
                swap_col_dict.__setitem__(x.get(columnconstant.SWAP_COL_ONE), x.get(columnconstant.SWAP_COL_TWO))
            data_frame = swap_df_columns(data_frame, swap_col_dict)
            data_frame.unpersist()
            data_frame.persist(StorageLevel.MEMORY_AND_DISK)
            write_logs("Info", "After swap record count:" + str(data_frame.count()))

        # drop column from dataframe
        if columnconstant.DEL_COL_SEQ in rule_items and len(rule_items[columnconstant.DEL_COL_SEQ]) > 0:
            data_frame.persist(StorageLevel.MEMORY_AND_DISK)
            del_col_arr = rule_items[columnconstant.DEL_COL_SEQ]
            write_logs("Info", "Before drop record count:" + str(data_frame.count()))
            data_frame = drop_column(data_frame, del_col_arr)
            data_frame.unpersist()
            data_frame.persist(StorageLevel.MEMORY_AND_DISK)
            write_logs("Info", "After drop record count:" + str(data_frame.count()))

        # Adding review column and flag column to dataframe
        data_frame = add_review_column(data_frame)

        # Filtering valid and invalid record
        valid_df, invalid_df = filter_record_after_numeric(data_frame)
        write_logs("Info", f"[*****After  Column level validation Invalid dataframe  count: {invalid_df.count()}")
        write_logs("Info", f"[*****After  Column level validation valid dataframe  count: {valid_df.count()}")
        

        return valid_df, invalid_df
    except Exception as e:
        write_logs("ERROR", "Error occured " + str(traceback.print_exc()))
        traceback.print_exc()
        raise e
