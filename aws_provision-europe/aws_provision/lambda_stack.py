from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_iam as _iam)
from provision.resources.job_lambda import JobLambda
from provision.resources.iam_job_role import JobIAmRole
from constant.constant import STACKS_CONSTANTS
from constant.constant import LAMBDA



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
        role_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.IAM_CONFIG]

        
        # Creating resources
        roles = JobIAmRole.createAll(self, role_path)
       # roles = IAMROLES.ROLES
        # Creating resources
        JobLambda.createAll(self,lambda_path,roles)
