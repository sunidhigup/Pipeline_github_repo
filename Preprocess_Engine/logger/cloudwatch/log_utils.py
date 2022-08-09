from logger.cloudwatch.write_logs import create_logs
from logger.log_formatter import LogFormatter
from logger.logger import LogObject, LogTypeEnum
import logger.cloudwatch.write_logs as write_logger
import datetime
from logger.cloudwatch.write_logs import create_log_stream
from logger.constant.constant import logger_constants

def write_logs(level, msg, step_params=None):
    """

    :param level:
    :param msg:
    :param step_params:
    :return:
    """

    #Formatting string Values of logs
    if step_params is not None:
        log_operation = LogFormatter(level=level,
                                     step_number=step_params.step_number,
                                     step_name=step_params.step_name,
                                     msg=msg)

    else:
        log_operation = LogFormatter(level=level,
                                     msg=msg)

    logs = LogObject(LogTypeEnum.STEP_SUCCESS.value, log_operation.create_log()).get_log_string()

    #Creating logs
    create_logs(logs)
    return None

def log_initiator(stream_name):
    """
        This function initiate the logger group
        :parameter : input parameters
        :return
    """
   

    write_logger.log_group = logger_constants.Log_group
    write_logger.log_stream_name = stream_name
    create_log_stream()
    
    write_logs("Info", "[****Preprocessing Jobs Started*********]")
    return None

