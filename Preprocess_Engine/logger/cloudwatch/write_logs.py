import time
from logger.cloudwatch.init import get_cloudwatch

log_group = None
client = get_cloudwatch()
log_stream_name = None
seq_token = None


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


def create_logs(logs):
    """

    :param logs:
    :return:
    """
    messages = str(logs)

    #Making log event
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

    time.sleep(1)

    return None
