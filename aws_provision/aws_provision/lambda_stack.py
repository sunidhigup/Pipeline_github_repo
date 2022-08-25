from aws_cdk import core
from constant.constant import IAMROLES
from provision.resources.job_lambda import JobLambda
from constant.constant import STACKS_CONSTANTS


class Dep_lambda_stack(core.Stack):
    """Stack creation of lambda

    Args:
        core (aws.core.Stack): Stack class from aws
    """    

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        """init class for lambda Stack

        Args:
            scope (core.Construct)
            id (str)
        """        
        env = kwargs[STACKS_CONSTANTS.ENV]
        super().__init__(scope, id, env=env)
        config = kwargs[STACKS_CONSTANTS.CONFIG]
        self.cfg = config
    
        lambda_path= self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.LAMBDA_CONFIG]

        # Creating resources
        roles = IAMROLES.ROLES
        # Creating resources
        lambda_functions= JobLambda.createAll(self,lambda_path,roles)
