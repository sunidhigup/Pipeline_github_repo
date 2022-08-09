"""
Constants
---------

Python script   :   rule_engine_constants.py
Version			:	1.0
Description     :   Module contains category wise constant values which is used in application to leverage
                    the maintainability,readability and loose coupling in of over all code.
"""


#############################################################
#        Scintilla Configuration Constants                  #
#############################################################
class GenericConstants:
    """
        This Class is being used for GenericConstants that are being used throughout the code

    """
    INPUT = "input"
    HISTORICAL = "historical"
    LEFT_ANTI = "left_anti"
    HEADER = "header"
    COMPRESSION = "compression"
    GZIP = "gzip"
    ONE = 1
    ZERO = 0
    TWO_FIFTY_SIX = 256
    PRGX_FILE_TAG = "prgxfiletag"
    PRGX_FILE_TAG_PARTITION = "prgxfiletag_partition"
    APPEND = "append"
    CSV = "csv"
    DOT_CSV = ".csv"
    SPARK_CSV_FORMAT = "com.databricks.spark.csv"
    OVERWRITE = "overwrite"
    CSN = "csn"
    DATA_SET_NAME = "data_set_name"
    FRT_ID = "frt_id"
    HASH = "hash"
    DATA = "data"
    NULL = "null"
    SOURCE = 'source'
    EXPORT_ID = 'export_id'
    TABLE_ID = 'table_id'
    LAYOUT = 'layout'


class ParameterValidation:
    """
        This Class contains constants used for parameter validation

    """
    MinioBucket = 's3a://'
    IsPartFile = ['y', 'n']
    Zero = '0'
    Flag = ["n", "y"]
    ConfigPattern = '^https?://'
    SaveNfsMinio = ["n", "m"]
    Checkpoint = ["false", "true"]


class StatsSourceConstants:
    """
        This Class contains constants which provides list of data source for stats computation.

    """
    LOAD = 'load'
    BRIDGE = 'bridge'
    DEFAULT = 'default'
    SOURCE_LIST = [LOAD, BRIDGE, DEFAULT]


class KeyConstants:
    """
        This Class contains constants which is being used in data validation process

    """
    IS_SUCCESS = "isSuccess"
    MESSAGE = "message"


class CharacterConstants:
    """
        This Class contains character constants which are used throughout the code

    """
    UNDERSCORE = "_"
    COMMA = ","
    BLANK = ""
    COLON = ":"
    SPACE = " "
    TILDE = "~"
    PERCENTAGE = "%"
    ONE = "1"
    PIPE = "||"
    DOUBLE_BACK_SLASH = "\\"
    HYPHEN = "-"
    DOT = "."
    EQUALS = "="
    FORWARD_SLASH = "/"
    BOXT = "╦"
    CHARACTER_REMOVE_LIST = ["╦", "^", "\0"]
    REJECT_FILE_SEPARATOR = '^'


class SchemaDictionary:
    """
        This Class contains constants such as DELIMITER, ENCODING which is used to get values from combined json dictionary

    """
    REVISION = "revision"
    DELIMITER = "delimiter"
    ENCODING = "encoding"
    TEXT_QUALIFIER = "textqualifier"
    SKIP_HEADERS = "skipheaders"
    IGNORE_BLANK_LINES = "ignoreblanklines"
    RECORD_QUALIFIER = 'recordqualifier'
    SEPARATOR = '|'


#############################################################
#                  Scintilla Constants                      #
#############################################################

class Step:
    """
        This Class contains constants related to ignore steps in restartability

    """
    IGNORE_STEPS = [10, 11, 12, 13]
    IGNORE_STEPS_DE_DUP = [10, 11, 12]


class JsonParams:
    """
        This Class contains constants values which are being used as a key in JSON
    """
    FIELD_ATTR = 'fields'
    FIELD_NAME_ATTR = 'fieldname'
    FIELD_RULES = 'fieldrules'
    DATE_OUTPUT_FORMAT_RULE = 'dateoutputformat'
    DATE_INPUT_FORMAT_PYTHON = 'dateinputformatpython'
    INVALID_DATES = 'known_invalid_date_list'
    DEFAULT_DATE_VALUE = 'datedefaultvalue'
    DEFAULT_DECIMAL_VALUE = 'decimaldefaultvalue'
    IGNORE_SPECIAL_CHAR = 'ignorespecialcharacters'
    SCALE_ATTR = 'scale'
    SET_SCALE_ROUNDING_MODE = 'setscaleroundingmode'
    DATE_RANGE_CHECK = "daterangecheck"
    ERROR_MESSAGE = "errorMessage"
    COL_NAME = "column_name"
    TYPE_ATTR = 'type'
    COL_TYPE_ATTR = 'col_type'
    ARGS = 'args'
    ARG_VALUE = 'argvalue'
    OUTPUT_VAL = 'outVal'
    INPUT_VAL = 'inputVal'
    IS_CONVERTED = 'isConverted'
    IS_DEFAULT = 'isDefault'
    IS_ERROR = 'isError'
    LOGCONFIG = 'logconfig'
    FILE_LEVEL_RULES = "filelevelrules"
    FIELDS = 'fields'
    TYPE_ATTRIBUTE = 'type'
    DICT_ROUTINE = 'fieldrules'
    DICT_COLUMN_NAME = 'fieldname'
    DICT_RULENAME = 'rulename'
    SKIPHEADERS='skipheaders'
    IGNOREBLANKLINES='ignoreblanklines'
    CONTROLCHAR='junkrecords'
    LINEBREAK='linebreak'
    COLUMNSHIFT='columnshift'



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
        This Class contains constants which contains datatypes values

    """
    MSSQL_NUMERIC = ['numeric', 'float', 'real', 'money', 'smallmoney', 'decimal', 'integer']
    MSSQL_DATETIME = ['smalldatetime', 'date', 'time', 'datetime', 'datetime2', 'datetimeoffset', 'timestamp']
    MSSQL_INTEGER = ['int', 'bit', 'smallint', 'tinyint']
    MSSQL_BIGINT = ['bigint']
    MSSQL_VARCHAR = ['char', 'text', 'varchar']
    MSSQL_NVARCHAR = ['nchar', 'ntext', 'nvarchar']




class Jobs:
    """
        This Class contains constants for job names
    """
    DATA_VALIDATION = "datavalidationjob"
    DE_DUPLICATION = "deduplicationjob"
    STATS = "statsjob"





class ParameterValidationSpark:
    """
        This Class contains constants for parameter validation of Data validation
        Dedup , Stats and Bridge Stats
    """

    class Datavalidation_Dedup:
        job_madatory_args = ["InputPath", "file_partitions", "minio_bucket_path", "csn", "frt_id",
                             "batch_id", "data_set_name", "is_part_file", "fudt_id"]

    class LoadTransformStats:
        job_madatory_args = ["minio_bucket_path", "csn", "frt_id", "data_set_name", "seq"]

    class BridgeStats:
        job_madatory_args = ["csn", "data_set_name", "export_id", "table_id",
                             "source_data_location",
                             "timestamp", "delimiter", "input_columns", "export_type",
                             "prgx_ref_nbr", "std_fields", "checkpoint"]
