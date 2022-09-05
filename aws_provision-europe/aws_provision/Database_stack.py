from sqlite3 import DatabaseError
from aws_cdk import core
from provision.resources import Dynamo_stack
from provision.resources import Secret_manager
from constant.constant import STACKS_CONSTANTS

class Dep_DB_Stack(core.Stack):
    """Stack creation for DB

    Args:
        core (aws.core.Stack): Stack class from aws
    """    

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        """init class for DB_Stack

        Args:
            scope (core.Construct)
            id (str)
        """        
        env = kwargs[STACKS_CONSTANTS.ENV]
        super().__init__(scope, id, env=env)
        config = kwargs[STACKS_CONSTANTS.CONFIG]
        self.cfg = config

        # Fetching path for configs
        dynamo_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.DYNAMO_CONFIG]
        secret_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.SECRET_CONFIG]

        # Creating resources
        Dynamo_stack.create_dynamo(self, dynamo_path)
        Secret_manager.create_secret_manager(self, secret_path)
