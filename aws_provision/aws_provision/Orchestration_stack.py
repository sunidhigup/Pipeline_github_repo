import imp
from constant.constant import IAMROLES
from aws_cdk import core
from provision.resources.step_function import StepFunctionJob
from constant.constant import STACKS_CONSTANTS

class Dep_orchestration_Stack(core.Stack):
    """Stack creation for Orchestration

    Args:
        core (aws.core.Stack): Stack class from aws
    """    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        """init class for Orchestrationstack

        Args:
            scope (core.Construct)
            id (str)
        """        
        env = kwargs[STACKS_CONSTANTS.ENV]
        super().__init__(scope, id, env=env)
        config = kwargs[STACKS_CONSTANTS.CONFIG]
        self.cfg = config

        # Fetching path for configs
        lambda_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.LAMBDA_CONFIG]
        step_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.STEP_CONFIG]

        # Creating resources
        # JobLambda.createAll(self,lambda_path)
        roles = IAMROLES.ROLES
        StepFunctionJob.createAll(self, step_path, lambda_path, roles)
