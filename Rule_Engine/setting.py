class Settings:
    AWS_CREDENTIALS = {
         "region_name": "us-east-1"
    }

    S3_DETAILS = {
        "RULE_ENGINE" : "/Rule_engine/",
        "bucket_name": "dep-qa",
        "input_folder_prefix": "Input",
        "rule_folder_prefix": "Rule/",
        "processed_folder_prefix": "Processed/",
        "output_valid_path": "Output/valid/",
        "output_invalid_path": "Output/invalid/",
        "jar_folder_path": "s3://cdep/rule_engine/jars/*",
        "file_extension": ['.txt', '.csv', '.json']
    }

    DYNAMODB_TABLE = {
        "job_table_name": "rule_engine_job"
    }

