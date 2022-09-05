from aws_cdk import core
from provision.resources import ECS_stack
from provision.resources import Log_Stack
from provision.resources.iam_job_role import JobIAmRole
from provision.resources.step_function import StepFunctionJob
from provision.resources.vpc_stack import VpcStack
from provision.resources import ECS_stack
from constant.constant import STACKS_CONSTANTS


# from provision.resources import SQS_Stack

class Dep_infra_Stack(core.Stack):
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
        vpc_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.VPC_CONFIG_EUROPE]
        #vpc_path_europe = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.VPC_CONFIG_EUROPE]
        security_grp_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.SC_GROUP_CONFIG]
        ecs_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.ECS_CONFIG]
        ebs_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.EBS_CONFIG]
        role_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.IAM_CONFIG]
        lambda_path= self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.LAMBDA_CONFIG]
        step_path= self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.STEP_CONFIG]
        sqs_path = self.node.try_get_context(self.cfg)['sqs_config']
        log_path = self.node.try_get_context(self.cfg)['log_config']

        # Creating resources
        roles = JobIAmRole.createAll(self, role_path)
        # Creating resources
        #vpc = VpcStack.create_vpc(self, vpc_path)
        #ECS_stack.createEcs(self, ecs_path, vpc, roles)
        # JobSecurityGroup.createAll(self,security_grp_path)

        # Creating resources
        # JobLambda.createAll(self,lambda_path)
        # roles = IAMROLES.ROLES
        StepFunctionJob.createAll(self, step_path, lambda_path, roles)
        # ElasticBeanstalk.create_elastic_beanstalk(self,ebs_path)

        # Creating resources
        # SQS_Stack.create_sqs(self,sqs_path)

        # Creating resources
        Log_Stack.create_logs(self, log_path)
