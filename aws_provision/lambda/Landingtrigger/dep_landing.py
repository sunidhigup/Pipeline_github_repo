import datetime
import json
import os
import urllib.parse

import boto3

from CDEP.aws_provision.constant.constant import lambdaConstants

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    file_metadata = {}
    ts = str(datetime.datetime.now())
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    copy_source = {
        'Bucket': bucket,
        'Key': key
    }

    # Get count of rows
    obj = s3.Object(bucket, key)
    file_contents = obj.get()["Body"].read()
    count = file_contents.decode('utf8').count('\n') - 1

    # Extracting client name
    full_name = key.split("/")[-1]  # gt_gl.csv
    file_name = full_name.split("_")[-1]
    table_name = file_name.split(".")[0]
    client_name = full_name.split("_")[0]

    destbucket = s3.Bucket('cdep-demo')
    dest_key = client_name + "/" + table_name + "/Incoming/" + file_name

    destbucket.copy(copy_source, dest_key)

    file_metadata["size"] = str(event['Records'][0]['s3']['object']['size'] / 1000) + "KB"
    file_metadata["Landing_path"] = bucket + "/" + key
    file_metadata["destination_key"] = dest_key
    file_metadata["destination_bucket"] = "cdep-demo"
    file_metadata["timestamp"] = ts

    file_metadata["id"] = client_name + "_" + table_name
    file_name = os.path.split(key)[1]
    ext = file_name.split(".")[-1]
    file_metadata["extension"] = ext
    file_metadata["Count"] = count
    file_metadata["Pattern"] = client_name + "*.csv"
    file_metadata["Skip_preprocessing"] = False
    file_metadata["file_state"] = "Pending"
    dynamodb.Table(lambdaConstants.FILE_CLASSIFICATION_TABLE_NAME).put_item(Item=file_metadata)

    batch_id = client_name + "~" + ts
    sfn_client = boto3.client('stepfunctions', region_name="us-east-1")

    state_machine_arn = 'arn:aws:states:us-east-1:955658629586:stateMachine:Cdep_preprocessor'
    response = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps({

            "rule_engine": True,
            "job_name": table_name,
            "client_name": client_name,
            "batch_id": batch_id}))
