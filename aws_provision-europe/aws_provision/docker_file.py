import json
from constructs import Construct
from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_iam as _iam,
    aws_ecr_assets as ecr_assets,
    aws_ecr as ecr,
    )
import aws_cdk as core
from aws_cdk import core 

from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from constant.constant import STACKS_CONSTANTS
#from cdk_docker import ecs_config


class CdkDockerStack(core.Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """init class for Infra Stack
        Args:
            scope (core.Construct)
            id (str)
        """        
        env = kwargs[STACKS_CONSTANTS.ENV]
        super().__init__(scope, id, env=env)
        config = kwargs[STACKS_CONSTANTS.CONFIG]
        self.cfg = config
        path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.ECS_CONFIG]
        config_docker = ecs_config(path)
        

        #path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.ECS_CONFIG]
        

        fargate_task_definition = ecs.FargateTaskDefinition(self, config_docker["task_id"],
                                                        cpu=config_docker["cpu"],
                                                        memory_limit_mib=config_docker["memory_limit"])

        dock_image = ecr_assets.DockerImageAsset(self, config_docker["image_id"],
                                             directory=(config_docker["directory"])
                                             )
        image = ecs.ContainerImage.from_docker_image_asset(dock_image)

        container = fargate_task_definition.add_container(config_docker["container_name"],
                                                      image=image,
                                                      logging=ecs.LogDrivers.aws_logs(
                                                          stream_prefix=config_docker["stream_prefix"])
                                                      )
        #runAIObj = runaimlmodel(
       # self, fargate_task_definition, container, path)
    
   




#def runaimlmodel(self, Task_Def, Container_Def, path):
    """
    Create stepfunction for Preprocessing
            :param Fargate_Cluster:
            :param Task_Def:
            :param Container_Def:
            :return:
    """
    
   # path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.ECS_CONFIG]
    #platform_version = ecs.FargatePlatformVersion.LATEST
    #integrationPattern = sfn.IntegrationPattern.RUN_JOB
    # subnetid1 = ec2.Subnet.from_subnet_attributes(
    #     self, config["subnet_1"]["name"], availability_zone=config["subnet_1"]["zone"], subnet_id=config["subnet_1"]["subnet_id"])
    # subnetid2 = ec2.Subnet.from_subnet_attributes(
    #     self, config["subnet_2"]["name"], availability_zone=config["subnet_2"]["zone"], subnet_id=config["subnet_2"]["subnet_id"])

    #Step function task
    #runAIMLModel_job = sfn_tasks.EcsRunTask(
        #self, 'AIML_Model',
        #integration_pattern=integrationPattern,
        #task_definition=Task_Def,
        #assign_public_ip=True,
        #container_overrides=[sfn_tasks.ContainerOverride(
            #container_definition=Container_Def
        #)],
        # subnets=ec2.SubnetSelection(subnets=[subnetid1, subnetid2]),
        # security_groups=[ec2.SecurityGroup.from_security_group_id(
        #     self, ECS.SECURITY_GROUP["name"], security_group_id=ECS.SECURITY_GROUP["id"])],
        #launch_target=sfn_tasks.EcsFargateLaunchTarget(
           # platform_version=platform_version)
    #)
    #return runAIMLModel_job
 

def ecs_config(path):
        """ Fetches config for emr
     Returns:
        dict : config for emr
     """
    #Reading config file
        with open(path) as f:
            ecs_config = json.load(f)
        return ecs_config

