import datetime
import json

batch_id = None
client_name = None
phase = None
json_location = None
status = None
batch_type = None


class LogFormatter:
    """
    This class is used as formatter for string log values.
    :param level: INFO, ERROR
    :param file_name: name of the file
    :param file_size: size of the file
    :param source_rec_count: number of records in source file
    :param target_record_count: number of records in target file
    :param reject_record_count: number of rejected records
    :param step: StepEnum value corresponding to log step
    :param status_cd:  0 for Success, 1 for Error
    :param status_message: status message
    """

    def __init__(self,
                 level,
                 step_number=None,
                 step_name=None,
                 msg=None,
                 query=None,
                 count=None
                 ):
        self.log_timestamp = str(datetime.datetime.now())
        self.level = level
        self.batch_id = batch_id
        self.client_name = client_name
        self.step_number = step_number
        self.step_name = step_name
        self.batch_type = batch_type
        self.phase = phase
        self.json_location = json_location
        self.query = query
        self.count = count
        self.status = status
        self.msg = msg

    # method to return formatted string for logging
    def create_log(self):
        """
        Method to return formatted string for logging
        :return: Formatted log
        """
        return json.dumps(self.__dict__)
