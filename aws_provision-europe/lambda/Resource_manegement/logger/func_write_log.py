import datetime
import json
from enum import Enum
import time
from constants.constant import logger_constant,Resource_manage
import boto3



log_group = None
log_stream_name = None
seq_token = None


def get_cloudwatch():
    """
    :return:
    """
    
    client = boto3.client('logs', region_name='us-east-1')
    
    return client

client = get_cloudwatch()



class LogFormatter:
    """
    This class is used as formatter for string log values.
    :param level: INFO, ERROR
    :param file_name: name of the file
    :param file_size: size of the file
    :param source_rec_count: number of records in source file
    :param target_record_count: number of records in target file
    :param reject_record_count: number of rejected records
    :param step: StepEnum value corresponding to log step
    :param status_cd:  0 for Success, 1 for Error
    :param status_message: status message
    """

    def __init__(self,
                 level,
                 msg=None
                 ):
        self.log_timestamp = str(datetime.datetime.now())
        self.level = level
        self.msg = msg

    # method to return formatted string for logging
    def create_log(self):
        """
        Method to return formatted string for logging
        :return: Formatted log
        """
        return json.dumps(self.__dict__)

class LogObject(object):
    """
        This class is used as formatter for string log values.
        :param log_type: Type of log
        :param log_msg: Log message
        :return
    """

    def __init__(self, log_type, log_msg):
        self.log_type = log_type
        self.log_msg = log_msg
        self.system_identifier = logger_constant.PROCESSOR_NAME

    def get_log_string(self):
        """
            This methods converts json format logs into string format.
        """
        return json.dumps(self.__dict__)


class LogTypeEnum(Enum):
    """
    This is Enum which defines enums for types of log.
    """
    APP_DEBUG = logger_constant.APP_DEBUG
    STEP_SUCCESS = logger_constant.STEP_SUCCESS
    STEP_ERROR = logger_constant.STEP_ERROR
    JOB_SUCCESS = logger_constant.JOB_SUCCESS

def create_logs(logs):
    """

    :param logs:
    :return:
    """
    messages = str(logs)
    #Creating log event
    log_event = {
        'logGroupName': log_group,
        'logStreamName': log_stream_name,
        'logEvents': [
            {
                'timestamp': int(round(time.time() * 1000)),
                'message': messages
            },
        ],
    }

    global seq_token
    if seq_token:
        log_event['sequenceToken'] = seq_token

    response = client.put_log_events(**log_event)
    seq_token = response['nextSequenceToken']

    time.sleep(10)

    return None

def write_logs(level, msg):
    """

    :param level:
    :param msg:
    :return:
    """
    #Formatting string in Logs
    log_operation = LogFormatter(level=level,
                                     msg=msg)

    logs = LogObject(LogTypeEnum.STEP_SUCCESS.value, log_operation.create_log()).get_log_string()
    #Creating logs
    create_logs(logs)

    return None
    
def create_log_stream():
    """
    :return:
    """
    #Creating log stream
    client.create_log_stream(
        logGroupName=log_group,
        logStreamName=log_stream_name
    )
    #create_log_stream successfully
    return None