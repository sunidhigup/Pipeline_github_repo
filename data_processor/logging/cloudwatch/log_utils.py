from data_processor.logging.cloudwatch.write_logs import create_logs
from data_processor.logging.log_formatter import LogFormatter
from data_processor.logging.logger import LogObject, LogTypeEnum


def write_logs(level, msg, step_params=None):
    """

    :param level:
    :param msg:
    :param step_params:
    """
    #Formatting string log values
    if step_params is not None:
        log_operation = LogFormatter(level=level,
                                     step_number=step_params.step_number,
                                     step_name=step_params.step_name,
                                     msg=msg)

    else:
        log_operation = LogFormatter(level=level,
                                     msg=msg)
    #Creating logs
    logs = LogObject(LogTypeEnum.STEP_SUCCESS.value, log_operation.create_log()).get_log_string()

    create_logs(logs)
