import json
from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_iam as _iam,
    aws_ecr_assets as ecr_assets,
    aws_ecr as ecr,
    core
)
from constant.constant import ECS
from constant.constant import STEPFUNCTION

from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks


def createEcs(self, path, Vpc,roles):
    """
    Create ecs image and push to repo
    :param path: config path
    :param Vpc: Vpc to be attached
    :return:
    """
    config = ecs_config(path)
    # iam_role_for_stepfunction = _iam.Role.from_role_arn(
    #     self, STEPFUNCTION.ROLE_NAME, STEPFUNCTION.ROLE_ARN, mutable=False)
    # iam_role_for_stepfunction = roles[STEPFUNCTION.ROLE_NAME]
    iam_role_for_stepfunction = roles[STEPFUNCTION.ROLE_NAME]

    # execution_role = _iam.Role.from_role_arn(
    #     self, ECS.EXEC_ROLE_NAME, ECS.EXEC_ROLE_ARN, mutable=False)
    # task_role = _iam.Role.from_role_arn(
    #     self, ECS.TASK_ROLE_NAME, ECS.TASK_ROLE_ARN, mutable=False)

    cluster = ecs.Cluster(self, config["cluster_id"],
                          cluster_name=config["cluster_name"], vpc=Vpc)

    fargate_task_definition = ecs.FargateTaskDefinition(self, config["task_id"],
                                                        cpu=config["cpu"],
                                                        memory_limit_mib=config["memory_limit"]
                                                        # task_role=task_role,
                                                        # execution_role=execution_role
                                                        )

    # repository = ecr.Repository.from_repository_arn(
    #     self, ECS.REPO_NAME, ECS.REPO_ARN)
  
    # repository = ecr.Repository(self, ECS.REPO_NAME,
    #     image_scan_on_push=True
    # )
    dock_image = ecr_assets.DockerImageAsset(self, config["image_id"],
                                             directory=(config["directory"])
                                             )
    image = ecs.ContainerImage.from_docker_image_asset(dock_image)
    # image = ecs.ContainerImage.from_ecr_repository(
    #     repository=repository, tag=config["image_tag"])

    container = fargate_task_definition.add_container(config["container_name"],
                                                      image=image,
                                                      logging=ecs.LogDrivers.aws_logs(
                                                          stream_prefix=config["stream_prefix"])
                                                      )

    runAIObj = runaimlmodel(
        self, cluster, fargate_task_definition, container, path)
    containerFailed_job = sfn.Fail(
        self, ECS.TASK_FAIL["id"],
        cause=ECS.TASK_FAIL["cause"],
        error=ECS.TASK_FAIL["error"]
    )
    runaimlmodel_job = runAIObj.add_catch(
        errors=["States.ALL"], handler=containerFailed_job)
    definition = runaimlmodel_job

    sfn.StateMachine(
        self, config["step_id"],
        state_machine_name=config["step_name"],
        definition=definition,
        timeout=core.Duration.seconds(config["timeout"]),
        role=iam_role_for_stepfunction
    )

    return cluster, fargate_task_definition, container


def runaimlmodel(self, Fargate_Cluster, Task_Def, Container_Def, path):
    """
    Create stepfunction for Preprocessing
            :param Fargate_Cluster:
            :param Task_Def:
            :param Container_Def:
            :return:
    """
    config = ecs_config(path)

    platform_version = ecs.FargatePlatformVersion.LATEST
    integrationPattern = sfn.IntegrationPattern.RUN_JOB
    # subnetid1 = ec2.Subnet.from_subnet_attributes(
    #     self, config["subnet_1"]["name"], availability_zone=config["subnet_1"]["zone"], subnet_id=config["subnet_1"]["subnet_id"])
    # subnetid2 = ec2.Subnet.from_subnet_attributes(
    #     self, config["subnet_2"]["name"], availability_zone=config["subnet_2"]["zone"], subnet_id=config["subnet_2"]["subnet_id"])

    #Step function task
    runAIMLModel_job = sfn_tasks.EcsRunTask(
        self, 'AIML_Model',
        integration_pattern=integrationPattern,
        cluster=Fargate_Cluster,
        task_definition=Task_Def,
        assign_public_ip=True,
        container_overrides=[sfn_tasks.ContainerOverride(
            container_definition=Container_Def
        )],
        # subnets=ec2.SubnetSelection(subnets=[subnetid1, subnetid2]),
        # security_groups=[ec2.SecurityGroup.from_security_group_id(
        #     self, ECS.SECURITY_GROUP["name"], security_group_id=ECS.SECURITY_GROUP["id"])],
        launch_target=sfn_tasks.EcsFargateLaunchTarget(
            platform_version=platform_version)
    )
    return runAIMLModel_job

def ecs_config(path):
    """ Fetches config for emr

    Returns:
        dict : config for emr
    """
    #Reading config file
    with open(path) as f:
        ecs_config = json.load(f)
    return ecs_config
