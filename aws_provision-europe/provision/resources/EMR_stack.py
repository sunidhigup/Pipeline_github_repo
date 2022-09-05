from aws_cdk import aws_iam as iam, core, aws_emr as emr
from aws_cdk import aws_s3 as _s3
from constant.constant import EMR
import json


def createEMR(self,path,subnet_id):
    """
     Creates new EMR cluster
        Args:
            path (str): path of config
    """
    
    #config for emr
    config = emr_config(path)
    
    #bucket for logs
    s3_log_bucket = _s3.Bucket(self, "s3bucket_logs")

    # emr service role
    emr_service_role = iam.Role(
        self,
        config["service_role"]["name"],
        assumed_by=iam.ServicePrincipal(
            config["service_role"]["assumed_by"]),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                config["service_role"]["policy"]
            )
        ]
        
    )

    # create emr cluster
    emr.CfnCluster(
        self,
        config["EMR"]["id"],
        instances=emr.CfnCluster.JobFlowInstancesConfigProperty(
            # To create core node
            #    core_instance_group=emr.CfnCluster.InstanceGroupConfigProperty(
            #        instance_count=0, instance_type="m4.large", market="SPOT"
            # ),
            ec2_subnet_id=subnet_id,
            #config["EMR"]["subnet_id"],
            hadoop_version=config["EMR"]["hadoop_ver"],
            keep_job_flow_alive_when_no_steps=config["EMR"]["cluster_alive_status"],
            #To create master node
            master_instance_group=emr.CfnCluster.InstanceGroupConfigProperty(
                instance_count=config["EMR"]["master_config"]["count"], instance_type=config[
                    "EMR"]["master_config"]["type"], market=config["EMR"]["master_config"]["market"]
            ),
        ),

        job_flow_role=config["EMR"]["job_flow_role"],
        name=config["EMR"]["name"],
        applications=[emr.CfnCluster.ApplicationProperty(
            name=config["EMR"]["application"])],
        service_role=emr_service_role.role_name,
        configurations=[
            # use python3 for pyspark
            emr.CfnCluster.ConfigurationProperty(
                # classification="spark-env",
                classification=EMR.CLASSIFICATION[0],
                configurations=[
                    emr.CfnCluster.ConfigurationProperty(
                        classification=EMR.CLASSIFICATION[1],
                        configuration_properties={
                            "PYSPARK_PYTHON": EMR.PYSPARK_PYTHON,
                            "PYSPARK_DRIVER_PYTHON": EMR.PYSPARK_DRIVER_PYTHON,
                        },
                    )
                ],
            ),

            emr.CfnCluster.ConfigurationProperty(
                classification=EMR.CLASSIFICATION[2],
                configuration_properties={
                    "maximizeResourceAllocation": EMR.ResourceAllocation},
            ),
        ],
        log_uri=f"s3://{s3_log_bucket}/{core.Aws.REGION}/elasticmapreduce/",
        release_label=config["EMR"]["version"],
        visible_to_all_users=False,

    )


def emr_config(path):
    """ Fetches config for emr

    Returns:
        dict : config for emr
    """    
    #Readinf config file
    with open(path) as f:
        emr_config = json.load(f)
    return emr_config
