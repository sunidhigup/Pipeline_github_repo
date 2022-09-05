from aws_cdk import aws_kinesis as kinesis
from aws_cdk.core import Duration
import json


def createkinesis(self,path):
    """
      Creates new Kinesis stream

      Args:
            path (str): path of config
            
      Returns:
         KinesisStream: newly created stream
     """
     #Reading kinesis config file
    config = kinesis_config(path)
    #Making kinesis stream
    kinesis_stream = kinesis.Stream(self, config["logical_id"],
                                    encryption=None,
                                    stream_name=config["name"],
                                    shard_count=config["shard"],
                                    retention_period=Duration.hours(config["retention_period"]))

    return kinesis_stream


def kinesis_config(path):
    """ Fetches config for Kinesis

     Returns:
         dict : config for KInesis
     """
    #Reading config file
    with open(path) as f:
        kinesis_config = json.load(f)

    return kinesis_config
