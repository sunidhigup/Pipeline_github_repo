
from logger.logger import LogObject,LogTypeEnum,get_logger


def write_to_console(streamData):
    """

    :param streamData:
    :return:
    """
    query = (
            streamData.writeStream
            .format("console")
            .outputMode("update")
            .queryName("count")
            .start())
    
    return query