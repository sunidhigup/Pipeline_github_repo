class StepParam:
    """

    """
    def __init__(self, spark, process_config):
        self.transform_config = process_config
        self.step_config = None
        self.spark = spark
        self.data_frame = None
        self.job_dict = None
        self.batch_id = None
        self.dynamoDb = None
        self.step_number = None
        self.step_name = None
        self.logger = None
        self.execution_id = None
        self.batch_name = None
        self.client_name = None
        self.table_name = None
        self.region_name = None
        self.profile_env = None
        self.profile_env_bucket = None
        self.bucket = None
        self.jar_folder_path = None
        self.job_status_table = None
        self.audit_table = None
        self.extension = None
        self.log_group = None
        self.extensions = None
        self.db_status_table = None
        self.df = None
        self.db_name = None
