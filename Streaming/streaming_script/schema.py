from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, DateType, DoubleType
from streaming_script.data_type_convertor import DataType
from DynamoDb_connector.settings import Settings
from DynamoDb_connector.secret_key import get_secret
import json
import boto3
from Streaming.env_fetcher import read_config

def DataStruct():
        """[Inputs json file having EMP Data]

        Returns:
            [pyspark StructType]: struct1
        """
        config = read_config("dev","depconfig","Streaming/Config/config.json")

        path = config["schema_path"]
        schema_json = get_schema(path)
        dic = schema_json['fields']
        struct_field_ls = []
        for obj in dic:
            struct_field_ls.append(StructField(obj["fieldname"], DataType.toDataType(obj["type"])))

        schema = StructType(struct_field_ls)

        return schema

def get_schema(path):
    """ Reads json from s3 and returns schema

    Returns:
        string: nam of kinesis stream
    """    
    AWS_CREDENTIALS = Settings.AWS_CREDENTIALS
    Kinesis = Settings.KINESIS

    BUCKET = Kinesis["bucket"]
    FILE_TO_READ = path
    access_key , secret_access_key = get_secret()
    region = AWS_CREDENTIALS['region']
   
    client = boto3.client('s3',
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_access_key,
                        region_name=region
                        )
    result = client.get_object(Bucket=BUCKET, Key=FILE_TO_READ) 
    text = result["Body"].read().decode('utf-8')
    json_obj = json.loads(text)
    return json_obj