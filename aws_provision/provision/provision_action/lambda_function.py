from aws_cdk import core, aws_lambda as _lambda
import json
from aws_cdk import aws_iam as _iam

class LambdaFunction(core.Stack):
    """

    """
    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        

    def create_lambda(self, function_name:str,path:str,iam_role):
        """ Creates lambda functions

        Args:
            function_name (str): name of lambda
            layer (LayerVersion): layer to be attached
            path(str): path to config

        Returns:
            Fucntion : returns lambda function created
        """        
        lambda_function_config = LambdaFunction.lambda_function_config(function_name,path)
        
    
        function = _lambda.Function(self, function_name,
                                    function_name=function_name,
                                    runtime=_lambda.Runtime.PYTHON_3_8,
                                    handler=lambda_function_config['handler'],
                                    code=_lambda.Code.from_asset(lambda_function_config['code_path']),
                                    role=iam_role,
                                    timeout=core.Duration.minutes(5))
        return function

    @staticmethod
    def lambda_function_config(lambda_function_name:str,path):
        """ Fetch config for lambda

        Args:
            lambda_function_name (str): name of function
            path(str): path of config

        Returns:
            dict: config for lambda
        """        
        with open(path) as f :
            lambdas_config = json.load(f)
        return lambdas_config[lambda_function_name]
