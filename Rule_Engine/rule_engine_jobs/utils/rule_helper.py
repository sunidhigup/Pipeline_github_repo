import datetime
import json
import os
import sys
import traceback
import unicodedata

import Rule_Engine.logging.cloudwatch.write_logs as write_logger
import boto3
import pyspark.sql.functions as f
from Rule_Engine.Constant.constant import Rule_Engine_Common_Constants
from Rule_Engine.logging.cloudwatch.log_utils import write_logs
from Rule_Engine.logging.cloudwatch.write_logs import create_log_stream
from Rule_Engine.rule_engine_jobs.constants.rule_engine_constants import JsonParamKeys, NumericValidationParams, \
    CharacterConstants, Additional_Columns, Mssql_types, CommonFlags, DynamoDbStatus, RuleFileName, columnconstant
from Rule_Engine.rule_engine_jobs.constants.rule_engine_constants import rule_helper_constants
from Rule_Engine.rule_engine_jobs.validation_jobs.date_validation import DateValidation
from Rule_Engine.rule_engine_jobs.validation_jobs.numeric_validation import NumericValidation
from Rule_Engine.setting import Settings
from boto3.dynamodb.conditions import Attr
from pyspark.sql import Window
from pyspark.sql import functions as F
from pyspark.sql.functions import col
from pyspark.sql.functions import expr, when
from pyspark.sql.types import StructType, StringType, BooleanType, StructField
from data_processor.logging.cloudwatch.log_utils import write_logs

def audit_table_initiator(parameters, job_status_dict):
    """
    Prepare dictionary for audit table

    :param parameters: arguments
    :param job_status_dict: intial dictionary
    :return: output dictionary
    """
    audit_table = parameters[Rule_Engine_Common_Constants.DB_AUDIT_TABLE]
    region_name = parameters[rule_helper_constants.REGION_NAME]
    audit_status_dict = {rule_helper_constants.ID: job_status_dict[rule_helper_constants.EXECUTION_ID],
                         Rule_Engine_Common_Constants.COUNT_SOURCE_LEVEL: 0,
                         Rule_Engine_Common_Constants.COUNT_ROW_LEVEL: 0,
                         Rule_Engine_Common_Constants.COUNT_VALID: 0, Rule_Engine_Common_Constants.COUNT_INVALID: 0,
                         rule_helper_constants.START_TIME: str(datetime.datetime.now()),
                         Rule_Engine_Common_Constants.END_TIME: "",
                         Rule_Engine_Common_Constants.STATUS: DynamoDbStatus.IN_PROGRESS}
    # Writing to dynamoDb table
    write_to_dynamodb(audit_table, region_name, audit_status_dict)

    return audit_status_dict


def job_status_initiator(parameters):
    """

    :param parameters:
    :return:
    """
    client_name = parameters[rule_helper_constants.CLIENT_NAME]
    execution_id = parameters[rule_helper_constants.EXECUTION_ID]
    table_name = parameters[rule_helper_constants.TABLE_NAME]
    job_status_table = parameters[Rule_Engine_Common_Constants.DB_STATUS_TABLE]
    
    region_name = parameters[rule_helper_constants.REGION_NAME]
    job_status_dict = {rule_helper_constants.CLIENT_NAME: client_name, rule_helper_constants.TABLE_NAME: table_name,
                       rule_helper_constants.EXECUTION_ID: execution_id, Rule_Engine_Common_Constants.STATUS: DynamoDbStatus.STARTED,
                       rule_helper_constants.START_TIME: str(datetime.datetime.now()),
                       Rule_Engine_Common_Constants.END_TIME: "", rule_helper_constants.ERROR_DETAIL: ""}
    # Writing status to dynamoDb table
    write_to_dynamodb(job_status_table, region_name, job_status_dict)

    return job_status_dict


def log_initiator(parameters):
    """
        This function initiate the logger group
        :parameter : input parameters
        :return
    """
    log_group = parameters[rule_helper_constants.LOG_GROUP]
    execution_id = parameters[rule_helper_constants.EXECUTION_ID]
    timeval = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    timestampval = str(datetime.datetime.strptime(timeval, "%Y-%m-%d %H:%M:%S").timestamp())

    write_logger.log_group = log_group
    write_logger.log_stream_name = execution_id + timestampval

    create_log_stream()
    write_logs(Rule_Engine_Common_Constants.INFO, rule_helper_constants.INFO_RE_STARTED)
    return None


def s3_save(df, path):
    """
        It saves the dataframe to specified location.
    """
    df.write.option("header", True).format('csv').mode("overwrite").save(path)

    return None


def s3_copy_and_delete(bucket, input_folder_path, copy_folder_path, extensions):
    """
        This function list down all the input file from specific input folder
        bucket: Bucket name
        input_folder_path : It contains the input folder prefix path
        :return All the file name from specified folder
    """

    client = boto3.resource("s3")

    my_bucket = client.Bucket(bucket)

    # fetching file list from s3 location
    s3_file_list = []
    file_list = []
    for object_summary in my_bucket.objects.filter(Prefix=input_folder_path):
        s3_file_list.append(object_summary.key)
    # It will filter out the specified extension file only from s3_file_list
    for file_name in s3_file_list:
        if file_name.endswith(tuple(extensions)):
            file_list.append("s3://" + bucket + "/" + file_name)

    # Moving file from one location to other
    for file in file_list:
        input_file_path = file.split(bucket + '/')[1]
        file_name = os.path.split(input_file_path)[1]
        final_output_folder_path = copy_folder_path + file_name

        copy_source = {'Bucket': bucket, 'Key': input_file_path}
        destination_bucket = client.Bucket(bucket)
        destination_bucket.copy(copy_source, final_output_folder_path)
        # To Delete the File After Copying It to the Target Directory
        # my_bucket.objects.filter(Prefix=input_folder_path).delete()
        # client.Object(bucket, input_file_path).delete()
    return None


def write_to_dynamodb(db_table_name, region_name, status_dict):
    """Write to Dynamodb
    Args:
        :param status_dict:
        :param region_name:
        :param db_table_name:
    """
    # Creating resource for dynamoDb
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    # Putting items in table
    dynamodb.Table(db_table_name).put_item(Item=status_dict)
    return None


def argument_parser():
    """

    :return:
    """
    input_args = sys.argv
    arg_dict = {rule_helper_constants.CLIENT_NAME: input_args[1], rule_helper_constants.TABLE_NAME: input_args[2],
                "batch_name": input_args[3], rule_helper_constants.BATCH_ID: input_args[4],
                "execution_id": input_args[5],
                rule_helper_constants.REGION_NAME: "us-east-1", rule_helper_constants.PROFILE_ENV: input_args[6],
                rule_helper_constants.PROFILE_ENV_BUCKET: input_args[7]}

    return arg_dict


def get_job_details(arg_dict):
    """
    The function will scan the dynamodb table on specified condition
    :table_name: attribute column value used in filter
    :client_name: attribute column value used in filter
    """
    # arg_dict = read_msg()
    batch_id = arg_dict[rule_helper_constants.BATCH_ID]
    client_name = arg_dict[Rule_Engine_Common_Constants.CLIENT_NAME]
    table_name = arg_dict[Rule_Engine_Common_Constants.TABLE_NAME]
    region_name = arg_dict[Rule_Engine_Common_Constants.REGION_NAME]
    profile_env = arg_dict[Rule_Engine_Common_Constants.PROFILE_ENV]
    profile_env_bucket = arg_dict[Rule_Engine_Common_Constants.PROFILE_ENV_BUCKET]
    batch_name = arg_dict[Rule_Engine_Common_Constants.BATCH_NAME]
    execution_id = arg_dict[Rule_Engine_Common_Constants.EXECUTION_ID]

    filter_value = client_name + "_" + batch_name + "_" + table_name

    resource = boto3.resource("dynamodb", region_name=region_name)
    tableName = DynamoDbStatus.DB_METADATA_TABLE
    dynamoTable = resource.Table(tableName)
    resultJson = dynamoTable.scan(FilterExpression=Attr('id').eq(filter_value))
    result = resultJson[rule_helper_constants.ITEMS]
    # Filtering only "params" column data from result dictionary
    rule_engine_param = result[0][rule_helper_constants.PARAMS]
    parameters = json.loads(rule_engine_param)
    parameters[rule_helper_constants.BATCH_ID] = batch_id
    parameters[Rule_Engine_Common_Constants.PROFILE_ENV] = profile_env
    parameters[Rule_Engine_Common_Constants.BATCH_NAME] = batch_name
    parameters[Rule_Engine_Common_Constants.EXECUTION_ID] = execution_id
    parameters[Rule_Engine_Common_Constants.CLIENT_NAME] = client_name
    parameters[Rule_Engine_Common_Constants.PROFILE_ENV_BUCKET] = profile_env_bucket

    return parameters


def rule_json(parameters, config):
    """
        It merges the client, global, table rule file and return single rule json file
        rule_list : It has all the rule input file
        :return It will return single rule json file
    """

    batch_name = parameters[Rule_Engine_Common_Constants.BATCH_NAME]
    client_name = parameters[Rule_Engine_Common_Constants.CLIENT_NAME]
    table_name = parameters[Rule_Engine_Common_Constants.TABLE_NAME]
    bucket = parameters[Rule_Engine_Common_Constants.BUCKET_NAME]
    isRuleEngine = parameters["isRuleEngine"]
    if isRuleEngine:
        table_name = parameters["flow_name"]+"_"+parameters["alias"]
    rule_folder_path = client_name + "/" + batch_name + "/" + table_name + "/" + config.get("S3_DETAILS").get(
        "RULE_ENGINE") + \
                       config.get("S3_DETAILS").get("rule_folder_prefix") + table_name + RuleFileName.RULE_FOLDER_SUFFIX
    write_logs("Info", f"[*****rule folder path is {rule_folder_path}***********]")
    s3 = boto3.resource('s3')
    write_logs("Info", "3.Object(bucket, rule_folder_path)" + rule_folder_path)
    content_object = s3.Object(bucket, rule_folder_path)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    process_config = json.loads(file_content)

    return process_config


def get_files_in_s3(bucket_name, prefix):
    folder = prefix
    s3 = boto3.resource("s3")
    s3_bucket = s3.Bucket(bucket_name)
    files_in_s3 = [f.key.split(folder + "/")[1] for f in s3_bucket.objects.filter(Prefix=folder).all()]
    write_logs("Info", "csv_file_name -----> " + str(files_in_s3))
    return files_in_s3[1]


def get_path_extension(path):
    """
        This function used to split the path to get extension of file
        path : path of the file
        :return full path and extension of file
    """
    file_name = os.path.split(path)[1]
    ext = file_name.split(".")[-1]
    return path, ext


def read_input_file(input_path, spark):
    """
        This function will read different type of input file and return dataframe
        :input_path : path of the file
        :return dataframe
    """
    encoding = "utf-8"
    write_logs("Info", "[ Step : read_input_file ]")
    inputDF = spark.read.format("text").option("charset", encoding).load(input_path)
    # inputDF = inputDF.rdd.zipWithIndex().toDF()
    # inputDF = inputDF.select(expr("_1['value'] as value")).drop("_1", "_2")

    return inputDF


def skip_headers(validation_df, rule_items):
    """
        Method to check for header in between data.
        :param rule_items:
        :param validation_df: Dataframe with all column data into single column
        :return validation_df: Dataframe with new remove_row_col set to true or false
    """
    # Step : skip_headers
    delimiter = ','
    fields = rule_items[rule_helper_constants.FIELDS]
    total_fields = len(fields)

    # Creating header by picking first two columns from schema
    # Appending delimiter at end if number of columns greater than two
    header = delimiter.join([field[JsonParamKeys.FIELD_NAME_ATTR] for field in fields[:2]]) + \
             (delimiter if total_fields > 2 else CharacterConstants.BLANK)
    header = header.replace(CharacterConstants.SPACE,
                            CharacterConstants.BLANK).lower()
    columns = validation_df.columns

    select_expr = f"case when lower(value) like '{header}%' " \
                  f"then true " \
                  f"else false end as {Additional_Columns.REMOVE_ROW_COL}"
    validation_df = validation_df.select(*columns, expr(select_expr))
    # This will remove the rows from input file which is set to true
    validation_df = remove_rows(validation_df)

    return validation_df


def escape_delimiter(delimiter):
    """
    Method to add \\ to escape | in regex pattern.
    :return delimiter: Modified file delimiter
    """
    delimiter = "".join([f"\\\\{char}" for char in delimiter])
    return delimiter


def escape_delimiters(delimiter):
    """
    Method to add \\ to escape | in regex pattern.
    :return delimiter: Modified file delimiter
    """
    delimiter = "".join([f"\\{char}" for char in delimiter])
    return delimiter


def skip_blanklines(validation_df):
    """
    This function will skip the blank line from spark dataframe
    :validation_df Input dataframe
    :return validation_df : dataframe without blank lines data
    """
    # Step : skip_blanklines 
    delimiter = escape_delimiter(NumericValidationParams.DELIMITER)
    columns = validation_df.columns
    select_expr = f"case when translate(value, '{delimiter}', '') == '' " \
                  f"then true " \
                  f"else false end as {Additional_Columns.REMOVE_ROW_COL}"
    validation_df = validation_df.select(*columns, expr(select_expr))
    # This will remove the rows from input file which is set to true
    validation_df = remove_rows(validation_df)

    return validation_df


def single_to_multicolumn(validation_df, rule_items, parameters):
    """
    This function will convert single column dataframe to multi column dataframe
    :validation_df Input dataframe
    :rule_items : It has all the field name
    :return validation_df : dataframe without blank lines data
    """
    # Step : single_to_multicolumn
    fields = rule_items[rule_helper_constants.FIELDS]
    delim = parameters[rule_helper_constants.DELIMETER]
    delimiter = escape_delimiters(delim)

    field_name_list = []
    for field in fields:
        field_name_list.append(field[rule_helper_constants.FIELDNAME])

    validation_df = validation_df.select(f.split(validation_df.value, delimiter)).rdd.flatMap(lambda x: x).toDF(
        schema=field_name_list)

    return validation_df


def remove_rows(validation_df):
    """
        Method to remove blank lines & headers from dataframe.
        :param validation_df: Dataframe containing data
        :return validation_df: Dataframe without headers and blanklines
    """
    # Step : remove_rows
    # Filtering rows with codepage error
    if Additional_Columns.col_code_page_error in validation_df.columns:
        validation_df = validation_df.filter(
            validation_df[Additional_Columns.col_code_page_error] == CommonFlags.TRUE.lower()).drop(
            validation_df[Additional_Columns.col_code_page_error])

    # Filtering rows with blank lines and headers
    validation_df = validation_df.filter(~validation_df[Additional_Columns.REMOVE_ROW_COL]).drop(
        Additional_Columns.REMOVE_ROW_COL)

    return validation_df


def date_numeric_validation(validation_df, rule_items):
    """
        Method to validate date and numeric type data.
        :param rule_items: rule file
        :param validation_df: Dataframe with all numeric, date & varchar columns
        :return validation_df: Dataframe with struct type date & numeric column
    """
    # Step : date_numeric_validation

    select_ls = []
    column = []
    items = rule_items[rule_helper_constants.FIELDS]

    for col in validation_df.columns:
        for d in items:
            if d[JsonParamKeys.FIELD_NAME_ATTR] == col:
                del column[:]
                column.append(d)
                break

        if column[0][JsonParamKeys.TYPE_ATTR] in Mssql_types.MSSQL_NUMERIC \
                or column[0][JsonParamKeys.TYPE_ATTR] in Mssql_types.MSSQL_INTEGER \
                or column[0][JsonParamKeys.TYPE_ATTR] in Mssql_types.MSSQL_BIGINT:

            # Numeric Validation
            select_ls.append(
                NumericValidation().numeric_validation(col, column[0]))


        elif column[0][JsonParamKeys.TYPE_ATTR] in Mssql_types.MSSQL_DATETIME:
            # Date Validation
            select_ls.append(DateValidation().date_validation(col, column[0]))
            write_logs("Info", "select_ls : ", select_ls)
            # self.date_numeric_column_count += 1

        else:
            select_ls.append(col)
            # select_ls.append(expr(f"translate(`{col}`, '\t', ' ') as `{col}`"))

    # df before expression
    validated_df = validation_df.select(*select_ls)

    return validated_df


def add_review_column(validation_df):
    """
        Method to add review column and error column in dataframe after date and numeric validation,
        delta column holds invalid values in case of value conversion failure.
        :param validation_df: Dataframe has date & numeric column with struct type
        :return validation_df: Dataframe with delta column & error column
    """
    # Step : add_review_column
    # Creating schema for numeric fields
    numeric_fields = [StructField(JsonParamKeys.OUTPUT_VAL, StringType(), True),
                      StructField(JsonParamKeys.INPUT_VAL, StringType(), True),
                      StructField(JsonParamKeys.IS_DEFAULT,
                                  BooleanType(), True),
                      StructField(JsonParamKeys.IS_ERROR, BooleanType(), True),
                      StructField(JsonParamKeys.ERROR_MESSAGE, StringType(), True)]

    # Creating schema for date fields
    date_fields = [StructField(JsonParamKeys.OUTPUT_VAL, StringType(), True),
                   StructField(JsonParamKeys.INPUT_VAL, StringType(), True),
                   StructField(JsonParamKeys.IS_DEFAULT, BooleanType(), True),
                   StructField(JsonParamKeys.IS_ERROR, BooleanType(), True),
                   StructField(JsonParamKeys.ERROR_MESSAGE, StringType(), True)]

    # Creating new column col_reject_flag with false value
    # Record will be move to rejected records if this flag column is set to true

    select_ls = []

    reject_flag_col = []
    error_col = []
    review_col = []
    input_col = []

    is_date_numeric_col_exist = False

    # In this loop error columns for all date & numeric columns will be added to dataframe
    # Column col_reject_flag will be set to true if numeric or date validation had failed
    for col in validation_df.columns:
        if validation_df.schema[col].dataType == StructType(numeric_fields) or \
                validation_df.schema[col].dataType == StructType(date_fields):
            is_date_numeric_col_exist = True

            reject_flag_col.append(f"`{col}`['{JsonParamKeys.IS_ERROR}']")

            error_col.append(f"(case when `{col}`['{JsonParamKeys.IS_ERROR}'] "
                             f"then concat(`{col}`['{JsonParamKeys.ERROR_MESSAGE}'], '{NumericValidationParams.DELIMITER}') "
                             f"else '' end)")

            review_col.append(f"case when `{col}`['{JsonParamKeys.IS_DEFAULT}'] "
                              f"then concat(\"'\", \"{col}\", \"'\", \":\", \"'\", "
                              f"`{col}`['{JsonParamKeys.INPUT_VAL}'], \"'\", \",\") "
                              f"else \"\" end")

            input_col.append(expr(f"case when not {Additional_Columns.reject_flag_col} "
                                  f"then `{col}`['{JsonParamKeys.OUTPUT_VAL}'] "
                                  f"else `{col}`['{JsonParamKeys.INPUT_VAL}'] "
                                  f"end as `{col}`"))

        else:
            select_ls.append(col)

    if is_date_numeric_col_exist:
        validation_df = validation_df.drop(Additional_Columns.reject_flag_col)
        validation_df = validation_df.select("*",
                                             expr(
                                                 f"concat({','.join(error_col)}) as error_temp"),
                                             expr(
                                                 f"concat({','.join(review_col)}) as delta_temp"),
                                             expr(f"{' or '.join(reject_flag_col)}  "
                                                  f"as {Additional_Columns.reject_flag_col}")
                                             )

        validation_df = validation_df.select(*select_ls,
                                             Additional_Columns.reject_flag_col,
                                             expr(f"substring(error_temp, 1, "
                                                  f"length(error_temp) - {len(NumericValidationParams.DELIMITER)}) "
                                                  f"as {Additional_Columns.Error_Column}"),
                                             expr(f"concat('{{', substring(delta_temp, 1, "
                                                  f"length(delta_temp) - 1), '}}') "
                                                  f"as {Additional_Columns.Review_Column}"),
                                             *input_col)
    else:
        validation_df = validation_df.select("*",
                                             expr(
                                                 f"false as {Additional_Columns.reject_flag_col}"),
                                             expr(
                                                 f"'' as {Additional_Columns.Error_Column}"),
                                             expr(f"'{{}}' as {Additional_Columns.Review_Column}"))

    return validation_df


def filter_record_after_numeric(validation_df):
    """
        Method to filter date & numeric rejected records from dataframe.
        :param validation_df: Dataframe containing data
        :return (validation_df, error_df_numeric): Tuple of success records &
        error records dataframe
    """
    # Step : filter_record_after_numeric
    # Filtering error records from validation_df
    error_df_numeric = validation_df \
        .filter(validation_df[Additional_Columns.reject_flag_col]) \
        .drop(Additional_Columns.Review_Column, Additional_Columns.reject_flag_col)

    # Filtering success records from validation_df
    validation_df_new = validation_df \
        .filter(~validation_df[Additional_Columns.reject_flag_col]) \
        .drop(Additional_Columns.reject_flag_col, Additional_Columns.Error_Column)
    
    return validation_df_new, error_df_numeric


def drop_column(data_frame, col_arr):
    """
    :param data_frame:
    :param col_arr:
    :return:
    """
    try:
        # get the dataframe column name list
        df_cols_list = data_frame.columns
        col_seq_dict = {}
        for i in df_cols_list:
            # add the column with index position in col_seq_dict
            col_seq_dict[df_cols_list.index(i)] = i
        for x in col_arr:
            # check if col_arr contains the index to be deleted
            if col_seq_dict.__contains__(x):
                data_frame = data_frame.drop(col_seq_dict[x])
                write_logs("Info", "column " + str(col_seq_dict[x]) + " dropped successfully")
        return data_frame

    except Exception as e:
        write_logs("Error", "Error occured in droping column" + str(traceback.print_exc()))


def swap_df_columns(data_frame, swap_col_dict):
    """
    :param data_frame:
    :param swap_col_dict:
    :return:
    """
    try:
        # get the dataframe column name list
        df_col_list = data_frame.columns
        for k, v in swap_col_dict.items():
            # swap the index of column in list
            df_col_list[k], df_col_list[v] = df_col_list[v], df_col_list[k]
            write_logs("Info", "Column " + str(df_col_list[k]) + " swapped with column " + df_col_list[v])
        data_frame = data_frame.select(*df_col_list)
        return data_frame

    except Exception as e:
        write_logs("Error", "Error occured in swapping column column" + str(traceback.print_exc()))


def add_column(data_frame, column_input):
    """
    :param data_frame:
    :param columns:
    :return:
    """
    try:
        # get the dataframe column name list
        df_col_list = data_frame.columns
        for x in column_input:
            for k, v in x.items():
                if (k == columnconstant.POSITION):
                    # add the new column entry with specified index in df_col_list
                    df_col_list.insert(int(v), x.get(columnconstant.FIELDNAME))
                    data_frame = data_frame.withColumn(x.get(columnconstant.FIELDNAME),
                                                       f.lit(x.get(columnconstant.VALUE)).cast(
                                                           x.get(columnconstant.TYPE)))
                    write_logs("Info", "Column " + str(x.get(columnconstant.FIELDNAME)) + " added successfully")
        data_frame = data_frame.select(*df_col_list)
        return data_frame

    except Exception as e:
        write_logs("Error", "Error occured in adding column" + str(traceback.print_exc()))


def s3_file_size(bucket, prefix):
    s3 = boto3.resource('s3')
    object = s3.Object(bucket, prefix)
    file_size = object.content_length  # size in bytes
    return file_size


def check_column_count(validation_df, delimiter, column_count):
    """
        Method to check for number of columns in each row if column does not
        match columns in schema than set column_count_error true.
        :param validation_df: Dataframe with all column data into single column
        :return validation_df: Dataframe with new column_count_error set to true or false
    """

    # Fetching number of columns from layout json
    column_count = column_count

    # Adding \\ to escape | in regex pattern
    delimiter = escape_delimiter(delimiter)
    select_expr = f"case when size(split(value, '{delimiter}')) == {column_count} " \
                  f"then false " \
                  f"else true end as column_count_error"
    validation_df = validation_df.select("*", expr(select_expr))

    return validation_df


def filter_records(validation_df, delimiter, column_count):
    """
        Method to filter records with column mismatch.
        :param validation_df: Dataframe containing data
        :return (validation_df, error_df): Tuple of success records &
        error records dataframe
    """

    # Adding \\ to escape | in regex pattern
    delimiter = escape_delimiter(delimiter)

    validation_df = validation_df.select("*", expr(
        f"split(value, '{delimiter}') as single_column_field"))
    #     validation_df.persist(StorageLevel.MEMORY_AND_DISK)

    # Filtering column mismatch error records from validation_df
    error_df = validation_df.filter(validation_df["column_count_error"]) \
        .drop("column_count_error")

    error_df = error_df.select("*",
                               expr(f"concat('Expected {column_count} "
                                    f"fields but found ', size(single_column_field)) "
                                    f"as errors"))

    #  Filtering success records from validation_df
    validation_df = validation_df.filter(~validation_df["column_count_error"]) \
        .drop("column_count_error")

    return validation_df, error_df.drop("single_column_field")


def remove_linebreak(validation_df, rule_items):
    """
    This function will remove the line break from spark dataframe
    :validation_df Input dataframe
    :return validation_df : dataframe without line break data
    """
    delimiter = rule_items["delimiter"]

    # calculating the delimeter and double Quotes count in each row of data
    validation_df = validation_df.withColumn(rule_helper_constants.DEL_COUNT_ALIAS,
                                             F.size(F.split(rule_helper_constants.COL_NAME_LINEBREAK, delimiter)))
    validation_df = validation_df.withColumn(rule_helper_constants.DQ_COUNT_ALIAS,
                                             F.size(F.split(rule_helper_constants.COL_NAME_LINEBREAK, '"')) - 1)

    fields = rule_items["fields"]
    del_count = len(fields)

    # if the row delimeter count is less than header delimiter count or double quotes count is odd then marking the particular row as linebreak
    validation_df = validation_df.withColumn(rule_helper_constants.LINEBREAK_GRP_NAME, when(((
                                                                                                         col(rule_helper_constants.DEL_COUNT_ALIAS) < del_count) | (
                                                                                                         col(rule_helper_constants.DQ_COUNT_ALIAS) % 2 != 0)),
                                                                                            rule_helper_constants.ROW_HAVING_LINEBREAK).otherwise(
        validation_df.value))

    # After marking the line break row create id and segment group of each row having linebreak.
    df1 = validation_df.rdd.zipWithIndex().toDF()
    validation_df = df1.select(col("_1.*"), col("_2").alias(rule_helper_constants.LINEBREAK_ID))

    validation_df = validation_df.withColumn(rule_helper_constants.LINEBREAK_SEGMENT, f.sum(f.when(
        f.lag(rule_helper_constants.LINEBREAK_GRP_NAME, 1).over(
            Window.orderBy(rule_helper_constants.LINEBREAK_ID)) != f.col(rule_helper_constants.LINEBREAK_GRP_NAME),
        1).otherwise(0)).over(Window.orderBy(rule_helper_constants.LINEBREAK_ID)) + 1)

    # conactente two or more row if there is linebreak and remove helper column that is previously used.
    validation_df = validation_df.groupby(rule_helper_constants.LINEBREAK_SEGMENT).agg(
        f.concat_ws(",", f.collect_list(validation_df.value))).withColumnRenamed("concat_ws(,, collect_list(value))",
                                                                                 "value").drop(
        rule_helper_constants.LINEBREAK_SEGMENT)

    # filter the header out from data
    header = validation_df.first()[0]
    validation_df = validation_df.filter(~col(rule_helper_constants.COL_NAME_LINEBREAK).contains(header))

    return validation_df


def clean_controlchar(validation_df, rule_items):
    """
    This function will remove Junk records 
    :validation_df Input dataframe
    :return validation_df : dataframe without junk records data
    """
    delimiter = rule_items["delimiter"]
    validation_df = column_cleansing(validation_df, delimiter)

    return validation_df


def remove_columnshift(validation_df, rule_items, parameters):
    """
    This function will skip the blank line from spark dataframe
    :validation_df Input dataframe
    :return validation_df : dataframe without blank lines data
    """
    client_name = parameters["client_name"]
    table_name = parameters["table_name"]
    bucket = parameters["bucket_name"]

    creation_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    delimiter = rule_items["delimiter"]
    fields = rule_items["fields"]
    column_count = len(fields)
    validation_df = check_column_count(validation_df, delimiter, column_count)

    valid_df, invalid_df = filter_records(validation_df, delimiter, column_count)

    invalid_output_file_path = JsonParamKeys.S3_EXT + bucket + Settings.S3_DETAILS[
        "output_invalid_path"] + client_name + "/" + table_name + "/" + creation_time

    # s3_save(invalid_df, invalid_output_file_path)

    valid_df = valid_df.drop('single_column_field')

    return valid_df, invalid_df


def control_charset_expr(col_name, delimiter):
    """
        Method is use generate sql exprssion to remove unicode characters from
        data.

        :param col_name: Name of the column which needs to be processed
        :param delimiter: Input file delimiter
        :return control_char_regex_string_expr: Sql expression to remove characters from
        data
    """

    CHARACTER_REMOVE_LIST = ["@", '^', '%', ":"]
    # Creating list of unicode charcters which needs to be remove
    all_unicode_chars = (chr(i) for i in range(sys.maxunicode))
    all_control_chars = [c for c in all_unicode_chars if unicodedata.category(c) == 'Cc']
    #     all_control_chars = [c for c in all_unicode_chars]
    all_control_chars.extend(CHARACTER_REMOVE_LIST)

    # Creating sql expression to remove characters
    control_char_regex_string = ""
    for control_char in all_control_chars:
        if control_char != delimiter and control_char != '\t':
            control_char_regex_string = control_char_regex_string + control_char

    control_char_regex_string_expr = 'translate(' + col_name + ', "' \
                                     + control_char_regex_string + '", "")'

    return control_char_regex_string_expr


def column_cleansing(validation_df, delimiter):
    """
        Method clean control characters from data.
        :param validation_df: Dataframe with all column data into single column
        :return validation_df: Dataframe with all control characters removed
    """
    # Getting column names
    df_cols = validation_df.schema.names
    delimiter = delimiter

    if len(df_cols) > 0:
        # Creating sql expression to remove control characters
        col_expr = control_charset_expr(df_cols[0], delimiter)
        columns = validation_df.columns
        columns.remove(df_cols[0])
        validation_df = validation_df.select(expr(f"{col_expr} as {df_cols[0]}"), *columns)

    return validation_df


def get_files_in_s3(bucket_name, prefix):
    folder = prefix
    s3 = boto3.resource("s3")
    s3_bucket = s3.Bucket(bucket_name)
    write_logs("Info", "get_files_in_s3")
    write_logs("Info", "Bucket " + bucket_name)
    write_logs("Info", "prefix " + prefix)
    files_in_s3 = [f.key.split(folder)[1] for f in s3_bucket.objects.filter(Prefix=folder).all()]
    # write_logs("Info","files_in_s3"+files_in_s3)
    # write_logs("Info", "csv_file_name -----> " + str(files_in_s3))

    return files_in_s3[1]
