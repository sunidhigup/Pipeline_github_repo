from aws_cdk import core
#from aws_provision.config import kinesis_config
from constant.constant import STACKS_CONSTANTS
from provision.resources import Kinesis_stack
import json


class Dep_kinesis_Stack(core.Stack):
    """Stack creation of Infra

    Args:
        core (aws.core.Stack): Stack class from aws
    """    

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        """init class for Infra Stack

        Args:
            scope (core.Construct)
            id (str)
        """        
        env = kwargs[STACKS_CONSTANTS.ENV]
        super().__init__(scope, id, env=env)
        config = kwargs[STACKS_CONSTANTS.CONFIG]
        self.cfg = config

        kinesis_path = self.node.try_get_context(self.cfg)['kinesis_config']

    
        Kinesis_stack.createkinesis(self,kinesis_path)
