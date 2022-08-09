import json
import time
import datetime
from DynamoDb_connector.settings import Settings

log_group = None
log_stream_name = None
seq_token = None
time_stamp = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

def create_logs(client,logs,log_stream):
    """

    :param client:
    :param logs:
    :param log_stream:
    """
    log_group = Settings.LOG_STREAM 
  

    log_stream_name = log_stream
    #Creating log stream
    try:
        client.create_log_stream(
            logGroupName=log_group,
            logStreamName= log_stream_name
        )
    except:
        pass

    messages = str(logs)

    #Creating log event
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

    #Putting log in stream
    response = client.put_log_events(**log_event)
    seq_token = response['nextSequenceToken']
    time.sleep(1)
    


