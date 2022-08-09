import zipfile
from io import BytesIO
from constant.Constant import extract_constants
from constant import Constant
from Boto3_client.dynamo_writer import get_dynamodb
from Boto3_client.s3client import get_s3

dynamodb = get_dynamodb()


def extract(meta_data):
    """

    :param meta_data:
    :param client_name:
    :param name:
    :param item:
    :param bucket:
    :param ts:
    """
    s3 = get_s3()
    bucket = meta_data["destination_bucket"]
    item = meta_data["destination_key"]
    client_name = meta_data["Client_name"]
    batch_name = meta_data["Batch_name"]
    table_name = meta_data["Table_name"]

    zip_obj = s3.Object(bucket_name=bucket, key=item)
    buffer = BytesIO(zip_obj.get()["Body"].read())
    meta_data[extract_constants.OPT_PERF] = "Unzipped"
    meta_data["Status"] = "Processed"
    z = zipfile.ZipFile(buffer)

    for filename in z.namelist():
        s3.meta.client.upload_fileobj(
            z.open(filename),
            Bucket=bucket,
            Key=client_name + extract_constants.SLASH + batch_name + extract_constants.SLASH + table_name + extract_constants.SLASH + 
                        extract_constants.RULE_ENGINE + extract_constants.SLASH + extract_constants.INPUT + extract_constants.SLASH + f'{filename}')
    dynamodb.Table(Constant.STATUS_TABLE_NAME).put_item(Item=meta_data)
    buffer.close()
