import boto3
from secret_key import get_secret
from constant.constant import Input
import os
class Kinesis:
    """
    """    
    def __init__(self, region, stream_name):
        """
        Args:
            region (string)
            stream_name (string)
        """        
        self.region = region
        self.stream_name = stream_name
        self.service = Input.SERVICE_NAME


    def _create_kinesis_object(self):

        # access_key,secret_access_key = get_secret()
        kinesis_obj = boto3.client(self.service,aws_access_key_id = os.getenv('AWS_ACCESS_KEY'),
                                   aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
                                   region_name=self.region)
        return kinesis_obj
    

    def put_object(self, data):
        """

        :param data:
        """
        #Putting recoed in the object
        k_obj = self._create_kinesis_object()
        put_response = k_obj.put_records(StreamName=self.stream_name, Records=data)


