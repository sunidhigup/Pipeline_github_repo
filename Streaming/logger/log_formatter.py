import datetime
import json


class LogFormatter:

    """
 
   
    """
    def __init__(self,
                 stream_name,
                 client_name,
                 phase,
                 source_rec_count,
                 target_record_count,
                 reject_record_count):
      
        self.log_timestamp = str(datetime.datetime.now())
        self.stream = stream_name
        self.client_name = client_name
        self.batch_type= "Daily"
        self.phase = phase
        self.source_rec_count = source_rec_count
        self.target_record_count = target_record_count
        self.reject_record_count = reject_record_count
        

    # method to return formatted string for logging
    def create_log(self):
        """
        Method to return formatted string for logging
        :return: Formatted log
        """
        return json.dumps(self.__dict__)
