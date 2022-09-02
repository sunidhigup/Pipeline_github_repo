from aws_cdk import core
from provision.resources import EMR_stack
from constant.constant import STACKS_CONSTANTS


class Dep_EMR_Stack(core.Stack):
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


        emr_path = self.node.try_get_context(self.cfg)['emr_config']

        EMR_stack.createEMR(self, emr_path)

