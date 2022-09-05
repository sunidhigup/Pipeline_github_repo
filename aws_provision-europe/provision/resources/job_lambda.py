from re import L
from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from provision.provision_action.lambda_function import LambdaFunction
import json
from aws_cdk import aws_iam as _iam
from constant.constant import LAMBDA


class JobLambda(core.Stack):
    """

    """
    def __init__(self, scope: core.Construct, id: str, vpc=None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def createAll(self, path,roles):
        """ Creates lambdas one by one by calling another function
        Args:
            path (str): path of config

        Returns:
            dict: Lambda function in key value pair
        """        

        self.lambda_functions = {}
        lambdas_config = JobLambda.lambda_function_config(path)
        # iam_role = _iam.Role.from_role_arn(self, LAMBDA.ROLE_NAME, LAMBDA.ROLE_ARN,
        #                               mutable = False)

        iam_role = roles[LAMBDA.ROLE_NAME]

        # try:
        #     layer = _lambda.LayerVersion(self, LAMBDA.LAYER_ID,
        #                                 code=_lambda.Code.from_bucket(
        #                                     bucket=s3.Bucket.from_bucket_name(self, LAMBDA.LAYER_ID,
        #                                                                    LAMBDA.S3_BUCKET),
        #                                     key=LAMBDA.S3_PATH),
        #                                 compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
        #                                 layer_version_name=LAMBDA.LAYER_VERSION_NAME)
        # except:
        #     layer = _lambda.LayerVersion.from_layer_version_arn(self,LAMBDA.PANDA_LAYER,
        #                             layer_version_arn=LAMBDA.PANDA_ARN)

        #Creating lambdas
        for lambda_function_name in lambdas_config:
            
            self.lambda_functions[lambda_function_name] = LambdaFunction.create_lambda(self, lambda_function_name,path,iam_role)
        return self.lambda_functions  

    @staticmethod
    def lambda_function_config(path):
        """Fetches config for lambda

        Returns:
            dict: config for lambda
        """      
    #Reading config file  
        with open(path) as f:
            lambdas_config = json.load(f)
        return lambdas_config
