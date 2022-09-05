from aws_cdk import core
from provision.resources import ECS_stack
from provision.resources.iam_job_role import JobIAmRole
from constant.constant import STACKS_CONSTANTS
from provision.resources.vpc_stack import VpcStack


class Dep_ECS_Stack(core.Stack):
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

         # Fetching path for configs
        ecs_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.ECS_CONFIG]
        role_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.IAM_CONFIG]
        vpc_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.VPC_CONFIG]

        # Creating resources
        roles = JobIAmRole.createAll(self, role_path)
        vpc = VpcStack.create_vpc(self, vpc_path)
        ECS_stack.createEcs(self, ecs_path, vpc, roles)
