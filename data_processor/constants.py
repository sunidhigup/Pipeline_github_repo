timestamp = ""


class Constants:
    """
        # This Class contains constants for data processor
    #
    # """
    SSQL_NUMERIC = ['numeric', 'float', 'real', 'money', 'smallmoney', 'decimal']
    MSSQL_DATETIME = ['smalldatetime', 'date', 'time', 'datetime', 'datetime2', 'datetimeoffset', 'timestamp']
    MSSQL_INTEGER = ['integer', 'bit', 'smallint', 'tinyint']
    MSSQL_BIGINT = ['bigint']
    INJECTOR_EXECUTE_SQL = 'ExecuteSQL'
    INJECTOR_EXECUTE_SQL = 'ExecuteSQL'
    INJECTOR_EXECUTE_SQL = 'ExecuteSQL'
    INJECTOR_EXECUTE_SQL = 'ExecuteSQL'
    INJECTOR_EXECUTE_SQL = 'ExecuteSQL'
    EXEC_SQL_PARAMS = 'params'
    EXEC_SQL_DEFINITIONS = 'definitions'
    EXEC_SQL_STEP_NUMBER = 'step_number'
    EXEC_SQL_STEP_NAME = 'step_name'
    EXEC_SQL_TEMP_VIEW = 'df'
    EXEC_SQL_STATEMENT = 'statement'
    EXEC_SQL_PERSIST = 'persist'
    EXEC_SQL_PERSIST_TYPE = 'persist_type'
    EXEC_SQL_ACTION = 'action'
    EXEC_SQL_DB_NAME = 'db_name'
    DB_NAME = 'database'
    TABLE_NAME = "tablename"
    JOIN_PARAMS = 'params'
    JOIN_TYPE = 'join_type'
    JOIN_CONDITION = 'join_condition'
    JOIN_TEMP_VIEW = 'df'
    JOIN_SELECT_COLS = 'select_cols'
    JOIN_FILTER = 'join_filter'
    JOIN_TABLE_1 = 'table1'
    JOIN_TABLE_1_TEMP_VIEW = 'table1_df'
    JOIN_TABLE_1_COLS = 'table1_cols'
    JOIN_TABLE_1_FILTER = 'table1_filter'
    JOIN_TABLE_2 = 'table2'
    JOIN_TABLE_2_TEMP_VIEW = 'table2_df'
    JOIN_TABLE_2_COLS = 'table2_cols'
    JOIN_TABLE_2_FILTER = 'table2_filter'
    JOIN_ACTION = 'action'
    JOIN_PERSIST = 'persist'
    JOIN_PERSIST_TYPE = 'persist_type'
    MULTI_JOIN_PARAMS = 'params'
    MULTI_JOIN_TEMP_VIEW = 'df'
    MULTI_JOIN_CONDITION = 'join_condition'
    MULTI_JOIN_SELECT_COLS = 'select_cols'
    MULTI_JOIN_FILTER = 'join_filter'
    MULTI_JOIN_PERSIST = 'persist'
    MULTI_JOIN_PERSIST_TYPE = 'persist_type'
    MULTI_JOIN_ACTION = 'action'
    MULTI_JOIN_TABLES = 'tables'
    MULTI_JOIN_TYPES = 'joins'

    Batch_Table = {
        "execution_id": "",
        "client_name": "",
        "batch_name":"",
        "batch_type": "",
        "start_time": "",
        "end_time": "",
        "status": "",
        "phase": ""
    }

    Job_Step_Table = {
        "execution_id": "",
        "step_number": "",
        "step_name": "",
        "batch_type": "",
        "start_time": "",
        "end_time": "",
        "status": "",
        "phase": "",
        "error_description": ""
    }

    Job_Status_Table = {
        "execution_id":"",
        "batch_type": "",
        "start_time": "",
        "end_time": "",
        "status": "",
        "phase": "",
        "error_description": ""
    }

    SCHEMA = {
    "type" : "object",
    "properties" : {
        "name" : {"type" : "string"},
        "transformer_execution_details" : {"type" : "object"},
        "spark_config" : {"type" : "object"},
        "udf" : {"type" : "object"},
        "steps":{"type" : "array"}
    }
}

    batch_table_name = "dep_flowbuilder_batch_status"
    job_step_status_table = "dep_flowbuilder_job_step_status"
    job_table = "dep_flowbuilder_job_input"
    job_status_table_name = "dep_flowbuilder_job_status"
    READ_PATH = 'path'
    READ_FORMAT = 'format'
    DATABASES = ["postgres","mysql","oracle"]


class profile_env_params:
    BUCKETNAME="depconfig"
    KEYNAME="Data_Processor/Config/path.json"
    
class processor_constants:
    ERROR_DETAIL = "error_description"
    INFO = "Info"
    ERROR = "Error"
    BATCH_ID = "batch_id"
    JOB_ID = "job_id"
    UNIQUE_ID = "uniqueId"
    ITEM = "Item"
    CLIENT_NAME = "client_name"
    BATCH_TYPE = "batch_type"
    BATCH_NAME = "batch_name"
    STATUS = "status"
    PHASE = "phase"
    START_TIME = "start_time"
    CLIENT_BATCH_ID = "client_batch_id"
    RUNNING_STATUS = "Running"
    CLIENT = "client"
    BUCKET  = "bucket"
    EXTRACT = "extract"
    EXTRACTS = "extracts"
    FAILED_STATUS = "Failed"
    END_TIME = "end_time"
    COMPLETED_STATUS = "Completed"
    STEPS = "steps"
    METHOD_NAME = "method_name"
    STEP_NUMBER = "step_number"
    STEP_NAME = "step_name"
    EXECUTION_ID="execution_id"
