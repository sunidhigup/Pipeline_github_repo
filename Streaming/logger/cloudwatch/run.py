from logger.cloudwatch.createlogs import create_logs
from logger.cloudwatch.readlogs import read_logs
from logger.cloudwatch.init import get_cloudwatch
from DynamoDb_connector.dml.read import get_stream_name
from logger.log_formatter import LogFormatter
from logger.logger import LogObject,LogTypeEnum,get_logger

def write_logs(phase,mode,log_stream):
    """

    :param phase:
    :param mode:
    :param log_stream:
    """
    client = get_cloudwatch()
    stream_name= get_stream_name()
    string_list=stream_name.split('_')
    client_name=string_list[0]
    log_operation_start = LogFormatter(stream_name, client_name,
                                                 phase,
                                                 source_rec_count='',
                                                 target_record_count='', reject_record_count='')
   #Creating logs based on Info/Error
    if mode== "info":
        logs= LogObject(LogTypeEnum.STEP_SUCCESS.value, log_operation_start.create_log()).get_log_string()
    if mode == "error":
        logs=LogObject(LogTypeEnum.STEP_ERROR.value, log_operation_start.create_log()).get_log_string()

    create_logs(client,logs,log_stream)
    


def read_logs():
    """

    :return:
    """
    client = get_cloudwatch()
    stream_name= get_stream_name()
    string_list=stream_name.split('_')
    client_name=string_list[0]
    #Rreading logs from stream
    logs = read_logs(client,stream_name,client_name)
    return logs
