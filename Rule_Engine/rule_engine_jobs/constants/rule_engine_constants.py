"""
Constants
---------
Python script   :   rule_engine_constants.py
Version			:	1.0
Description     :   Module contains category wise constant values which is used in application to leverage
                    the maintainability,readability and loose coupling in of over all code.
"""


class DynamoDbStatus:
    STARTED = 'Started'
    IN_PROGRESS = 'In Progress'
    ERROR = 'Error'
    COMPLETED = 'Completed'
    ID = 'CDEP_RULE_ENGINE_'
    DB_METADATA_TABLE = 'dep_rule_engine_metadata'
    DB_RULE_TABLE = 'dep_rules'


class JsonParamKeys:
    """
        This Class contains constants values which are being used as a key in JSON
    """
    FIELD_ATTR = 'fields'
    FIELD_NAME_ATTR = 'fieldname'
    FIELD_RULES = 'fieldrules'
    DATE_OUTPUT_FORMAT_RULE = 'dateoutputformat'
    DEFAULT_DATE_VALUE = 'datedefaultvalue'
    DEFAULT_DECIMAL_VALUE = 'decimaldefaultvalue'
    ERROR_MESSAGE = "errorMessage"
    COL_NAME = "column_name"
    TYPE_ATTR = 'type'
    COL_TYPE_ATTR = 'col_type'
    ARGS = 'args'
    ARG = 'arg'
    RULE_NAME = "rulename"
    ARG_VALUE = 'argvalue'
    OUTPUT_FORMAT = "output_format"
    OUTPUT_VAL = 'outVal'
    INPUT_VAL = 'inputVal'
    IS_CONVERTED = 'isConverted'
    IS_DEFAULT = 'isDefault'
    IS_ERROR = 'isError'
    FIELDS = 'fields'
    TYPE_ATTRIBUTE = 'type'
    S3_EXT = 's3://'
    RULE_LIST_SEPERATOR = ','
    RULE_LIST_SEPERATOR_DATE = ';'
    ARG_LIST_SEPERATOR = ',,,'


class CommonFlags:
    """
        This Class contains flag constants
    """
    TRUE = 'true'
    FALSE = 'false'
    INFO = 'INFO'
    ERROR = 'ERROR'
    SUCCESS_MSG = 'Success'


class Mssql_types:
    """
        This Class contains constants which contains datatype values
    """
    MSSQL_NUMERIC = ['numeric', 'float', 'decimal', 'integer']
    MSSQL_DATETIME = ['smalldatetime', 'date', 'time', 'datetime', 'timestamp']
    MSSQL_INTEGER = ['int', 'bit', 'smallint', 'tinyint']
    MSSQL_BIGINT = ['bigint']
    MSSQL_VARCHAR = ['char', 'text', 'varchar']
    MSSQL_NVARCHAR = ['nchar', 'nvarchar']


class Additional_Columns:
    """
        This Class contains constants related to additional columns

    """
    Review_Column = "review_column"
    reject_flag_col = "reject_flag_column"
    REMOVE_ROW_COL = "remove_row_column"
    Error_Column = "error_column"
    col_code_page_error = "code_page_error"


class DateValidationParams:
    """
    This Class contains constants related to date validation
    """

    DATE_DEFAULT_VALUE = "1900-01-01"
    TIME_DEFAULT_VALUE = "00:00:00.000"
    DATE_DEFAULT_FORMAT = "yyyy-MM-dd"
    TIME_DEFAULT_FORMAT = "HH:mm:ss.SSS"
    DATE_OUTPUT_FORMAT = "yyyy-MM-dd"


class NumericValidationParams:
    """
    This Class contains constants related to numeric validation
    """
    INT_TYPE_LIST = "int,bigint,integer,decimal"
    DELIMITER = ","


class CharacterConstants:
    """
        This Class contains character constants which are used throughout the code

    """
    BLANK = ""
    SPACE = " "
    DOT = "."
    SLASH = "/"


class profile_env_keys:
    KEYNAME = "rule_engine/config/path.json"


class rule_engine_processor_constants:
    INFO = "Info"
    JAR_FOLDER_PATH = "jar_folder_path"
    DB_STATUS_TABLE = "db_status_table"
    FILE_EXTENSION = "file_extension"
    INPUT_FOLDER_PREFIX = "input_folder_prefix"
    OP_VALID_PATH = "output_valid_path"
    OP_INVALID_PATH = "output_invalid_path"
    PROCESSED_FOLDER_PREFIX = "processed_folder_prefix"
    INFO_ROW_LEVEL = "[******* Starting Executing Row Level Validation *********]"
    INFO_COL_LEVEL = "[******* Starting Executing Column Level Validation *********]"
    INFO_DYNAMO_UPDATE = "[**Updating job status to dynamodb table**]"
    ERROR_DETAIL = "error_detail"
    BATCH_NAME = "batch_name"
    INFO_PROCESS_CMPLT = "[********Process completed***********]"
    STATUS_FAILED = "Failed"
    INFO_ERROR = "[********Error caught***********]"


class rule_engine_udfs_constants:
    SKIP_HEAD = "skipheaders"
    IGNORE_BL = "ignoreblanklines"
    RULE_NAME = "rule_name"
    PACKAGE = "package"
    ITEMS = "Items"


class RuleFileName:
    """
        This Class contains character constants which are used throughout the code
    """
    r = {
        "layout_file_path": "table_layout_json", "client_file_path": "client_rule",
        "global_file_path": "global_rule", "rules_file_path": "table_rule"
    }
    TABLE_LAYOUT = "table_layout_json"
    CLIENT_RULE = "client_rule"
    GLOBAL_RULE = "global_rule"
    TABLE_RULE = "table_rule"
    RULE_FOLDER = "dep"
    RULE_FOLDER_SUFFIX = ".json"


class DataframeConstant:
    """
    This class contains the dataframe specif operation constants
    """
    # block size in bytes for data storage on spark partiton
    BLOCK_SIZE = 256000000

class rule_helper_constants:
    PROFILE_ENV_BUCKET = "profile_env_bucket"
    ID = "id"
    START_TIME = "start_time"
    BATCH_ID = "batch_id"
    ERROR_DETAIL = "error_detail"
    LOG_GROUP = "log_group"
    INFO_RE_STARTED = "[****Rule Engine Jobs Started*********]"
    PARAMS = "params"
    FIELDS = "fields"
    DELIMETER = "delimiter"
    FIELDNAME = "fieldname"
    CLIENT_NAME = "client_name"
    TABLE_NAME = "table_name"
    EXECUTION_ID="execution_id"
    REGION_NAME = "region_name"
    PROFILE_ENV = "profile_env"
    ITEMS = "Items"
    DEL_COUNT_ALIAS = 'delimeter_count'
    DQ_COUNT_ALIAS = 'Double_Quotes_count'
    ROW_HAVING_LINEBREAK = 'LINEBREAK'
    COL_NAME_LINEBREAK = 'value'
    LINEBREAK_GRP_NAME = 'group'
    LINEBREAK_ID = 'id'
    LINEBREAK_SEGMENT = 'segment'
    BATCH_NAME = "batch_name"

class columnconstant:
    COLUMN_ADD="column_add"
    POSITION="position"
    SWAP_FIELD="swap_field"
    SWAP_COL_ONE="swap_col_one"
    SWAP_COL_TWO="swap_col_two"
    DEL_COL_SEQ="del_col_seq"
    POSITION="position"
    FIELDNAME="fieldname"
    VALUE="value"
    TYPE="type"



