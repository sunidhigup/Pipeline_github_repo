class Resource_manage:
    TRUE = "true"
    IS_ACTIVE = "is_active"
    DATA_PROCESSOR_LOG_GROUP = "/aws/vendedlogs/states/CDEP_STATE_MACHINE_1-Logs"
    RULE_ENGINE_LOG_GROUP="cdep_rule_engine_logs"
    RULE_SQS_QUEUE = "cdep_rule.fifo"
    RULE_METADATA = "dep_rule_engine_metadata"

    DWH_QUEUE = "cdep.fifo"
    DWH_METADATA = "dep_flowbuilder_meta_data"
    JOB_TABLE = "dep_flowbuilder_job_name"
    JOB_INPUT_TABLE = "dep_flowbuilder_job_input"
    DWH_STATUS_TABLE = "dep_flowbuilder_job_status"

    DWH_ARN = "arn:aws:states:us-east-1:955658629586:stateMachine:Cdep_resource_management"
    RULE_ENGINE_ARN = "arn:aws:states:us-east-1:955658629586:stateMachine:Rule_engine_resource_management"

    EMR_CLIENT = "emr"
    DYNAMO_CLIENT = "dynamodb"
    SQS_CLIENT = "sqs"
    S3_CLIENT = "s3"
    STEP_FUNCTION_CLIENT = "stepfunctions"
    REGION = "us-east-1"

    FILE_SIZE_CONST = 2
    UNIT_CONVERT = 1024
    INPUT_CONST = "input/"
    DEP_CONST = "dep"
    DATASET_CONST = "GL"
    EXT = ["txt", "csv"]

    FIFO = "true"
    DUPLICATION = "true"
    VISIBLE_TIMEOUT = "5"
    RULE_JOB_STATUS_TABLE="dep_rule_engine_job_status"

class common_constant:
    NAME = "name"
    STATE_MACHINE_ARN = "stateMachineArn"
class call_dwh_constants:
    STATE_MACHINE_NAME = "cdep_resource_management_cdk_step"

class call_ruleengine_constants:
    STATE_MACHINES = "stateMachines"
    STATE_MACHINE_NAME = "rule_engine_resource_management_cdk_step"

class write_sqs_constants:
    CORES = "cores"
    EXTENSIONS = "extensions"
    UNIQUE_ID = "uniqueId"
    CLIENT_ID = "client_id"
    JOB_ID = "job_id"
    LOG_GROUP = "log_group"
    CLIENT_NAME = "client_name"
    RULE_ENGINE = "rule_engine"
    BATCH_NAME  = "batch_name"
    EXECUTION_ID="execution_id"
    EXTENSION_RULE_ENGINE = "_rule_engine.fifo"
    SQS_RULE_ENGINE = "rule_engine_sqs"
    ITEMS = "Items"
    BATCH_ID = "batch_id"
    PARAMS = "params"
    BUCKET_NAME = "bucket_name"
    TABLE_NAME = "table_name"
    JOB_NAME = "job_name"
    DEFAULT_CORES = "cores"
    JOBS = "jobs"
    FIFO = "fifo"
    EXTENSION_QUEUE = "_data_processor.fifo"
    SQS_DATA_PROCESSOR = "data_processor_sqs"
    JOB = "job"
    CLIENT = "client"
    LOG_GROUP_RULE_ENGINE = "DEP_Rule_Engine"
    LOG_GROUP_DATA_PROCESSOR = "DEP_Data_Processor"
    EXTRACTS = "extracts"
    ITEM = "Item"
    BUCKET = "bucket"
    PREFIX = "prefix"
    EXT = "extensions"
    FIFO_QUEUE = "fifo_queue"
    EXT = ["txt","csv"]

    DEFAULT_CORES=4
    FIFO_SUFFIX_RULE_ENGINE="_rule_engine.fifo"
    FIFO_SUFFIX_DATA_PROCESSOR="_data_processor.fifo"
    WRITE_TO_SQS="_write_to_sqs"

class logger_constant:
    PROCESSOR_NAME = "CDEP_RULE_ENGINE_PROCESSOR"
    APP_DEBUG = "Application Debug"
    STEP_SUCCESS = "Step Success"
    STEP_ERROR = "Step Error"
    JOB_SUCCESS = "Job Success"

class character_constants:
    COMMA=","
    UNDERSCORE="_"