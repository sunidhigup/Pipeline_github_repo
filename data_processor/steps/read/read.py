import datetime

from data_processor.constants import Constants
from data_processor.logging.cloudwatch.log_utils import write_logs
from data_processor.steps.constant.constants import steps_constants


class Read:
    def execute(self, step_param):
        """

        :param step_param: contains 3 sub paramters step_config(for that particular step), transform_config(full transformation
                        data_frame object and spark_session object)

        Extract the db name the sql query from the step config and execute it against the spark_session created, and
        return the transformed dataframe for further processing

        :return:
        """
        # Further implement the logic to check if the path of sql is provided then open that file and run the sql
        self.process_data(step_param)

    def process_data(self, step_param):
        """

        :param step_param:
        """
        write_logs(steps_constants.INFO, "Inside Read .. ")
        write_logs(steps_constants.INFO, "Inside Read Definitions - {} ".format(
            step_param.step_config[Constants.EXEC_SQL_PARAMS][Constants.EXEC_SQL_DEFINITIONS]))
        job_step_status_table = Constants.job_step_status_table
        for definition in step_param.step_config[Constants.EXEC_SQL_PARAMS][Constants.EXEC_SQL_DEFINITIONS]:
            step_param.step_number = definition[Constants.EXEC_SQL_STEP_NUMBER]
            step_param.step_name = definition[Constants.EXEC_SQL_STEP_NAME]
            write_logs(steps_constants.INFO, "Step Number: {}".format(definition[Constants.EXEC_SQL_STEP_NUMBER]),
                       step_param)
            write_logs(steps_constants.INFO,
                       "Step name inside Read : {}".format(definition[Constants.EXEC_SQL_STEP_NAME]),
                       step_param)

            step_param.job_dict[steps_constants.BATCH_ID] = "{}{}{}" \
                .format(step_param.batch_id, step_param.step_number, step_param.step_name)
            step_param.job_dict[steps_constants.STEP_NUMBER] = definition[Constants.EXEC_SQL_STEP_NUMBER]
            step_param.job_dict[steps_constants.STEP_NAME] = definition[Constants.EXEC_SQL_STEP_NAME]
            step_param.job_dict[steps_constants.START_TIME] = str(datetime.datetime.now())
            step_param.job_dict[steps_constants.STATUS] = steps_constants.STATUS_RUNNING

            step_param.dynamoDb.Table(job_step_status_table).put_item(Item=step_param.job_dict)

            read_format = definition[Constants.READ_FORMAT]
            temp_view = definition[Constants.EXEC_SQL_TEMP_VIEW]
            persist_flag = definition[Constants.EXEC_SQL_PERSIST]
            persist_type = definition[Constants.EXEC_SQL_PERSIST_TYPE]
            # action = definition[Constants.EXEC_SQL_ACTION]
            action = ""
            Databases = Constants.DATABASES
            write_logs(steps_constants.INFO, "Read from path with format {}".format(read_format), step_param)
            try:
                if read_format in Databases:

                    database_name = definition[Constants.DB_NAME]
                    table_name = definition[Constants.TABLE_NAME]
                    df = eval(read_format).connect(step_param, database_name, table_name)

                else:
                    path = definition[Constants.READ_PATH]
                    df = step_param.spark.read \
                        .format(read_format) \
                        .option("header", True) \
                        .load(path)
                        # .option("inferSchema", "true") \
                        # .load(path)
            except Exception as error:

                step_param.job_dict[steps_constants.END_TIME] = str(datetime.datetime.now())
                step_param.job_dict[steps_constants.ERROR_DETAIL] = error
                step_param.job_dict[steps_constants.STATUS] = steps_constants.STATUS_FAILED
                step_param.dynamoDb.Table(job_step_status_table).put_item(Item=step_param.job_dict)

            write_logs(steps_constants.INFO, "Read Success", step_param)
            df.createOrReplaceTempView(temp_view)
            # if persist_flag.casefold() == "true":
            #     write_logs("Info", "Persisting DF with persist type {}".format(persist_type), step_param)
            #     # Make a separate file for storage
            #     level = StorageLevel.getStorageLevel(self, persist_type)
            #     df.persist(level)
            # Add else
            # if action != "":
            #     write_logs("Info", "Executing Action : {}".format(action), step_param)
            #     Actions.getAction(self, action, df)

            step_param.job_dict[steps_constants.END_TIME] = str(datetime.datetime.now())
            step_param.job_dict[steps_constants.STATUS] = steps_constants.STATUS_COMPLETED

            step_param.dynamoDb.Table(job_step_status_table).put_item(Item=step_param.job_dict)
