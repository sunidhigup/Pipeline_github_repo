from re import sub
from unicodedata import name
from aws_cdk import core
from aws_cdk import aws_ec2 as ec2
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

        vpc = ec2.Vpc.from_lookup(self, "vpc", vpc_name="dep-vpc-stack/Dep_vpc")
        print (vpc.vpc_id)
        selection = vpc.select_subnets(
         subnet_type=ec2.SubnetType.PUBLIC)
         #c2.subnet_ids)
        #subnets = vpc.select_subnets("*")
        print (selection.subnet_ids[0])
        subnet_id=selection.subnet_ids[0] 
        EMR_stack.createEMR(self,emr_path,subnet_id)

