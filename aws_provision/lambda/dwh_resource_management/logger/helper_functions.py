import boto3

import func_write_log as write_logger
from func_write_log import create_log_stream


def log_initiator(log_group,log_stream_name):
    """
        This function initiate the logger group
        :parameter : input parameters
        :return
    """

    write_logger.log_group = log_group
    write_logger.log_stream_name=log_stream_name

    create_log_stream()
    
    return None
    
    

    
