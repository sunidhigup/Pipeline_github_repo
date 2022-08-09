# class EMR:
#     """
#      Contains all the constant used
#     """    
#     CLASSIFICATION = ["spark-env","export","spark"]
#     PYSPARK_PYTHON = "/usr/bin/python3"
#     PYSPARK_DRIVER_PYTHON = "/usr/bin/python3"
#     ResourceAllocation = "true"

class LAMBDA:
    LAYER_ID = "functional-dependecy"
    LAYER_VERSION_NAME = "functional-dependecy-layer"
    S3_BUCKET="customer360generic"
    S3_PATH= "raw/function-dependency.zip"
    ROLE_NAME = "dep_emr_spark_trigger-role"
    ROLE_ARN="arn:aws:iam::955658629586:role/service-role/dep_emr_spark_trigger-role-urgun2up"
    PANDA_LAYER='Pandas_numpy'
    PANDA_ARN='arn:aws:lambda:us-east-1:955658629586:layer:Pandas_numpy:1'

class STEPFUNCTION:
    ROLE_NAME= "StepFunctions-Resource_management-role"
    ROLE_ARN="arn:aws:iam::955658629586:role/service-role/StepFunctions-Cdep_resource_management-role-3afb1986"

class SECURITYGROUP:
    GROUP_ID="sg-034ffd1fd6650c42c"
    ID= "endpoint-sg-cluster"

class ECS:
    EXEC_ROLE_NAME = "execution_role"
    EXEC_ROLE_ARN = "arn:aws:iam::955658629586:role/ecsTaskExecutionRole"
    TASK_ROLE_NAME = "task_role"
    TASK_ROLE_ARN = "arn:aws:iam::955658629586:role/ECS_TASK_ROLE"
    REPO_NAME = "cdep"
    REPO_ARN = "arn:aws:ecr:us-east-1:955658629586:repository/cdep"
    TASK_FAIL = {
        "id":"ContainerFailed",
        "cause":"Access Keys Expired",
        "error":"Container Failed"
    }
    SECURITY_GROUP = {
        "name":"endpoint-sg-cluster1",
        "id":"sg-034ffd1fd6650c42c"
    }

class IAMROLES:
    ROLES = {}

class STACKS_CONSTANTS:
    ENV = "env"
    CONFIG = "config"
    DYNAMO_CONFIG = "dynamo_config"
    SECRET_CONFIG = "secret_config"
    VPC_CONFIG = "vpc_config"
    SC_GROUP_CONFIG = "sc_group_config"
    ECS_CONFIG = "ecs_config"
    EBS_CONFIG = "ebs_config"
    IAM_CONFIG = "iam_config"
    LAMBDA_CONFIG = "lambda_config"
    STEP_CONFIG = "step_config"
    S3_STACK = "s3_stack"
    FILE_CLASSIFICATION_TABLE_NAME: str = "dep_file_classification"

# class DATBASE_STACK_CONSTANT:
#     ENV = "env"
#     CONFIG = "config"
#     DYNAMO_CONFIG = "dynamo_config"
#     SECRET_CONFIG = "secret_config"


# class INFRA_STACK_CONSTANT:
#     ENV = "env"
#     CONFIG = "config"
#     VPC_CONFIG = "vpc_config"
#     SC_GROUP_CONFIG = "sc_group_config"
#     ECS_CONFIG = "ecs_config"
#     EBS_CONFIG = "ebs_config"
#     IAM_CONFIG = "iam_config"
#     LAMBDA_CONFIG = "lambda_config"
#     STEP_CONFIG = "step_config"


# class ORCHESTRATION_STACK_CONSTANT:
#     ENV = "env"
#     CONFIG = "config"
#     LAMBDA_CONFIG = "lambda_config"
#     STEP_CONFIG = "step_config"


# class ROLES_STACK_CONSTANT:
#     ENV = "env"
#     CONFIG = "config"
#     IAM_CONFIG = "iam_config"


# class S3_CONSTANT:
#     ENV = "env"
#     CONFIG = "config"
#     S3_STACK = "s3_stack"
# class lambdaConstants:
#     FILE_CLASSIFICATION_TABLE_NAME: str = "dep_file_classification"

