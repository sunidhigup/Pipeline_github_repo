import json

from aws_cdk import aws_s3 as s3


def create_bucket(self, path):
    """creates S3 Bucket

    Args:
        path (String): path to S3 config file

    Returns:
        bucket: S3 Bucket
    """

    # Read Config file
    s3config = s3_config(path)

    for bucket in s3config["buckets"]:
        # Set up a bucket
        bucket_name = bucket.setdefault('bucket_name', 'a')
        bucket = s3.Bucket(self, bucket_name)

    # return bucket


def s3_config(path):
    """Fetches config for S3

    Args:
        path (String): path to S3 config file

    Returns:
        Dictionary: Config for S3
    """
    # Reading config file
    with open(path, 'r') as f:
        s3_config = json.load(f)

    return s3_config
