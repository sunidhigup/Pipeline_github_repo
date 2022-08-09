import json
from aws_cdk import aws_sqs as sqs

def create_sqs(self,path):
    """Create SQS Queue 

    Args:
        path (String): path to config
    """    
    #Read config file
    config = sqs_config(path)

    #Set up Queue
    for queue in config["queue"]:
        sqs.Queue(self, queue["queue_name"],queue_name = queue["queue_name"],fifo=True)


def sqs_config(path):
    """Reading config file for sqs

    Args:
        path (string): path for config

    Returns:
        dictionary: config for sqs
    """    
    #Reading config file
    with open(path, 'r') as f:
        sqs_config = json.load(f)

    return sqs_config