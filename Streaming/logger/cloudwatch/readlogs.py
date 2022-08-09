import boto3

import datetime

def read_logs(client,stream_name,client_name):
    """

    :param client:
    :param stream_name:
    :param client_name:
    :return:
    """
    #Reading logs from stream
    response = client.get_log_events(
        logGroupName="aws/Kinesis"+stream_name,
        logStreamName=client_name,
        startTime=int(datetime.datetime(2021, 8, 19, 0, 0).strftime('%s'))*1000,
        endTime=int(datetime.datetime(2021, 8, 20, 0, 0).strftime('%s'))*1000,
        limit=123,
        startFromHead=True
    )

    log_events = response['events']
    return log_events