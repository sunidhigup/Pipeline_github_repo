class Rule_Engine:
    TABLE_NAME = "dep_rule_engine_resource_management"
    BATCH_STATUS_TABLE = "dep_flowbuilder_batch_status"
    JOB_STATUS_TABLE = "dep_rule_engine_job_status"
    SQS_QUEUE = "cdep_rule.fifo"
    INSTANCE_MAP_TABLE = "dep_emr_instance_mapping"
    # JOB_INPUT_TABLE = "dep_flowbuilder_job_input"

    DWH_ARN = "arn:aws:states:us-east-1:955658629586:stateMachine:Cdep_resource_management"

    EMR_CLIENT = "emr"
    DYNAMO_CLIENT = "dynamodb"
    SQS_CLIENT = "sqs"
    STEP_FUNCTION_CLIENT = "stepfunctions"
    REGION = "us-east-1"

    FIFO_SUFFIX_CREATE_EMR = ".fifo"

    EMR_STATE_RUNNING = "RUNNING"
    EMR_STATE_WAITING = "WAITING"

    READY_STATE = "Ready"
    WAIT_STATE = "Wait"

    JOB_COMPLETE = "COMPLETED"
    JOB_FAILED = "FAILED"
    JOB_CANCELLED = "CANCELLED"

    LOGS_URI = 's3://cdep/emr/logs/'
    RELEASE = "emr-6.2.0"

    MASTER_NODE = "Master"
    MASTER_ROLE = "MASTER"
    MARKET = "ON_DEMAND"
    CORE_NODE = "Core"
    CORE_ROLE = "CORE"
    INSTANCES = 1
    KEEP_ALIVE = True
    TERMINATE_PROTECT = False
    SUBNET_ID = "subnet-1ce7fc12"
    BOOTSTRAP_PATH = "s3://dep-develop/emr/BootStrap/BootStrap.sh"
    BOOTSTRAP_NAME = "dep-copy-scripts"
    JOB_FLOW_ROLE = "EMR_EC2_DefaultRole"
    SERVICE_ROLE = "EMR_DefaultRole"
    TIMEOUT = 300

    FIFO = "true"
    DUPLICATION = "true"
    VISIBLE_TIMEOUT = "5"

    STEP_NAME = "dep-spark-run"
    ON_FAIL = "CANCEL_AND_WAIT"
    JAR = "command-runner.jar"
    SUBMIT = "spark-submit"
    MASTER = "yarn"
    MODE = "cluster"
    MEMORY = "6G"
    EXECUTERS = "5"
    ZIP_PATH = "s3://cdep/rule_engine/code/Rule_Engine.zip"
    JAR_PATH = "s3://cdep/rule_engine/jars/cdep-udf-date_2.11-1.1.11.jar,s3://cdep/rule_engine/jars/cdep-udf-numeric_2.11-1.1.4.jar"
    FILE_PATH = "s3://cdep/rule_engine/code/run_rule_engine.py"
    LOG_GROUP = "cdep_rule_engine_logs"
    READ_SQS_MESSAGE = "_read_sqs_message_"
    RETRIVE_CLUSTER = "_retrive_cluster_"
    CREATE_CLUSTER = "_create_cluster_"
    CBMS = "_check_batch_message_status_"
    CHECK_CLUSTER_STATE = "_check_cluster_state_"
    CHECK_CLUSTER_AVAILABLE = "_check_available_cluster_"
    CHECK_JOB_STATUS = "_check_job_status_"
    SUBMIT_JOB = '_submit_job'


class common_constants:
    Json_Config = "rule_engine/config/path.json"
    ERROR = "ERROR"
    INFO = "Info"
    AVAILABLE_CLUSTERS = "Available_clusters"
    STATUS = "status"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    END_TIME = "end_time"
    ITEMS = "Items"
    CLUSTER_ID = "cluster_id"
    ITEM = "Item"
    AVAILABLE_CORES = "Available_cores"
    BATCH_ID = "batch_id"
    CLIENT_NAME = "client_name"
    JOB_QUEUE = "Job_Queue"
    QUEUE_NAME = "Queue_name"
    JOBS = "jobs"
    BATCH_NAME = "batch_name"
    ALL = "All"
    MESSAGES = "Messages"
    MSG_EXIST = "msg_exist"
    BODY = "Body"
    CORES = "cores"
    CLUSTER_AVAILABLE = "cluster_available"
    RECEIPT_HANDLE = "ReceiptHandle"
    TOTAL_CORES = "Total_cores"
    EXECUTION_ID = "execution_id"
    ERROR_DETAIL = "error_detail"
    CLIENT_ID = "client_id"
    MSG_EXIST = "msg_exist"
    EXECUTOR_MEMORY = "executor_memory"
    RECEIPTHANDLE = "ReceiptHandle"
    PROFILE_ENV = "profile_env"
    PROFILE_ENV_BUCKET = "profile_env_bucket"
    RUNNING_STATUS = "RUNNING"


class check_clusters_status_constants:
    CLUSTERS = "Clusters"
    STATE = "state"
    ID = "Id"


class check_job_status_constants:
    STEPS = "Steps"
    STATE = "State"
    STEP_LIST = "Step_list"


class check_next_sqs_msg_constants:
    BATCH_TYPE = "batch_type"
    DAILY = "Daily"
    PHASE = "phase"
    PROCESSING = "Processing"
    CLIENT_BATCH_ID = "client_batch_id"
    JOB_NAME = "job_name"
    START_TIME = "start_time"
    QUEUE_FIFO = "fifo"
    STARTING = "Starting"
    QUEUE_KEY = "rule_engine_sqs"


class read_sqs_constants:
    DATA_PROCESSOR_SQS = "data_processor_sqs"
    RULE_ENGINE_SQS = 'rule_engine_sqs'


class submit_spark_job_constants:
    STEPS_PENDING = "steps_pending"
    END_TIME = "end_time"
    BUCKET = "bucket"
    EXTRACT = "extract"
    STEP_LIST = "Step_list"
    JOB_NAMES = "job_names"
    STOPPED = "STOPPED"
    STEPS_IDS = "StepIds"


class create_emr_constants:
    MAX_CORES = "max_cores"
    MIN_CORES = "min_cores"
    INSTANCE_NAME = "instance_name"
    DRIVER = "driver"
    JOB_FLOW_ID = "JobFlowId"
    EXTENSION_QUEUE = ".fifo"
    QUEUE_JOB = "Job_Queue"
    LOG_GROUP = "DEP_Data_Processor"
    NUMBER_OF_INSTANCES = "number_of_instances"
    NUMBER_OF_INSTANCE = "no_of_instance"
    EXECUTOR_MEMORY = "executor_memory"


class logger_constant:
    PROCESSOR_NAME = "CDEP_RULE_ENGINE_PROCESSOR"
    APP_DEBUG = "Application Debug"
    STEP_SUCCESS = "Step Success"
    STEP_ERROR = "Step Error"
    JOB_SUCCESS = "Job Success"