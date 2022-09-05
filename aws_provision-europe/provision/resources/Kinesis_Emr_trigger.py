# from aws_cdk import (
#     aws_lambda as lambda_,
#     aws_kinesis as kinesis,
#     aws_lambda_event_sources as event_sources,
#     core,
# )
# from provision.resources import Kinesis_stack
# import json
# import boto3
# from aws_cdk import aws_iam as _iam
# from constant.constant import LAMBDA
#
# def LambdaWithKinesisTrigger(self,path):
#     """
#         Use existing stream or create new one and adds lambda trigger to create EMR
#
#         Args:
#             path (str): path of config
#     """
#
#     with open("../job_steps/create_emr_cluster/handler.py", encoding="utf8") as fp:
#         handler_code = fp.read()
#
#
#     config= kinesis_config(path)
#     stream_name=config["name"]
#     # Creates reference to already existing kinesis stream
#     try:
#         kinesis_stream = kinesis.Stream.from_stream_arn(
#         self, 'KinesisStream',
#             core.Arn.format(
#             core.ArnComponents(
#                 resource='stream',
#                 service='kinesis',
#                 resource_name=stream_name
#              ),
#             self
#            )
#         )
#
#     #Create new stream
#     except:
#
#         kinesis_stream=Kinesis_stack.createkinesis(self,path)
#
#     iam_role = _iam.Role.from_role_arn(self, LAMBDA.ROLE_NAME,LAMBDA.ROLE_ARN,mutable = False)
#
#     #create lambda function
#     lambdaFn = lambda_.Function(
#         self, 'Singleton',
#         handler='index.lambda_handler',
#         role=iam_role,
#         code=lambda_.InlineCode(handler_code),
#         runtime=lambda_.Runtime.PYTHON_3_7,
#         timeout=core.Duration.seconds(300)
#     )
#
#     # Update Lambda Permissions To Use Stream
#     kinesis_stream.grant_read(lambdaFn)
#
#     # Create New Kinesis Event Source
#     kinesis_event_source = event_sources.KinesisEventSource(
#         stream=kinesis_stream,
#         starting_position=lambda_.StartingPosition.LATEST,
#         batch_size=1
#     )
#
#     # Attach New Event Source To Lambda
#     lambdaFn.add_event_source(kinesis_event_source)
#     stream_json=to_json(stream_name)
#     s3_data(stream_json)
#
# def to_json(streamname):
#     """
#
#     :param streamname:
#     :return:
#     """
#     dic = {"stream_name" : streamname}
#     # json_object = json.dumps(dic, indent = 4)
#     name="stream_name.json"
#     with open(name, "w") as outfile:
#         json.dump(dic, outfile)
#     return name
#
# def s3_data(stream_json):
#     """
#
#     :param stream_json:
#     """
#     s3 = boto3.client('s3')
#     bucket_name = "cdep"
#     s3.upload_file(stream_json, bucket_name,'emr/'+ stream_json)
#     # s3.put_object(Bucket=bucket_name, Key=(streamname+'/'))
#
#
# def kinesis_config(path):
#     """ Fetches config for Kinesis
#
#     Returns:
#         dict : config for KInesis
#     """
#     with open(path) as f:
#         kinesis_config = json.load(f)
#
#     return kinesis_config
#
#
#