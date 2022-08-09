import datetime

from data_processor.constants import Constants
from data_processor.logging.cloudwatch.log_utils import write_logs
from data_processor.utils.actions import Actions
from data_processor.utils.storage_level import StorageLevel



from data_processor.steps.constant.constants import steps_constants

class ExecuteSQL:

    def execute(self, step_param):
        """

        :param step_param: contains 3 sub paramters step_config(for that particular step), transform_config(full transformation
                        data_frame object and spark_session object)

        Extract the db name the sql query from the step config and execute it against the spark_session created, and
        return the transformed dataframe for further processing

        :return:
        """
        # Further implement the logic to check if the path of sql is provided then open that file and run the sql
        step_param.data_frame = self.process_data(step_param)

    def process_data(self, step_param):
        """

        :param step_param:
        :return:
        """
        spark_session = step_param.spark
        job_step_status_table = Constants.job_step_status_table
        # Read from a constant file
        for definition in step_param.step_config[Constants.EXEC_SQL_PARAMS][Constants.EXEC_SQL_DEFINITIONS]:
            step_param.step_number = definition[Constants.EXEC_SQL_STEP_NUMBER]
            step_param.step_name = definition[Constants.EXEC_SQL_STEP_NAME]
            write_logs(steps_constants.INFO, "Step Number: {}".format(definition[Constants.EXEC_SQL_STEP_NUMBER]), step_param)
            write_logs(steps_constants.INFO, "Step name inside Execute SQL: {}".format(definition[Constants.EXEC_SQL_STEP_NAME]),
                       step_param)

            step_param.job_dict[steps_constants.BATCH_ID] = "{}{}{}"\
                .format(step_param.batch_id, step_param.step_number, step_param.step_name)
            step_param.job_dict[steps_constants.STEP_NUMBER] = definition[Constants.EXEC_SQL_STEP_NUMBER]
            step_param.job_dict[steps_constants.STEP_NAME] = definition[Constants.EXEC_SQL_STEP_NAME]
            step_param.job_dict[steps_constants.START_TIME] = str(datetime.datetime.now())
            step_param.job_dict[steps_constants.STATUS] = steps_constants.STATUS_RUNNING

            step_param.dynamoDb.Table(job_step_status_table).put_item(Item=step_param.job_dict)

            db_name = definition[Constants.EXEC_SQL_DB_NAME]

            if db_name != "":
                step_param.spark.sql(f"use `{db_name}`")

            temp_view = definition[Constants.EXEC_SQL_TEMP_VIEW]
            statement = definition[Constants.EXEC_SQL_STATEMENT]
            persist_flag = definition[Constants.EXEC_SQL_PERSIST]
            persist_type = definition[Constants.EXEC_SQL_PERSIST_TYPE]
            action = definition[Constants.EXEC_SQL_ACTION]

            write_logs(steps_constants.INFO, "Executing Query -{} ".format(statement), step_param)
            # try:
            df = spark_session.sql(statement)
            # except:
            #     step_param.job_dict["end_time"] = str(datetime.datetime.now())
            #     step_param.job_dict["status"] = 'Failed'
            #     step_param.job_dict["error_description"] = 'Query Failed - {}'.format(statement)
            #     step_param.dynamoDb.Table(job_step_status_table).put_item(Item=step_param.job_dict)

            df.createOrReplaceTempView(temp_view)
            # definition["df"] = spark_session.sql(statement)
            # Use Ignore Case, check the alternative in Code shared by Rajat
            if persist_flag:
                write_logs(steps_constants.INFO, "Persisting DF with persist type {}".format(persist_type), step_param)
                # Make a separate file for storage
                level = StorageLevel.getStorageLevel(self, persist_type)
                df.persist(level)
            # Add else
            if action != "":
                write_logs(steps_constants.INFO, "Executing Action : {}".format(action), step_param)
                Actions.getAction(self, action, df)

            step_param.job_dict[steps_constants.END_TIME] = str(datetime.datetime.now())
            step_param.job_dict[steps_constants.STATUS] = steps_constants.STATUS_COMPLETED

            step_param.dynamoDb.Table(job_step_status_table).put_item(Item=step_param.job_dict)

        return df
