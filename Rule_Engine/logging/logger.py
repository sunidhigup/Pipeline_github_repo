import imp
import json
from enum import Enum
from Rule_Engine.logging.Constant.constant import logger_constant

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


