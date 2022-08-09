from data_processor.logging.cloudwatch.log_utils import write_logs
from data_processor.steps.constant.constants import write_constants
class Write:
    """

    """
    def __init__(self):
        pass

    def execute(self, step_param):
        """

        :param step_param:
        """
        write_logs(write_constants.INFO,"Inside write .. ")
        path = step_param.step_config[write_constants.PARAMS][write_constants.PATH]
        write_logs(write_constants.INFO,"path - {}".format(path))
        overwrite = step_param.step_config[write_constants.PARAMS][write_constants.OVERWRITE]
        write_logs(write_constants.INFO,"overwrite - {}".format(overwrite))
        file_format = step_param.step_config[write_constants.PARAMS][write_constants.FORMAT]
        write_logs(write_constants.INFO,"file_format - {}".format(file_format))
        tble = step_param.step_config[write_constants.PARAMS][write_constants.DF]
        write_logs(write_constants.INFO,"tble - {}".format(tble))

        df = step_param.spark.sql("select * from {}".format(tble))
        write_logs(write_constants.INFO,"Df Created for write..")
        df.show()
        write_logs(write_constants.INFO,"type of overwrite - {}".format(type(overwrite)))
        if overwrite:
            write_logs(write_constants.INFO,"Writing Dataframe in overwrite mode.... ")
            df.show()
            df.coalesce(1).write.option("header", True).format(file_format).mode("overwrite").csv(path)
        else:
            write_logs(write_constants.INFO,"Writing Dataframe .... ")
            df.show()
            df.coalesce(1).write.option("header", True).format(file_format).csv(path)
        write_logs(write_constants.INFO,f"Step name: {step_param.step_config['step_name']} succesfully")
