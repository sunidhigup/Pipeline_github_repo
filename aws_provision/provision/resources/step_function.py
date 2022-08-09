from aws_cdk import core
from provision.provision_action.step_function import StepFunction
from provision.resources.job_lambda import JobLambda
import json
from constant.constant import STEPFUNCTION

class StepFunctionJob(core.Stack):
    """

    Args:
        core (core.aws.Stack): Stack class from AWS
    """    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def createAll(self, path,lambda_path,roles):
        """
            Creates step function one by one by calling another function
            Args:
                path (str): path of config
        """        
        
        step_functions_config = StepFunctionJob.step_function_config(path)
        step_functions_definitions = StepFunctionJob.step_definitions(self,path,lambda_path,roles)
        
        
        #creating stepfunction
        for step_function_name in step_functions_config:
            
            role = roles[STEPFUNCTION.ROLE_NAME].role_arn
            StepFunction.create_step_function(self, step_function_name, step_functions_definitions[step_function_name],role)

    def step_definitions(self,path,lambda_path,roles):
        """
            Generates definition for each stepfunction
        Returns:
            dict: definitions of stepfunctions in key value pair
        """        
        lambda_functions= JobLambda.createAll(self,lambda_path,roles)
        step_functions_definitions = {}
        step_functions_config = StepFunctionJob.step_function_config(path)
        for step_function_name in step_functions_config:
            
            for tasks in step_functions_config[step_function_name]["States"]:
                try:

                    if lambda_functions[step_functions_config[step_function_name]["States"][tasks]["Parameters"]["FunctionName"]]:
                        step_functions_config[step_function_name]["States"][tasks]["Parameters"]["FunctionName"] = lambda_functions[step_functions_config[step_function_name]["States"][tasks]["Parameters"]["FunctionName"]].function_arn
                except:
                    pass
            
            step_functions_definitions[step_function_name]=step_functions_config[step_function_name]
        return step_functions_definitions

    @staticmethod
    def step_function_config(path):
        """
            Fetches config for stepfunction
        Returns:
            dict : config for stepfunction
        """     
        #Reading config file   
        with open(path) as f:
            steps_functions_config = json.load(f)
        return steps_functions_config



  