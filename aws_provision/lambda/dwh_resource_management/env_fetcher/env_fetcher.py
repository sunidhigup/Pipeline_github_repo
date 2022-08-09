import json
import boto3
from   logger.helper_functions import log_initiator
from   logger.func_write_log import write_logs
def read_config(PROFILE_ENV, BUCKETNAME, KEYNAME):
    """the function is used to read the config file stored in s3 bucket

    Args:
        PROFILE_ENV(str): profile - dev/prod/qa
        BUCKETNAME (str): Name of S3 Bucket. 
        KEYNAME (str): The Object Name which refers to the config file name. 

    Returns:
        dictionary: Config 
    """      
    try:
        #Creating client for S3
        s3_conn = boto3.client('s3')
        
        #Downloading and Reading Config file
        result = s3_conn.get_object(Bucket=BUCKETNAME, Key=KEYNAME)
        text = result["Body"].read().decode('utf-8')
        json_obj = json.loads(text)

    except Exception as e:
        write_logs("ERROR", "ERROR CAUGHT - {}".format(str(e)))
        raise e
    
    return json_obj[PROFILE_ENV]
    
    
