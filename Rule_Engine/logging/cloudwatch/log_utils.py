from Rule_Engine.logging.cloudwatch.write_logs import create_logs
from Rule_Engine.logging.log_formatter import LogFormatter
from Rule_Engine.logging.logger import LogObject, LogTypeEnum


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

