from aws_cdk import core 
from aws_cdk import aws_ec2 as ec2
from provision.resources import ECS_stack
from provision.resources.iam_job_role import JobIAmRole
from constant.constant import STACKS_CONSTANTS
from constant.constant import STEPFUNCTION_ECS
from provision.resources.vpc_stack import VpcStack
from aws_cdk import aws_iam as iam

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
        role_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.ECS_SF_CONFIG]
        vpc_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.VPC_CONFIG]
    
        #Fetching VPC id
        vpc_test = ec2.Vpc.from_lookup(self, "vpc", vpc_name="dep-vpc-stack/Dep_vpc")
        #print (vp)
       
        
        #role = iam.Role.from_role_arn(self, "Role", "arn:aws:iam::955658629586:role/dep_emr_spark_role",
        # Set 'mutable' to 'false' to use the role as-is and prevent adding new
        # policies to it. The default is 'true', which means the role may be
        # modified as part of the deployment.
        #mutable=False
        #)

        #role= iam.from_role_arn(self,"Role","dep_emr_spark_role")
        #print (role)
        #role_arn=role.Irole
        #vpc_id = vpc_test.vpc_id
        # Creating resources

        roles = JobIAmRole.createAll(self, role_path)
        #vpc = VpcStack.create_vpc(self, vpc_path)
        ECS_stack.createEcs(self, ecs_path, vpc_test, roles)
