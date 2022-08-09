class Settings:
    AWS_CREDENTIALS = {
       
        "region": "us-east-1",
        "endpointUrl": "kinesis.us-east-1.amazonaws.com",
        "startingposition": "latest"
    }

    KINESIS = {
        "bucket": "cdep",
        "path": "emr/stream_name.json",
        "status": "Processing"
        }
    DYNAMO = {
                "stream_meta_data":"dep_stream_metadata",
                "stream_status":"dep_stream_status",
                "streaming_table": "cdep_stream_data"
                }
    SECRET_NAME = "dep_aws_credentials",
    PROFILE_NAME = "cdep"
    LOG_STREAM = "Kinesis/CDEP"
    region_name="us-east-1"

   
    
    
