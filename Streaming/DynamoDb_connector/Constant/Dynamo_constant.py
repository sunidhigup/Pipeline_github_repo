from DynamoDb_connector.settings import Settings
import datetime 
from DynamoDb_connector.dml.read import get_stream_name

Kinesis = Settings.KINESIS
current_time = str(datetime.datetime.now())
stream_name= "dep_stream_table"
string_list=stream_name.split('_')
client_name=string_list[0]


class META_DICT:
    """
        Contains Dictionary containing metedata
    """    
    DICT = {
            "stream_name": stream_name,
            "client_name": client_name ,
            "timestamp": current_time,
            "isprocessing": "Yes",
            "isstorage": "Yes",
            "isanalytics": "No"
    }



class STATUS_DICT:
    """
        Contains Dictionary containing status of stream
    """    
    DICT = {
            "stream_name": stream_name,
            "status": Kinesis["status"],
            "timestamp": current_time
    }