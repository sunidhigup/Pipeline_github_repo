import json
import datetime
from enum import Enum

from Constant.constant import logger_constant

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
        self.system_identifier = "spark"

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


def get_logger(spark_session):
        """
        This method return logger used for logging.
        :return:
        """
        logger= None
        if logger is None:
            log4j_logger = spark_session.sparkContext._jvm.org.apache.log4j
            logger = log4j_logger.LogManager.getLogger(__name__)
        return logger