from aws_cdk import core
from provision.resources import s3_job_bucket
from constant.constant import STACKS_CONSTANTS


class S3_Stack(core.Stack):
    """Creates S3 Bucket

    Args:
        core (aws_cdk.core.stack): inherited object of aws_cdk.core.stack class
    """

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        """init class for S3 Stack

        Args:
            scope (core.Construct)
            id (str)
        """        
        
        env = kwargs[STACKS_CONSTANTS.ENV]
        super().__init__(scope, id, env=env)
        config = kwargs[STACKS_CONSTANTS.CONFIG]
        self.cfg = config

        # Fetching path for configs
        s3_path = self.node.try_get_context(self.cfg)[STACKS_CONSTANTS.S3_STACK]
        

        # Creating resources
        s3_job_bucket.create_bucket(self, s3_path)
