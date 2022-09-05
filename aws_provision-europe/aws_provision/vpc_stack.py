from aws_cdk import core 
from provision.resources.vpc_stack import VpcStack
from constant.constant import STACKS_CONSTANTS

class Dep_vpc_Stack(core.Stack):
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
        
        #self.node.try_get_context(self.cfg)['log_config']
        # Fetching path for configs
        vpc_path = self.node.try_get_context(self.cfg)['vpc_config_europe']

         # Creating resources
        vpc = VpcStack.create_vpc(self, vpc_path)
