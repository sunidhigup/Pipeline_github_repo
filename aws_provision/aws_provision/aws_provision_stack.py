# from aws_cdk import core

# from provision.resources.vpc_stack import VpcStack
# from provision.resources.job_security_group import JobSecurityGroup
# from provision.resources.iam_job_role import JobIAmRole
# from provision.resources.job_lambda import JobLambda
# from provision.resources.step_function import StepFunctionJob
# from provision.resources import EMR_stack
# from provision.resources import Kinesis_stack
# from provision.resources import Dynamo_stack
# from provision.resources import Secret_manager
# from provision.resources import Kinesis_Emr_trigger
# from provision.resources import ECS_stack
# from provision.resources.elastic_bean_stack import ElasticBeanstalk


# class AwsProvisionStack(core.Stack):
#     """

#     """
#     def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        
#         env = kwargs["env"]
#         super().__init__(scope, id,env=env)
#         config = kwargs["config"]
#         self.cfg=config

#         #Fetching path for configs
#         vpc_path = self.node.try_get_context(self.cfg)['vpc_config']
#         security_grp_path= self.node.try_get_context(self.cfg)['sc_group_config']
#         role_path= self.node.try_get_context(self.cfg)['iam_config']
#         lambda_path= self.node.try_get_context(self.cfg)['lambda_config']
#         step_path= self.node.try_get_context(self.cfg)['step_config']
#         dynamo_path= self.node.try_get_context(self.cfg)['dynamo_config']
#         emr_path= self.node.try_get_context(self.cfg)['emr_config']
#         secret_path= self.node.try_get_context(self.cfg)['secret_config']
#         kinesis_path = self.node.try_get_context(self.cfg)['kinesis_config']
#         ecs_path = self.node.try_get_context(self.cfg)["ecs_config"]
#         ebs_path = self.node.try_get_context(self.cfg)["ebs_config"]


#         #Creating resources
#         vpc = VpcStack.create_vpc(self,vpc_path)
#         # ECS_stack.createEcs(self,ecs_path,vpc)
#         JobSecurityGroup.createAll(self,security_grp_path)
#         JobIAmRole.createAll(self,role_path)
#         # JobLambda.createAll(self,lambda_path)
#         StepFunctionJob.createAll(self,step_path,lambda_path)
#         Dynamo_stack.create_dynamo(self,dynamo_path)
#         # EMR_stack.createEMR(self,emr_path)
#         Secret_manager.create_secret_manager(self,secret_path)
#         Kinesis_stack.createkinesis(self,kinesis_path)
#         # Kinesis_Emr_trigger.LambdaWithKinesisTrigger(self, kinesis_path)
#         ElasticBeanstalk.create_elastic_beanstalk(self,ebs_path)

