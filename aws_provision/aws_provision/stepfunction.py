from aws_cdk import core
from provision.resources.iam_job_role import JobIAmRole
from provision.resources.step_function import StepFunctionJob
from constant.constant import STACKS_CONSTANTS
from provision.resources.job_lambda import JobLambda

class Dep_stepfunction_Stack(core.Stack):
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



        step_path= self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.STEP_CONFIG]
        role_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.IAM_CONFIG]
        lambda_path= self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.LAMBDA_CONFIG]

        # Creating resources
        roles = JobIAmRole.createAll(self, role_path)
        StepFunctionJob.createAll(self, step_path, lambda_path, roles)
