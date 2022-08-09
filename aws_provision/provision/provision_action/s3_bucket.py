from aws_cdk import core, aws_s3


class S3Bucket(core.Stack):
    """

    """
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def create(self, bucket_id, bucket_name):
        """

        :param bucket_id:
        :param bucket_name:
        :return:
        """
        bucket = aws_s3.Bucket(self, id=bucket_id, bucket_name=bucket_name)
        return bucket
